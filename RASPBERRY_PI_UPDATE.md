# 🔄 Raspberry Pi Update Guide

This guide will help you pull the latest changes from GitHub to your Raspberry Pi and update the channel configuration.

## Step 1: Connect to Your Raspberry Pi

```bash
ssh pi@your-raspberry-pi-ip
# Or if you're using a different username:
# ssh your-username@your-raspberry-pi-ip
```

## Step 2: Navigate to the Bot Directory

```bash
cd ~/Crypto_News_Telegram_Bot
# Or wherever you installed the bot
```

## Step 3: Stop the Running Bot (if it's running)

```bash
# Check if bot is running
ps aux | grep Crypto_News_Analyzer.py

# Stop the systemd service (if using service)
sudo systemctl stop crypto-news-bot

# OR stop manually if running in background
pkill -f "python.*Crypto_News_Analyzer.py"
```

## Step 4: Pull Latest Changes from GitHub

```bash
# Make sure you're on the main branch
git branch

# Pull the latest changes
git pull origin main
```

## Step 5: Update the .env File with Your Channel ID

```bash
# Edit the .env file
nano .env

# Update the TELEGRAM_CHAT_ID line to:
# TELEGRAM_CHAT_ID=-1003448714142

# Save and exit (Ctrl+X, then Y, then Enter)
```

Or use this one-liner to update it automatically:

```bash
sed -i 's/^TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=-1003448714142/' .env
```

## Step 6: Test the Connection

```bash
# Run the test script
python test_telegram_channel.py
```

You should see:
```
✅ SUCCESS! Test message sent to your Telegram channel!
```

Check your Telegram channel to confirm you received the test message.

## Step 7: Restart the Bot

### Option A: Using systemd service (recommended)

```bash
# Start the service
sudo systemctl start crypto-news-bot

# Check status
sudo systemctl status crypto-news-bot

# View logs
sudo journalctl -u crypto-news-bot -f
```

### Option B: Run manually in background

```bash
# Start the bot in background
nohup python Crypto_News_Analyzer.py > output.log 2>&1 &

# Check if it's running
ps aux | grep Crypto_News_Analyzer.py

# View logs
tail -f crypto_news_bot.log
```

## Step 8: Verify It's Working

```bash
# Check the logs for activity
tail -f crypto_news_bot.log

# You should see messages like:
# "Starting Crypto News Analysis Workflow"
# "Fetching RSS feed from..."
# "Sending X opportunities to Telegram..."
```

## Quick Update Script

Save this as `update_bot.sh` on your Raspberry Pi for easy updates:

```bash
#!/bin/bash

echo "🔄 Updating Crypto News Bot..."

# Stop the bot
echo "⏸️  Stopping bot..."
sudo systemctl stop crypto-news-bot 2>/dev/null || pkill -f "python.*Crypto_News_Analyzer.py"

# Pull latest changes
echo "📥 Pulling from GitHub..."
git pull origin main

# Update channel ID if needed
echo "🔧 Updating channel ID..."
sed -i 's/^TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=-1003448714142/' .env

# Test connection
echo "🧪 Testing connection..."
python test_telegram_channel.py

# Restart bot
echo "▶️  Starting bot..."
sudo systemctl start crypto-news-bot

echo "✅ Update complete!"
echo "📊 Check status with: sudo systemctl status crypto-news-bot"
```

Make it executable:
```bash
chmod +x update_bot.sh
```

Then run it anytime you need to update:
```bash
./update_bot.sh
```

## Troubleshooting

### "Permission denied" when pulling from GitHub

```bash
# Make sure you have the right permissions
ls -la .git/

# If needed, fix ownership
sudo chown -R $USER:$USER .
```

### Bot not sending to channel

1. **Verify bot is admin in the channel**
   - Go to your Telegram channel
   - Click on channel name → Administrators
   - Make sure your bot is listed as an admin

2. **Check channel ID is correct**
   ```bash
   grep TELEGRAM_CHAT_ID .env
   # Should show: TELEGRAM_CHAT_ID=-1003448714142
   ```

3. **Test with the test script**
   ```bash
   python test_telegram_channel.py
   ```

### Bot crashes on Raspberry Pi

Check the logs:
```bash
tail -50 crypto_news_bot.log
```

Common issues:
- **Memory issues**: Selenium can be heavy on Raspberry Pi
- **Chrome driver issues**: Make sure chromium-chromedriver is installed
- **Network timeouts**: Increase timeout values if your Pi has slow internet

### View real-time logs

```bash
# If using systemd
sudo journalctl -u crypto-news-bot -f

# If running manually
tail -f crypto_news_bot.log
```

## Important Notes

⚠️ **Security Reminders:**
- Never commit your `.env` file to GitHub
- The `.env` file stays only on your local machine and Raspberry Pi
- Each machine needs its own `.env` file with the credentials

✅ **What gets synced via GitHub:**
- Python code changes
- Configuration files (except .env)
- Documentation updates
- New features and bug fixes

❌ **What does NOT get synced:**
- `.env` file (contains secrets)
- `sent_news_history.json` (local tracking)
- Log files

---

**Need help?** Check the main [README.md](README.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
