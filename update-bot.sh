#!/bin/bash

echo "🔄 Updating Crypto News Bot with crash fixes..."
echo ""

# Navigate to project directory
cd ~/Python/Crypto_News_Telegram_Bot || exit 1

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

# Update systemd service file
echo "⚙️  Updating systemd service..."
sudo cp crypto-news-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Start the service
echo "▶️  Starting bot..."
sudo systemctl start crypto-news-bot.service

# Wait a moment for startup
sleep 2

# Check status
echo ""
echo "✅ Bot status:"
sudo systemctl status crypto-news-bot.service --no-pager -l

echo ""
echo "📊 To view logs, run:"
echo "   tail -f ~/Python/Crypto_News_Telegram_Bot/crypto_news_bot.log"
echo ""
echo "🎉 Update complete!"
