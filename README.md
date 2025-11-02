# 🚀 Crypto News Analyzer Bot

An automated crypto news analysis bot that fetches news from multiple sources, uses Google Gemini AI to identify trading opportunities, and sends alerts to your Telegram chat.

## 📋 Features

- **Multi-Source News Aggregation**
  - CoinTelegraph RSS feed
  - CoinDesk RSS feed
  - NewsBTC RSS feed
  - CoinGecko trending coins
  - Twitter/X crypto tweets (optional)

- **AI-Powered Analysis**
  - Uses Google Gemini 2.5 Flash for intelligent opportunity detection
  - Identifies opportunity types (price movement, partnerships, tech breakthroughs, etc.)
  - Assesses risk levels (LOW/MEDIUM/HIGH)
  - Provides brief explanations for each opportunity

- **Smart Duplicate Prevention**
  - Tracks sent news in local JSON file
  - Filters duplicates BEFORE AI analysis (saves API costs!)
  - Auto-cleanup of old entries (7-day retention)

- **Automated Delivery**
  - Sends opportunities directly to your Telegram chat
  - Runs on a schedule (default: every hour)
  - Beautiful formatted messages with markdown

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone or Download

```bash
cd /path/to/your/projects
# If using git:
git clone <your-repo-url>
cd Crypto_News_Telegram_Bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   nano .env  # or use your preferred text editor
   ```

See [SETUP.md](SETUP.md) for detailed instructions on obtaining API keys.

## 🔑 Required API Keys

