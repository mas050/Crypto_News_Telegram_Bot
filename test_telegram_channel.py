#!/usr/bin/env python3
"""
Quick test script to verify Telegram channel connection
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print("=" * 60)
print("Telegram Channel Connection Test")
print("=" * 60)
print(f"Bot Token: {'✓ Set' if bot_token else '✗ Missing'}")
print(f"Chat ID: {chat_id if chat_id else '✗ Missing'}")
print("=" * 60)

if not bot_token or not chat_id:
    print("\n❌ Missing credentials in .env file!")
    print("Please ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set.")
    exit(1)

# Test message
test_message = """
🧪 *Test Message*

This is a test message from your Crypto News Analyzer Bot!

If you're seeing this, your bot is successfully connected to the channel.

✅ Channel ID: `{}`
✅ Connection: Working
""".format(chat_id)

# Send test message
try:
    print("\n📤 Sending test message to channel...")
    
    telegram_api = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': test_message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(telegram_api, json=payload, timeout=10)
    response.raise_for_status()
    
    print("✅ SUCCESS! Test message sent to your Telegram channel!")
    print("\nCheck your channel to see the message.")
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Make sure your bot is an admin in the channel")
    print("2. Run: python Crypto_News_Analyzer.py")
    print("=" * 60)
    
except requests.exceptions.HTTPError as e:
    print(f"\n❌ HTTP Error: {e}")
    print(f"Response: {response.text}")
    print("\nPossible issues:")
    print("- Bot is not added to the channel")
    print("- Bot is not an admin in the channel")
    print("- Channel ID is incorrect")
    print("- Bot token is invalid")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPlease check your credentials and try again.")
