#!/bin/bash

echo "================================================================================"
echo "🔍 Crypto News Bot Diagnostics"
echo "================================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "Crypto_News_Analyzer.py" ]; then
    echo "❌ Error: Not in the bot directory!"
    echo "Please run this from ~/Python/Crypto_News_Telegram_Bot"
    exit 1
fi

echo "📁 Current Directory: $(pwd)"
echo ""

# Check if .env file exists
echo "1️⃣  Checking .env file..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    
    # Check for required variables (without showing values)
    if grep -q "GEMINI_API_KEY=" .env && [ -n "$(grep GEMINI_API_KEY= .env | cut -d'=' -f2)" ]; then
        echo "   ✅ GEMINI_API_KEY is set"
    else
        echo "   ❌ GEMINI_API_KEY is missing or empty"
    fi
    
    if grep -q "TELEGRAM_BOT_TOKEN=" .env && [ -n "$(grep TELEGRAM_BOT_TOKEN= .env | cut -d'=' -f2)" ]; then
        echo "   ✅ TELEGRAM_BOT_TOKEN is set"
    else
        echo "   ❌ TELEGRAM_BOT_TOKEN is missing or empty"
    fi
    
    if grep -q "TELEGRAM_CHAT_ID=" .env && [ -n "$(grep TELEGRAM_CHAT_ID= .env | cut -d'=' -f2)" ]; then
        CHAT_ID=$(grep TELEGRAM_CHAT_ID= .env | cut -d'=' -f2)
        echo "   ✅ TELEGRAM_CHAT_ID is set to: $CHAT_ID"
        
        if [ "$CHAT_ID" = "-1003448714142" ]; then
            echo "   ✅ Channel ID matches expected value"
        else
            echo "   ⚠️  Channel ID is different from expected (-1003448714142)"
        fi
    else
        echo "   ❌ TELEGRAM_CHAT_ID is missing or empty"
    fi
else
    echo "   ❌ .env file not found!"
fi
echo ""

# Check if bot service is running
echo "2️⃣  Checking bot service status..."
if systemctl is-active --quiet crypto-news-bot.service; then
    echo "   ✅ Bot service is RUNNING"
    UPTIME=$(systemctl show crypto-news-bot.service -p ActiveEnterTimestamp --value)
    echo "   📅 Started: $UPTIME"
else
    echo "   ❌ Bot service is NOT running"
    echo "   💡 Try: sudo systemctl start crypto-news-bot"
fi
echo ""

# Check for bot process
echo "3️⃣  Checking for bot process..."
if pgrep -f "Crypto_News_Analyzer.py" > /dev/null; then
    echo "   ✅ Bot process is running"
    PID=$(pgrep -f "Crypto_News_Analyzer.py")
    echo "   🆔 Process ID: $PID"
else
    echo "   ❌ No bot process found"
fi
echo ""

# Check log file
echo "4️⃣  Checking log file..."
if [ -f "crypto_news_bot.log" ]; then
    echo "   ✅ Log file exists"
    LOG_SIZE=$(du -h crypto_news_bot.log | cut -f1)
    echo "   📊 Log size: $LOG_SIZE"
    
    echo ""
    echo "   📋 Last 10 log entries:"
    echo "   ─────────────────────────────────────────────────────────────────"
    tail -10 crypto_news_bot.log | sed 's/^/   /'
    echo "   ─────────────────────────────────────────────────────────────────"
else
    echo "   ⚠️  Log file not found (bot may not have run yet)"
fi
echo ""

# Check history file
echo "5️⃣  Checking news history..."
if [ -f "sent_news_history.json" ]; then
    echo "   ✅ History file exists"
    HISTORY_COUNT=$(grep -o '"' sent_news_history.json | wc -l)
    echo "   📊 Entries in history: ~$((HISTORY_COUNT / 4))"
else
    echo "   ⚠️  No history file yet (normal for first run)"
fi
echo ""

# Check systemd logs
echo "6️⃣  Recent systemd logs (last 20 lines)..."
echo "   ─────────────────────────────────────────────────────────────────"
sudo journalctl -u crypto-news-bot -n 20 --no-pager | sed 's/^/   /'
echo "   ─────────────────────────────────────────────────────────────────"
echo ""

# Check for errors in logs
echo "7️⃣  Checking for errors..."
if [ -f "crypto_news_bot.log" ]; then
    ERROR_COUNT=$(grep -i "error" crypto_news_bot.log | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "   ⚠️  Found $ERROR_COUNT error(s) in log file"
        echo ""
        echo "   Recent errors:"
        echo "   ─────────────────────────────────────────────────────────────────"
        grep -i "error" crypto_news_bot.log | tail -5 | sed 's/^/   /'
        echo "   ─────────────────────────────────────────────────────────────────"
    else
        echo "   ✅ No errors found in log file"
    fi
else
    echo "   ⚠️  Cannot check - log file doesn't exist"
fi
echo ""

# Check quiet hours
echo "8️⃣  Checking current time and quiet hours..."
CURRENT_HOUR=$(date +%H)
echo "   🕐 Current hour: ${CURRENT_HOUR}:00"
if [ $CURRENT_HOUR -ge 22 ] || [ $CURRENT_HOUR -lt 7 ]; then
    echo "   🌙 QUIET HOURS ACTIVE (10 PM - 7 AM)"
    echo "   ⚠️  Bot will not post during quiet hours!"
else
    echo "   ✅ Not in quiet hours - bot should be active"
fi
echo ""

echo "================================================================================"
echo "📝 SUMMARY & RECOMMENDATIONS"
echo "================================================================================"
echo ""

# Provide recommendations
ISSUES=0

if [ ! -f ".env" ]; then
    echo "❌ Create .env file with your API keys"
    ISSUES=$((ISSUES + 1))
fi

if ! systemctl is-active --quiet crypto-news-bot.service; then
    echo "❌ Start the bot service: sudo systemctl start crypto-news-bot"
    ISSUES=$((ISSUES + 1))
fi

if [ $CURRENT_HOUR -ge 22 ] || [ $CURRENT_HOUR -lt 7 ]; then
    echo "⚠️  Bot is in quiet hours - wait until 7 AM for posts"
fi

if [ -f "crypto_news_bot.log" ]; then
    if grep -q "Telegram credentials not set" crypto_news_bot.log; then
        echo "❌ Check your .env file - Telegram credentials may be incorrect"
        ISSUES=$((ISSUES + 1))
    fi
    
    if grep -q "No new items to analyze" crypto_news_bot.log; then
        echo "ℹ️  Bot is running but all news items are duplicates (this is normal)"
    fi
    
    if grep -q "No opportunities to send" crypto_news_bot.log; then
        echo "ℹ️  Bot analyzed news but found no significant opportunities (this is normal)"
    fi
fi

if [ $ISSUES -eq 0 ]; then
    echo "✅ No critical issues detected!"
    echo ""
    echo "💡 If you still don't see messages:"
    echo "   1. Make sure your bot is an ADMIN in the Telegram channel"
    echo "   2. Run: python test_telegram_channel.py"
    echo "   3. Check if it's quiet hours (10 PM - 7 AM)"
    echo "   4. Wait for the next hourly run"
    echo "   5. Check: tail -f crypto_news_bot.log"
fi

echo ""
echo "================================================================================"