| Service | Required | Get It From |
|---------|----------|-------------|
| Google Gemini API | ✅ Yes | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| Telegram Bot Token | ✅ Yes | [@BotFather](https://t.me/BotFather) on Telegram |
| Telegram Chat ID | ✅ Yes | [@userinfobot](https://t.me/userinfobot) on Telegram |
| Twitter Bearer Token | ⚪ Optional | [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) |

## 🚀 Usage

### Run Once

```bash
python Crypto_News_Analyzer.py
```

The script will:
1. Fetch news from all sources
2. Filter out duplicates
3. Analyze new items with Gemini AI
4. Send opportunities to your Telegram chat
5. Schedule to run every hour

### Run in Background

```bash
nohup python Crypto_News_Analyzer.py > output.log 2>&1 &
```

### Stop the Bot

```bash
# Find the process
ps aux | grep Crypto_News_Analyzer.py

# Kill it
kill <process_id>

# Or use pkill
pkill -f "python.*Crypto_News_Analyzer.py"
```

## 📊 How It Works

```
┌─────────────────┐
│  Fetch News     │  CoinTelegraph, CoinDesk, NewsBTC, CoinGecko, Twitter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Merge Sources  │  Combine all news into single list
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Filter Duplicates│  Check against sent_news_history.json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Analysis    │  Gemini 2.5 Flash analyzes in batches of 5
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Filter Opportunities│ Keep only significant opportunities
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send to Telegram│  Formatted messages with analysis
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save History   │  Update sent_news_history.json
└─────────────────┘
```

## 📁 Project Structure

```
Crypto_News_Telegram_Bot/
├── Crypto_News_Analyzer.py    # Main bot script
├── requirements.txt            # Python dependencies
├── .env                        # Your API keys (DO NOT COMMIT!)
├── .env.example               # Template for .env
├── .gitignore                 # Git ignore rules
├── sent_news_history.json     # Duplicate tracking (auto-generated)
├── README.md                  # This file
├── SETUP.md                   # Detailed setup guide
└── DUPLICATE_TRACKING.md      # Duplicate prevention docs
```

## ⚙️ Configuration

### Change Schedule Interval

Edit the `main()` function in `Crypto_News_Analyzer.py`:

```python
# Run every 30 minutes
schedule.every(30).minutes.do(analyzer.run_workflow)

# Run every 2 hours
schedule.every(2).hours.do(analyzer.run_workflow)

# Run every day at 9 AM
schedule.every().day.at("09:00").do(analyzer.run_workflow)
```

### Adjust Batch Size for AI Analysis

Edit line 227 in `Crypto_News_Analyzer.py`:

```python
batch_size = 5  # Change to 3, 10, etc.
```

### Change Duplicate Retention Period

Edit the `_load_history()` method (line 67):

```python
# Current: 7 days
if current_time - timestamp < 7 * 24 * 60 * 60

# Change to 3 days:
if current_time - timestamp < 3 * 24 * 60 * 60
```

### Add More RSS Feeds

Edit the `__init__()` method (line 37):

```python
self.rss_feeds = {
    'CoinTelegraph': 'https://cointelegraph.com/rss',
    'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'NewsBTC': 'https://www.newsbtc.com/feed/',
    'YourSource': 'https://yoursource.com/rss'  # Add here
}
```

## 🔒 Security Best Practices

- ✅ Never commit `.env` file to version control
- ✅ Never share your API keys publicly
- ✅ Keep `.env.example` as a template (without real keys)
- ✅ The `.gitignore` file already protects `.env` and `sent_news_history.json`

## 🐛 Troubleshooting

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "Gemini API key not set"
- Verify `.env` file exists in the same directory as the script
- Check that `GEMINI_API_KEY` is set in `.env`
- Ensure no extra spaces around the `=` sign

### "Fetched 0 articles from CoinDesk"
This is now fixed! The script handles CoinDesk's redirect properly.

### No opportunities found
This is normal! The AI is selective and only identifies significant opportunities. Not every news item is an opportunity.

### Too many duplicates
- Check if `sent_news_history.json` is being saved properly
- Verify file permissions
- Try deleting `sent_news_history.json` to reset

## 📈 Performance & Costs

### API Usage

- **Gemini API**: ~4-7 calls per run (depending on news volume)
  - Free tier: 15 requests/minute, 1,500 requests/day
  - More than enough for hourly runs!

- **CoinGecko API**: 1 call per run
  - Free tier: 10-30 calls/minute
  - No issues

- **Twitter API**: 1 call per run (if enabled)
  - Free tier: Limited, may require paid plan

### Optimization Features

- ✅ Duplicate filtering BEFORE AI analysis (saves 40-50% API costs)
- ✅ Batch processing (5 items per API call)
- ✅ Summary truncation (500 chars max)
- ✅ Rate limiting (2-second delay between batches)

## 📝 Example Output

```
============================================================
🔄 Starting Crypto News Analysis Workflow
⏰ 2025-11-02 16:00:00
============================================================

Fetching RSS feed from CoinTelegraph...
✓ Fetched 10 articles from CoinTelegraph
Fetching RSS feed from CoinDesk...
✓ Fetched 10 articles from CoinDesk
Fetching RSS feed from NewsBTC...
✓ Fetched 10 articles from NewsBTC
Fetching CoinGecko trending data...
✓ Fetched 5 trending coins

📊 Total items collected: 35

🔍 Filtered out 18 duplicate(s), 17 new items to analyze

🤖 Analyzing content with Google Gemini 2.5 Flash...

🎯 Found 8 opportunities out of 17 items

📱 Sending 8 opportunities to Telegram...
✓ Sent: Bitcoin hits new all-time high...
✓ Sent: Major exchange lists new altcoin...

============================================================
✅ Workflow completed successfully!
============================================================
```

## 🤝 Contributing

Feel free to fork, modify, and improve this bot! Some ideas:

- Add more news sources
- Improve AI prompts for better opportunity detection
- Add sentiment analysis
- Create a web dashboard
- Add price alerts integration

## 📄 License

This project is open source. Use it however you like!

## 🙏 Acknowledgments

- Google Gemini for AI analysis
- Telegram for bot API
- CoinTelegraph, CoinDesk, NewsBTC for news feeds
- CoinGecko for market data

## 📞 Support

For detailed setup instructions, see [SETUP.md](SETUP.md)

For duplicate tracking info, see [DUPLICATE_TRACKING.md](DUPLICATE_TRACKING.md)

---

**Happy Trading! 🚀📈**
