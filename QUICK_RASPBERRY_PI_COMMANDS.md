# 🚀 Quick Raspberry Pi Commands

Copy and paste these commands on your Raspberry Pi to update the bot.

## 🔄 Quick Update (One Command)

```bash
cd ~/Python/Crypto_News_Telegram_Bot && ./update-bot.sh
```

## 📋 Step-by-Step Manual Update

### 1. Connect to Raspberry Pi
```bash
ssh pi@your-raspberry-pi-ip
```

### 2. Navigate to bot directory
```bash
cd ~/Python/Crypto_News_Telegram_Bot
```

### 3. Pull latest changes
```bash
git pull origin main
```

### 4. Update channel ID
```bash
sed -i 's/^TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=-1003448714142/' .env
```

### 5. Test connection
```bash
python test_telegram_channel.py
```

### 6. Restart bot
```bash
sudo systemctl restart crypto-news-bot
```

### 7. Check status
```bash
sudo systemctl status crypto-news-bot
```

## 📊 Monitoring Commands

### View live logs
```bash
tail -f ~/Python/Crypto_News_Telegram_Bot/crypto_news_bot.log
```

### View systemd logs
```bash
sudo journalctl -u crypto-news-bot -f
```

### Check if bot is running
```bash
sudo systemctl status crypto-news-bot
```

### Check bot process
```bash
ps aux | grep Crypto_News_Analyzer.py
```

## 🛠️ Control Commands

### Start bot
```bash
sudo systemctl start crypto-news-bot
```

### Stop bot
```bash
sudo systemctl stop crypto-news-bot
```

### Restart bot
```bash
sudo systemctl restart crypto-news-bot
```

### Enable auto-start on boot
```bash
sudo systemctl enable crypto-news-bot
```

## 🧪 Testing

### Test Telegram connection
```bash
cd ~/Python/Crypto_News_Telegram_Bot
python test_telegram_channel.py
```

### Run bot once (manual test)
```bash
cd ~/Python/Crypto_News_Telegram_Bot
source venv/bin/activate
python Crypto_News_Analyzer.py
# Press Ctrl+C to stop
deactivate
```

## 🔍 Troubleshooting

### View last 50 log lines
```bash
tail -50 ~/Python/Crypto_News_Telegram_Bot/crypto_news_bot.log
```

### Check .env configuration
```bash
cat ~/Python/Crypto_News_Telegram_Bot/.env
```

### Verify channel ID
```bash
grep TELEGRAM_CHAT_ID ~/Python/Crypto_News_Telegram_Bot/.env
```

### Reinstall dependencies
```bash
cd ~/Python/Crypto_News_Telegram_Bot
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate
```

### Force restart everything
```bash
cd ~/Python/Crypto_News_Telegram_Bot
sudo systemctl stop crypto-news-bot
pkill -9 -f Crypto_News_Analyzer.py
sudo systemctl start crypto-news-bot
```

## 📝 Notes

- **Channel ID**: `-1003448714142`
- **Bot runs every**: 1 hour
- **Quiet hours**: 10 PM - 7 AM (no posts)
- **Posts per run**: 1-3 opportunities randomly selected

---

For detailed instructions, see [RASPBERRY_PI_UPDATE.md](RASPBERRY_PI_UPDATE.md)
