# 🔧 Troubleshooting Guide - Bot Crashes Daily

This guide addresses the common issues causing the crypto news analyzer to crash daily on Raspberry Pi.

## 🚨 Critical Issues Fixed

### 1. **Selenium Memory Leak** ✅ FIXED
**Problem**: Selenium Chrome processes weren't properly closed, causing memory exhaustion.

**Solution Applied**:
- Added `finally` block to always close WebDriver
- Added `--single-process` flag for Raspberry Pi
- Set page load timeout to prevent hanging
- Proper exception handling for TimeoutException

### 2. **Unhandled Exceptions in Main Loop** ✅ FIXED
**Problem**: Any exception in `schedule.run_pending()` would crash the entire bot.

**Solution Applied**:
- Wrapped main loop in try-except
- Added consecutive error tracking
- Bot will only exit after 10 consecutive errors
- Each error is logged with full traceback

### 3. **Missing Logging** ✅ FIXED
**Problem**: No persistent logs made debugging impossible.

**Solution Applied**:
- Added comprehensive logging to `crypto_news_bot.log`
- All errors logged with full stack traces
- Both file and console output

### 4. **Network Failures** ✅ FIXED
**Problem**: Network timeouts caused crashes without retry.

**Solution Applied**:
- Added `@retry_on_failure` decorator to critical functions
- Exponential backoff (5s, 10s, 20s)
- 3 retry attempts before failing

### 5. **Resource Limits** ✅ FIXED
**Problem**: No memory/CPU limits on Raspberry Pi.

**Solution Applied**:
- Added systemd resource limits (512MB max memory)
- CPU quota set to 80%
- Automatic restart on crash

## 📊 How to Monitor the Bot

### Check if Bot is Running
```bash
sudo systemctl status crypto-news-bot.service
```

### View Live Logs
```bash
# Main log (all activity)
tail -f ~/Python/Crypto_News_Telegram_Bot/crypto_news_bot.log

# Error log (systemd errors)
tail -f ~/Python/Crypto_News_Telegram_Bot/bot_error.log

# System journal
sudo journalctl -u crypto-news-bot.service -f
```

### Check Memory Usage
```bash
# Overall system memory
free -h

# Bot process memory
ps aux | grep Crypto_News_Analyzer
```

### Check for Zombie Chrome Processes
```bash
# Find orphaned Chrome processes
ps aux | grep chrome

# Kill them if found
pkill -f chrome
```

## 🔄 Updating the Service

After pulling the latest code with fixes:

```bash
# Navigate to project
cd ~/Python/Crypto_News_Telegram_Bot

# Stop the bot
sudo systemctl stop crypto-news-bot.service

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Copy new service file
sudo cp crypto-news-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Start the bot
sudo systemctl start crypto-news-bot.service

# Verify it's running
sudo systemctl status crypto-news-bot.service
```

## 🐛 Common Issues & Solutions

### Issue: Bot Still Crashes Daily

**Check the logs first:**
```bash
tail -100 ~/Python/Crypto_News_Telegram_Bot/crypto_news_bot.log
```

**Look for:**
- `MemoryError` - Reduce batch_size in code
- `TimeoutException` - Network issues
- `WebDriverException` - Chrome/Selenium issues
- `API rate limit` - Gemini API quota exceeded

### Issue: Out of Memory

**Solution 1: Reduce batch size**
Edit `Crypto_News_Analyzer.py` line ~487:
```python
batch_size = 3  # Reduced from 5
```

**Solution 2: Disable Selenium scraping**
Edit `Crypto_News_Analyzer.py` around line 612:
```python
# Comment out Selenium scraping
# if not image_url:
#     image_url = self._fetch_image_with_selenium(article_url)
```

**Solution 3: Increase swap space**
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue: Gemini API Rate Limit

**Check logs for:**
```
Error analyzing batch: 429 Too Many Requests
```

**Solution:**
- Increase delay between batches (line ~563)
- Reduce number of items analyzed
- Check Gemini API quota in Google Cloud Console

### Issue: Chrome/Selenium Not Working

**Install/reinstall Chrome and ChromeDriver:**
```bash
# Install Chromium
sudo apt install chromium-browser chromium-chromedriver -y

# Verify installation
chromium-browser --version
chromedriver --version
```

### Issue: Bot Stops During Quiet Hours

The bot is configured to skip runs between 10 PM - 7 AM.

**To disable quiet hours**, edit `Crypto_News_Analyzer.py` around line 748:
```python
# Comment out quiet hours check
# if current_hour >= 22 or current_hour < 7:
#     logger.info("Quiet hours are active (10 PM - 7 AM). Skipping run.")
#     return
```

## 📈 Performance Optimization

### For Low-End Raspberry Pi (Pi 3 or older)

1. **Reduce RSS feeds** (edit `__init__` method):
```python
self.rss_feeds = {
    'CoinTelegraph': 'https://cointelegraph.com/rss',
    'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
    # Comment out others
}
```

2. **Disable CoinGecko and Twitter**:
```python
# In run_workflow(), comment out:
# coingecko_data = self.fetch_coingecko_data()
# twitter_data = self.search_twitter("crypto OR bitcoin OR ethereum")
coingecko_data = []
twitter_data = []
```

3. **Increase run interval** (edit main function):
```python
# Run every 2 hours instead of 1
schedule.every(2).hours.do(analyzer.run_workflow)
```

## 🔍 Debugging Steps

1. **Check service status:**
```bash
sudo systemctl status crypto-news-bot.service
```

2. **View recent errors:**
```bash
sudo journalctl -u crypto-news-bot.service -n 100 --no-pager
```

3. **Check disk space:**
```bash
df -h
```

4. **Check log file size:**
```bash
ls -lh ~/Python/Crypto_News_Telegram_Bot/*.log
```

5. **Rotate logs if too large:**
```bash
cd ~/Python/Crypto_News_Telegram_Bot
mv crypto_news_bot.log crypto_news_bot.log.old
mv bot.log bot.log.old
mv bot_error.log bot_error.log.old
sudo systemctl restart crypto-news-bot.service
```

## 🆘 Emergency Recovery

If the bot is completely broken:

```bash
# Stop the service
sudo systemctl stop crypto-news-bot.service

# Check for zombie processes
ps aux | grep -E 'python|chrome'

# Kill any stuck processes
pkill -f Crypto_News_Analyzer
pkill -f chrome

# Clear logs
cd ~/Python/Crypto_News_Telegram_Bot
> crypto_news_bot.log
> bot.log
> bot_error.log

# Restart
sudo systemctl start crypto-news-bot.service

# Monitor
tail -f crypto_news_bot.log
```

## 📞 Getting Help

When reporting issues, include:

1. **Service status:**
```bash
sudo systemctl status crypto-news-bot.service
```

2. **Last 50 log lines:**
```bash
tail -50 ~/Python/Crypto_News_Telegram_Bot/crypto_news_bot.log
```

3. **System info:**
```bash
free -h
df -h
cat /proc/cpuinfo | grep Model
```

4. **Python/package versions:**
```bash
source ~/Python/Crypto_News_Telegram_Bot/venv/bin/activate
python --version
pip list
```

---

**The bot should now be much more stable and resilient to crashes! 🎉**
