# 🍓 Raspberry Pi Setup Guide

Complete guide to deploy the Crypto News Analyzer Bot on your Raspberry Pi, with automatic startup and background execution.

## 📋 Prerequisites

- Raspberry Pi (any model with network connectivity)
- Raspberry Pi OS (formerly Raspbian) installed
- Internet connection
- SSH access or direct terminal access

## 🚀 Initial Setup

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python and Git

```bash
# Install Python 3 and pip (if not already installed)
sudo apt install python3 python3-pip git -y

# Verify installation
python3 --version
pip3 --version
git --version
```

### Step 3: Clone the Repository

```bash
# Navigate to your home directory
cd ~

# Clone your GitHub repository
git clone https://github.com/mas050/Crypto_News_Telegram_Bot.git

# Navigate into the project directory
cd Crypto_News_Telegram_Bot
```

### Step 4: Create a Virtual Environment

```bash
# Install python3-venv if not already installed
sudo apt install python3-venv python3-full -y

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your prompt should now show (venv) at the beginning
```

### Step 5: Install Python Dependencies

```bash
# Make sure virtual environment is activated (you should see (venv) in prompt)
# Install required packages
pip install -r requirements.txt
```

**Note**: You'll need to activate the virtual environment (`source venv/bin/activate`) every time you want to run commands manually. The systemd service will handle this automatically.

### Step 6: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
nano .env
```

Add your API keys:
```
GEMINI_API_KEY=your_actual_gemini_key
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_CHAT_ID=your_actual_chat_id
TWITTER_BEARER_TOKEN=your_twitter_token_if_you_have_one
```

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 7: Test the Bot

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the bot once to make sure it works
python Crypto_News_Analyzer.py
```

Press `Ctrl+C` to stop after verifying it works.

## 🔄 Auto-Start on Boot (systemd Service)

### Step 1: Create a systemd Service File

```bash
sudo nano /etc/systemd/system/crypto-news-bot.service
```

### Step 2: Add the Following Content

```ini
[Unit]
Description=Crypto News Analyzer Bot
After=network.target

[Service]
Type=simple
User=sebastien
WorkingDirectory=/home/sebastien/Python/Crypto_News_Telegram_Bot
ExecStart=/home/sebastien/Python/Crypto_News_Telegram_Bot/venv/bin/python /home/sebastien/Python/Crypto_News_Telegram_Bot/Crypto_News_Analyzer.py
Restart=always
RestartSec=10
StandardOutput=append:/home/sebastien/Python/Crypto_News_Telegram_Bot/bot.log
StandardError=append:/home/sebastien/Python/Crypto_News_Telegram_Bot/bot_error.log

[Install]
WantedBy=multi-user.target
```

**Important Notes:**
- Replace `sebastien` with your actual username if different
- Replace `/home/sebastien/Python/Crypto_News_Telegram_Bot` with your actual path
- The key change is using `venv/bin/python` instead of system Python

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable crypto-news-bot.service

# Start the service now
sudo systemctl start crypto-news-bot.service
```

### Step 4: Verify the Service is Running

```bash
# Check service status
sudo systemctl status crypto-news-bot.service

# You should see "active (running)" in green
```

## 📊 Managing the Bot

### Check if Bot is Running

```bash
sudo systemctl status crypto-news-bot.service
```

### Stop the Bot

```bash
sudo systemctl stop crypto-news-bot.service
```

### Start the Bot

```bash
sudo systemctl start crypto-news-bot.service
```

### Restart the Bot

```bash
sudo systemctl restart crypto-news-bot.service
```

### Disable Auto-Start on Boot

```bash
sudo systemctl disable crypto-news-bot.service
```

### View Live Logs

```bash
# View output logs
tail -f ~/Crypto_News_Telegram_Bot/bot.log

# View error logs
tail -f ~/Crypto_News_Telegram_Bot/bot_error.log

# View systemd logs
sudo journalctl -u crypto-news-bot.service -f
```

Press `Ctrl+C` to stop viewing logs.

## 🔄 Updating the Bot (Pull Latest from GitHub)

### Method 1: Manual Update

```bash
# Navigate to project directory
cd ~/Python/Crypto_News_Telegram_Bot

# Stop the bot
sudo systemctl stop crypto-news-bot.service

# Pull latest changes from GitHub
git pull origin main

# Activate virtual environment and install any new dependencies
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Start the bot
sudo systemctl start crypto-news-bot.service

# Verify it's running
sudo systemctl status crypto-news-bot.service
```

### Method 2: Create an Update Script

Create a convenient update script:

```bash
nano ~/update-crypto-bot.sh
```

Add this content:

```bash
#!/bin/bash

echo "🔄 Updating Crypto News Bot..."

# Navigate to project directory
cd ~/Python/Crypto_News_Telegram_Bot

