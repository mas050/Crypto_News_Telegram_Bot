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
from typing import List, Dict, Any, Set
import os
import json
import hashlib
import google.generativeai as genai
from dotenv import load_dotenv

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
    
    def _generate_news_hash(self, item: Dict[str, Any]) -> str:
        """Generate a unique hash for a news item based on title and link"""
        # Use title + link to create a unique identifier
        unique_string = f"{item.get('title', '')}|{item.get('link', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
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
        """Check if a news item has already been analyzed"""
        news_hash = self._generate_news_hash(item)
        return news_hash in self.sent_news_hashes
    
    def _mark_as_analyzed(self, item: Dict[str, Any]) -> None:
        """Mark a news item as analyzed (whether opportunity or not)"""
        news_hash = self._generate_news_hash(item)
        self.sent_news_hashes[news_hash] = time.time()
        
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
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
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
        
        analyzed_items = []
        
        print("\n🤖 Analyzing content with Google Gemini 2.5 Flash...")
        
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
                # Format message
                analysis = opp.get('ai_analysis', {})
                message = f"""
🚀 *Crypto Opportunity Detected*

*Source:* {opp['source']}
*Title:* {opp['title']}

*Type:* {analysis.get('opportunity_type', 'N/A')}
*Risk Level:* {analysis.get('risk_level', 'N/A')}

*Analysis:*
{analysis.get('explanation', 'No analysis available')}

*Link:* {opp.get('link', 'N/A')}

_Analyzed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
"""
                
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
            
            # Step 6: Send to Telegram
            self.send_to_telegram(opportunities)
            
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