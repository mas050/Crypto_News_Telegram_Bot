"""
Crypto News Analyzer - n8n Workflow to Python Conversion
Fetches crypto news from multiple sources, analyzes with Google Gemini 2.5 Flash,
and sends opportunities to Telegram.
"""

import feedparser
import requests
import time
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set, Optional
import os
import json
import hashlib
import random
import google.generativeai as genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()


class CryptoNewsAnalyzer:
    def __init__(self):
        # API Keys - Set these as environment variables
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')  # Optional
        
        # Configure Gemini
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # RSS Feed URLs
        self.rss_feeds = {
            'CoinTelegraph': 'https://cointelegraph.com/rss',
            'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'NewsBTC': 'https://www.newsbtc.com/feed/',
            'CryptoSlate': 'https://cryptoslate.com/feed/',
            'Bitcoin Magazine': 'https://bitcoinmagazine.com/.rss/full/',
            'The Block': 'https://www.theblock.co/rss.xml'
        }
        
        # CoinGecko API
        self.coingecko_api = 'https://api.coingecko.com/api/v3'
        
        # History tracking file
        self.history_file = 'sent_news_history.json'
        self.sent_news_hashes = self._load_history()
        
        # Load prompt variations
        self.prompts = self._load_prompts()
        self.current_prompt_style = None  # Will be set during analysis
        
        # Load message templates
        self.message_templates = self._load_message_templates()
    
    def _load_prompts(self) -> Dict[str, Dict[str, str]]:
        """Load prompt variations from prompts.json"""
        try:
            with open('prompts.json', 'r') as f:
                prompts = json.load(f)
                print(f"📝 Loaded {len(prompts)} prompt variations")
                return prompts
        except FileNotFoundError:
            print("⚠ prompts.json not found, using default prompt")
            return {
                "original": {
                    "prompt": "Analyze the following crypto news items and identify potential trading or investment opportunities.\n\nFor each item, determine:\n1. Is this a significant opportunity? (YES/NO)\n2. What type of opportunity? (price movement, new listing, partnership, technology breakthrough, market trend, etc.)\n3. Risk level (LOW/MEDIUM/HIGH)\n4. Brief explanation (max 2 sentences)\n\nContent to analyze:\n{content_summary}\n\nRespond in JSON format for each item:\n{{\n    \"item_1\": {{\n        \"is_opportunity\": true/false,\n        \"opportunity_type\": \"type\",\n        \"risk_level\": \"LOW/MEDIUM/HIGH\",\n        \"explanation\": \"brief explanation\"\n    }},\n    ...\n}}",
                    "emoji": "🔍"
                }
            }
        except Exception as e:
            print(f"⚠ Error loading prompts: {str(e)}")
            return {}
    
    def _load_message_templates(self) -> Dict[str, Dict[str, str]]:
        """Load message templates from message_templates.json"""
        try:
            with open('message_templates.json', 'r') as f:
                templates = json.load(f)
                print(f"💬 Loaded {len(templates)} message templates")
                return templates
        except FileNotFoundError:
            print("⚠ message_templates.json not found, using default template")
            return {
                "original": {
                    "template": "{emoji} *Crypto Opportunity Detected*\n\n*Source:* {source}\n*Title:* {title}\n\n*Type:* {opportunity_type}\n*Risk Level:* {risk_level}\n\n*Analysis:*\n{explanation}\n\n*Link:* {link}\n\n_Analyzed at {timestamp}_\n_Style: {style}_"
                }
            }
        except Exception as e:
            print(f"⚠ Error loading message templates: {str(e)}")
            return {}
    
    def _generate_news_hash(self, item: Dict[str, Any]) -> str:
        """Generate a unique hash for a news item based on title and link"""
        # Use title + link to create a unique identifier
        unique_string = f"{item.get('title', '')}|{item.get('link', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _extract_image_from_entry(self, entry) -> Optional[str]:
        """Extract image URL from RSS feed entry"""
        try:
            # Try to get image from media:content or media:thumbnail
            if hasattr(entry, 'media_content') and entry.media_content:
                return entry.media_content[0].get('url')
            
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                return entry.media_thumbnail[0].get('url')
            
            # Try to get image from enclosures
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        return enclosure.get('href')
            
            # Try to extract from summary/description HTML
            if hasattr(entry, 'summary'):
                soup = BeautifulSoup(entry.summary, 'html.parser')
                img = soup.find('img')
                if img and img.get('src'):
                    return img.get('src')
            
            return None
        except Exception as e:
            return None
    
    def _fetch_image_from_article(self, url: str) -> Optional[str]:
        """Fetch image from article page (fallback method)"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; CryptoNewsBot/1.0)'}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image.get('content')
            
            # Try Twitter card image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                return twitter_image.get('content')
            
            # Try first article image
            article = soup.find('article')
            if article:
                img = article.find('img')
                if img and img.get('src'):
                    img_url = img.get('src')
                    # Handle relative URLs
                    if img_url.startswith('//'):
                        return 'https:' + img_url
                    elif img_url.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        return f"{parsed.scheme}://{parsed.netloc}{img_url}"
                    return img_url
            
            return None
        except Exception as e:
            return None
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing query parameters and fragments"""
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # Keep only scheme, netloc, and path (remove query, fragment)
        normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        # Remove trailing slash for consistency
        return normalized.rstrip('/')
    
    def _generate_url_hash(self, item: Dict[str, Any]) -> str:
        """Generate a hash based only on the normalized URL"""
        url = item.get('link', '')
        if not url:
            return None
        normalized_url = self._normalize_url(url)
        return hashlib.md5(normalized_url.encode()).hexdigest()
    
    def _load_history(self) -> Dict[str, float]:
        """Load sent news history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    # Clean up old entries (older than 7 days)
                    current_time = time.time()
                    cleaned_history = {
                        hash_id: timestamp 
                        for hash_id, timestamp in history.items()
                        if current_time - timestamp < 7 * 24 * 60 * 60  # 7 days
                    }
                    print(f"📚 Loaded {len(cleaned_history)} items from history (cleaned {len(history) - len(cleaned_history)} old entries)")
                    return cleaned_history
            except Exception as e:
                print(f"⚠ Error loading history: {str(e)}")
                return {}
        return {}
    
    def _save_history(self) -> None:
        """Save sent news history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.sent_news_hashes, f, indent=2)
        except Exception as e:
            print(f"⚠ Error saving history: {str(e)}")
    
    def _is_duplicate(self, item: Dict[str, Any]) -> bool:
        """Check if a news item has already been analyzed (by title+link OR by URL)"""
        # Check title+link hash
        news_hash = self._generate_news_hash(item)
        if news_hash in self.sent_news_hashes:
            return True
        
        # Also check URL-only hash (catches same story from different sources)
        url_hash = self._generate_url_hash(item)
        if url_hash and url_hash in self.sent_news_hashes:
            return True
        
        return False
    
    def _mark_as_analyzed(self, item: Dict[str, Any]) -> None:
        """Mark a news item as analyzed (whether opportunity or not)"""
        # Store both title+link hash and URL-only hash
        news_hash = self._generate_news_hash(item)
        self.sent_news_hashes[news_hash] = time.time()
        
        # Also store URL hash to catch same story from different sources
        url_hash = self._generate_url_hash(item)
        if url_hash:
            self.sent_news_hashes[url_hash] = time.time()
        
    def fetch_rss_feeds(self) -> List[Dict[str, Any]]:
        """Fetch articles from all RSS feeds"""
        all_articles = []
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                print(f"Fetching RSS feed from {source_name}...")
                
                # For CoinDesk, manually fetch with requests to handle redirects
                if source_name == 'CoinDesk':
                    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CryptoNewsBot/1.0)'}
                    response = requests.get(feed_url, headers=headers, timeout=10, allow_redirects=True)
                    response.raise_for_status()
                    feed = feedparser.parse(response.content)
                else:
                    feed = feedparser.parse(feed_url, agent='Mozilla/5.0 (compatible; CryptoNewsBot/1.0)')
                
                # Debug: Check if feed has errors
                if hasattr(feed, 'bozo') and feed.bozo:
                    print(f"⚠ Feed parsing warning for {source_name}: {feed.get('bozo_exception', 'Unknown error')}")
                
                # Debug: Check total entries available
                if len(feed.entries) == 0:
                    print(f"⚠ No entries found in {source_name} feed. Status: {feed.get('status', 'N/A')}")
                
                for entry in feed.entries[:10]:  # Limit to 10 most recent
                    article = {
                        'source': source_name,
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.get('summary', ''),
                        'image_url': self._extract_image_from_entry(entry),
                        'published': entry.get('published', ''),
                        'type': 'rss'
                    }
                    all_articles.append(article)
                
                print(f"✓ Fetched {len(feed.entries[:10])} articles from {source_name}")
            except Exception as e:
                print(f"✗ Error fetching {source_name}: {str(e)}")
        
        return all_articles
    
    def fetch_coingecko_data(self) -> List[Dict[str, Any]]:
        """Fetch trending coins and market data from CoinGecko"""
        try:
            print("Fetching CoinGecko trending data...")
            
            # Get trending coins
            trending_url = f"{self.coingecko_api}/search/trending"
            response = requests.get(trending_url, timeout=10)
            response.raise_for_status()
            trending_data = response.json()
            
            trending_items = []
            for coin in trending_data.get('coins', [])[:5]:  # Top 5 trending
                item = coin.get('item', {})
                trending_items.append({
                    'source': 'CoinGecko',
                    'title': f"Trending: {item.get('name')} ({item.get('symbol')})",
                    'summary': f"Market Cap Rank: #{item.get('market_cap_rank', 'N/A')} | Score: {item.get('score', 0)}",
                    'link': f"https://www.coingecko.com/en/coins/{item.get('id')}",
                    'type': 'coingecko'
                })
            
            print(f"✓ Fetched {len(trending_items)} trending coins")
            return trending_items
            
        except Exception as e:
            print(f"✗ Error fetching CoinGecko data: {str(e)}")
            return []
    
    def search_twitter(self, query: str = "crypto") -> List[Dict[str, Any]]:
        """Search Twitter/X for crypto-related tweets"""
        # Note: Twitter API v2 requires authentication
        # This is a placeholder - you'll need to implement proper Twitter API integration
        
        if not self.twitter_bearer_token:
            print("⚠ Twitter Bearer Token not set, skipping Twitter search")
            return []
        
        try:
            print(f"Searching Twitter for: {query}...")
            
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
            params = {
                "query": f"{query} -is:retweet lang:en",
                "max_results": 10,
                "tweet.fields": "created_at,public_metrics"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            tweets = []
            for tweet in data.get('data', []):
                tweets.append({
                    'source': 'Twitter/X',
                    'title': f"Tweet: {tweet['text'][:100]}...",
                    'summary': tweet['text'],
                    'link': f"https://twitter.com/i/web/status/{tweet['id']}",
                    'type': 'twitter'
                })
            
            print(f"✓ Fetched {len(tweets)} tweets")
            return tweets
            
        except Exception as e:
            print(f"✗ Error searching Twitter: {str(e)}")
            return []
    
    def merge_sources(self, *sources) -> List[Dict[str, Any]]:
        """Merge all data sources into a single list"""
        merged = []
        for source in sources:
            if isinstance(source, list):
                merged.extend(source)
        
        print(f"\n📊 Total items collected: {len(merged)}")
        return merged
    
    def analyze_with_gemini(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze items using Google Gemini 2.5 Flash to identify opportunities"""
        if not self.gemini_api_key:
            print("⚠ Gemini API key not set, skipping AI analysis")
            return []
        
        # Select a random prompt style for this run
        if self.prompts:
            prompt_key = random.choice(list(self.prompts.keys()))
            prompt_data = self.prompts[prompt_key]
            prompt_template = prompt_data['prompt']
            prompt_emoji = prompt_data['emoji']
            self.current_prompt_style = prompt_key
            print(f"\n🤖 Analyzing with '{prompt_key}' style {prompt_emoji}...")
        else:
            print("\n🤖 Analyzing content with Google Gemini 2.5 Flash...")
            prompt_template = None
        
        analyzed_items = []
        
        # Batch items for analysis (process in groups)
        batch_size = 5
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            
            # Prepare content for analysis
            content_summary = "\n\n".join([
                f"Source {idx+1} ({item['source']}):\n"
                f"Title: {item['title']}\n"
                f"Summary: {item.get('summary', '')[:500]}"
                for idx, item in enumerate(batch)
            ])
            
            # Use selected prompt template or default
            if prompt_template:
                prompt = prompt_template.format(content_summary=content_summary)
            else:
                # Fallback to original prompt
                prompt = f"""Analyze the following crypto news items and identify potential trading or investment opportunities.

For each item, determine:
1. Is this a significant opportunity? (YES/NO)
2. What type of opportunity? (price movement, new listing, partnership, technology breakthrough, market trend, etc.)
3. Risk level (LOW/MEDIUM/HIGH)
4. Brief explanation (max 2 sentences)

Content to analyze:
{content_summary}

Respond in JSON format for each item:
{{
    "item_1": {{
        "is_opportunity": true/false,
        "opportunity_type": "type",
        "risk_level": "LOW/MEDIUM/HIGH",
        "explanation": "brief explanation"
    }},
    ...
}}"""
            
            try:
                response = self.model.generate_content(prompt)
                
                # Parse the response
                response_text = response.text.strip()
                
                # Try to extract JSON from the response
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                try:
                    analysis = json.loads(response_text)
                    
                    # Match analysis results with items
                    for idx, item in enumerate(batch):
                        item_key = f"item_{idx+1}"
                        if item_key in analysis:
                            item_analysis = analysis[item_key]
                            item['ai_analysis'] = item_analysis
                            item['is_opportunity'] = item_analysis.get('is_opportunity', False)
                            analyzed_items.append(item)
                        else:
                            item['ai_analysis'] = None
                            item['is_opportunity'] = False
                            analyzed_items.append(item)
                    
                except json.JSONDecodeError:
                    print(f"⚠ Could not parse JSON response for batch {i//batch_size + 1}")
                    # Add items without analysis
                    for item in batch:
                        item['ai_analysis'] = {'explanation': response_text[:200]}
                        item['is_opportunity'] = False
                        analyzed_items.append(item)
                
                # Rate limiting - be nice to the API
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ Error analyzing batch {i//batch_size + 1}: {str(e)}")
                # Add items without analysis
                for item in batch:
                    item['ai_analysis'] = None
                    item['is_opportunity'] = False
                    analyzed_items.append(item)
        
        return analyzed_items
    
    def filter_opportunities(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter items to only include identified opportunities"""
        opportunities = [item for item in items if item.get('is_opportunity', False)]
        
        print(f"\n🎯 Found {len(opportunities)} opportunities out of {len(items)} items")
        return opportunities
    
    def filter_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out previously analyzed items (opportunities AND non-opportunities)"""
        new_items = []
        duplicate_count = 0
        
        for item in items:
            if not self._is_duplicate(item):
                new_items.append(item)
            else:
                duplicate_count += 1
        
        print(f"🔍 Filtered out {duplicate_count} already-analyzed item(s), {len(new_items)} new items to analyze")
        return new_items
    
    def send_to_telegram(self, opportunities: List[Dict[str, Any]]) -> None:
        """Send opportunities to Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("⚠ Telegram credentials not set, skipping notification")
            print("\n📋 Opportunities found:")
            for idx, opp in enumerate(opportunities, 1):
                print(f"\n{idx}. {opp['title']}")
                print(f"   Source: {opp['source']}")
                if opp.get('ai_analysis'):
                    print(f"   Analysis: {opp['ai_analysis'].get('explanation', 'N/A')}")
                    print(f"   Risk: {opp['ai_analysis'].get('risk_level', 'N/A')}")
            return
        
        if not opportunities:
            print("ℹ No opportunities to send")
            return
        
        print(f"\n📱 Sending {len(opportunities)} opportunities to Telegram...")
        
        telegram_api = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        
        for opp in opportunities:
            try:
                # Format message using template
                analysis = opp.get('ai_analysis', {})
                
                # Get prompt emoji and template
                style = self.current_prompt_style or 'original'
                prompt_emoji = '🚀'
                template = None
                
                if self.prompts and style in self.prompts:
                    prompt_emoji = self.prompts[style].get('emoji', '🚀')
                
                if self.message_templates and style in self.message_templates:
                    template = self.message_templates[style].get('template')
                
                # Format message with template or use default
                if template:
                    message = template.format(
                        emoji=prompt_emoji,
                        source=opp['source'],
                        title=opp['title'],
                        opportunity_type=analysis.get('opportunity_type', 'N/A'),
                        risk_level=analysis.get('risk_level', 'N/A'),
                        explanation=analysis.get('explanation', 'No analysis available'),
                        link=opp.get('link', 'N/A'),
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        style=style
                    )
                else:
                    # Fallback to default format
                    message = f"""
{prompt_emoji} *Crypto Opportunity Detected*

*Source:* {opp['source']}
*Title:* {opp['title']}

*Type:* {analysis.get('opportunity_type', 'N/A')}
*Risk Level:* {analysis.get('risk_level', 'N/A')}

*Analysis:*
{analysis.get('explanation', 'No analysis available')}

*Link:* {opp.get('link', 'N/A')}

_Analyzed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
_Style: {style}_
"""
                
                # Try to get image URL
                image_url = opp.get('image_url')
                
                # If no image in RSS, try fetching from article (only for non-CoinGecko sources)
                if not image_url and opp['source'] not in ['CoinGecko']:
                    image_url = self._fetch_image_from_article(opp.get('link', ''))
                
                # Send with image if available, otherwise text only
                if image_url:
                    # Send as photo with caption
                    photo_api = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
                    payload = {
                        'chat_id': self.telegram_chat_id,
                        'photo': image_url,
                        'caption': message,
                        'parse_mode': 'Markdown'
                    }
                    response = requests.post(photo_api, json=payload, timeout=10)
                else:
                    # Send as text message
                    payload = {
                        'chat_id': self.telegram_chat_id,
                        'text': message,
                        'parse_mode': 'Markdown',
                        'disable_web_page_preview': True
                    }
                    response = requests.post(telegram_api, json=payload, timeout=10)
                
                response.raise_for_status()
                
                print(f"✓ Sent: {opp['title'][:50]}...")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"✗ Error sending to Telegram: {str(e)}")
    
    def run_workflow(self) -> None:
        """Execute the complete workflow"""
        print(f"\n{'='*60}")
        print(f"🔄 Starting Crypto News Analysis Workflow")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Fetch all sources
            rss_articles = self.fetch_rss_feeds()
            coingecko_data = self.fetch_coingecko_data()
            twitter_data = self.search_twitter("crypto OR bitcoin OR ethereum")
            
            # Step 2: Merge sources
            all_items = self.merge_sources(rss_articles, coingecko_data, twitter_data)
            
            if not all_items:
                print("\n⚠ No items collected. Exiting workflow.")
                return
            
            # Step 3: Filter out duplicates BEFORE AI analysis (saves API calls!)
            new_items = self.filter_duplicates(all_items)
            
            if not new_items:
                print("\n⚠ No new items to analyze. All items were duplicates.")
                return
            
            # Step 4: AI Analysis (only on new items)
            analyzed_items = self.analyze_with_gemini(new_items)
            
            # Mark ALL analyzed items (opportunities and non-opportunities)
            for item in analyzed_items:
                self._mark_as_analyzed(item)
            
            # Step 5: Filter opportunities
            opportunities = self.filter_opportunities(analyzed_items)
            
            # Step 6: Randomly select 1-3 opportunities to send
            if opportunities:
                max_posts = random.randint(1, 3)
                selected_opportunities = random.sample(opportunities, min(max_posts, len(opportunities)))
                print(f"🎲 Randomly selected {len(selected_opportunities)} out of {len(opportunities)} opportunities to post")
            else:
                selected_opportunities = []
            
            # Step 7: Send to Telegram
            self.send_to_telegram(selected_opportunities)
            
            # Step 7: Save history
            self._save_history()
            
            print(f"\n{'='*60}")
            print(f"✅ Workflow completed successfully!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n❌ Workflow error: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the analyzer"""
    analyzer = CryptoNewsAnalyzer()
    
    # Run immediately
    analyzer.run_workflow()
    
    # Schedule to run every hour (adjust as needed)
    schedule.every(1).hours.do(analyzer.run_workflow)
    
    print("\n⏰ Scheduler started. Running every 1 hour.")
    print("Press Ctrl+C to stop.\n")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()