# Stop the service
echo "⏸️  Stopping bot..."
sudo systemctl stop crypto-news-bot.service

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Install/update dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Start the service
echo "▶️  Starting bot..."
sudo systemctl start crypto-news-bot.service

# Check status
echo "✅ Bot status:"
sudo systemctl status crypto-news-bot.service --no-pager

echo "🎉 Update complete!"
```

Make it executable:

```bash
chmod +x ~/update-crypto-bot.sh
```

Now you can update anytime with:

```bash
~/update-crypto-bot.sh
```

## 🔧 Troubleshooting

### Bot Not Starting

```bash
# Check for errors in logs
sudo journalctl -u crypto-news-bot.service -n 50

# Check error log file
cat ~/Crypto_News_Telegram_Bot/bot_error.log
```

### Permission Issues

```bash
# Make sure the script is executable
chmod +x ~/Crypto_News_Telegram_Bot/Crypto_News_Analyzer.py

# Check file ownership
ls -la ~/Crypto_News_Telegram_Bot/
```

### Module Not Found Errors

```bash
# Reinstall dependencies in virtual environment
cd ~/Python/Crypto_News_Telegram_Bot
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Check Python Path

```bash
# Find Python location
which python3

# Update ExecStart in service file if needed
sudo nano /etc/systemd/system/crypto-news-bot.service
```

### Service Won't Start After Reboot

```bash
# Check if service is enabled
sudo systemctl is-enabled crypto-news-bot.service

# If not enabled, enable it
sudo systemctl enable crypto-news-bot.service
```

### Git Pull Conflicts

If you have local changes conflicting with GitHub:

```bash
cd ~/Python/Crypto_News_Telegram_Bot

# Stash your local changes (saves them temporarily)
git stash

# Pull latest changes
git pull origin main

# Reapply your changes (if needed)
git stash pop
```

## 📈 Performance Optimization for Raspberry Pi

### Reduce Memory Usage

Edit the script to reduce batch size:

```bash
nano ~/Crypto_News_Telegram_Bot/Crypto_News_Analyzer.py
```

Find line ~227 and change:
```python
batch_size = 5  # Change to 3 for lower memory usage
```

### Monitor Resource Usage

```bash
# Check CPU and memory usage
htop

# Check disk space
df -h

# Check bot process
ps aux | grep Crypto_News_Analyzer
```

## 🔐 Security Best Practices

### Secure Your .env File

```bash
# Set proper permissions (only you can read/write)
chmod 600 ~/Crypto_News_Telegram_Bot/.env
```

### Regular Backups

```bash
# Backup your .env file
cp ~/Crypto_News_Telegram_Bot/.env ~/crypto-bot-env-backup

# Backup history file
cp ~/Crypto_News_Telegram_Bot/sent_news_history.json ~/crypto-bot-history-backup.json
```

### Keep System Updated

```bash
# Run weekly
sudo apt update && sudo apt upgrade -y
```

## 📱 Remote Management via SSH

### Connect to Your Raspberry Pi

```bash
ssh pi@YOUR_RASPBERRY_PI_IP
```

### Useful Remote Commands

```bash
# Quick status check
ssh pi@YOUR_PI_IP "sudo systemctl status crypto-news-bot.service"

# Restart bot remotely
ssh pi@YOUR_PI_IP "sudo systemctl restart crypto-news-bot.service"

# View recent logs
ssh pi@YOUR_PI_IP "tail -n 50 ~/Crypto_News_Telegram_Bot/bot.log"
```

## 🎯 Quick Reference Commands

| Action | Command |
|--------|---------|
| Start bot | `sudo systemctl start crypto-news-bot.service` |
| Stop bot | `sudo systemctl stop crypto-news-bot.service` |
| Restart bot | `sudo systemctl restart crypto-news-bot.service` |
| Check status | `sudo systemctl status crypto-news-bot.service` |
| View logs | `tail -f ~/Crypto_News_Telegram_Bot/bot.log` |
| Update bot | `~/update-crypto-bot.sh` |
| Edit config | `nano ~/Crypto_News_Telegram_Bot/.env` |

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Bot runs manually: `python3 Crypto_News_Analyzer.py`
- [ ] Service starts: `sudo systemctl start crypto-news-bot.service`
- [ ] Service is enabled: `sudo systemctl is-enabled crypto-news-bot.service`
- [ ] Logs are being written: `ls -lh ~/Crypto_News_Telegram_Bot/bot.log`
- [ ] Telegram messages are received
- [ ] Bot survives reboot: `sudo reboot` then check status

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `tail -f ~/Crypto_News_Telegram_Bot/bot.log`
2. Check service status: `sudo systemctl status crypto-news-bot.service`
3. Verify .env file has correct API keys
4. Ensure internet connection is working
5. Check GitHub repository for updates

---

**Your bot is now running 24/7 on your Raspberry Pi! 🎉**
