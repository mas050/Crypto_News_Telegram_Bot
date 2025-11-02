# Crypto News Analyzer - Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   ```bash
   nano .env  # or use your preferred text editor
   ```

### 3. Get Your API Keys

#### Google Gemini API Key (Required)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy and paste it into `.env` as `GEMINI_API_KEY`

#### Telegram Bot Token (Required)
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided
5. Paste it into `.env` as `TELEGRAM_BOT_TOKEN`

#### Telegram Chat ID (Required)
1. Open Telegram and search for `@userinfobot`
2. Send `/start` command
3. The bot will reply with your chat ID
4. Copy the ID and paste it into `.env` as `TELEGRAM_CHAT_ID`

#### Twitter Bearer Token (Optional)
1. Visit: https://developer.twitter.com/en/portal/dashboard
2. Create a Twitter Developer account if you don't have one
3. Create a new project and app
4. Generate a Bearer Token
5. Paste it into `.env` as `TWITTER_BEARER_TOKEN`
   - Leave empty if you don't want Twitter integration

### 4. Verify Your Setup

Your `.env` file should look like this (with your actual keys):
```
GEMINI_API_KEY=AIzaSyD...your_actual_key
TELEGRAM_BOT_TOKEN=1234567890:ABC...your_actual_token
TELEGRAM_CHAT_ID=123456789
TWITTER_BEARER_TOKEN=AAAAAAAAAA...your_actual_token
```

## Running the Script

```bash
python Crypto_News_Analyzer.py
```

The script will:
- Run immediately on startup
- Schedule to run every hour automatically
- Send crypto opportunities to your Telegram chat

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your `.env` file to version control
- Never share your API keys publicly
- The `.env` file is already in `.gitignore` to prevent accidental commits
- Keep `.env.example` as a template (without real keys)

## Troubleshooting

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "Gemini API key not set"
Make sure your `.env` file exists and contains `GEMINI_API_KEY=your_key`

### "Telegram credentials not set"
Verify both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are in your `.env` file

### Script not finding .env file
Make sure the `.env` file is in the same directory as `Crypto_News_Analyzer.py`
