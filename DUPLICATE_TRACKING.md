# Duplicate News Tracking

## How It Works

The bot automatically tracks **all analyzed news** (both opportunities and non-opportunities) to prevent wasting API calls on re-analysis using a **local JSON file** approach.

### Key Features

1. **Unique Identification**: Each news item is identified by a hash of its title + link
2. **Smart Filtering**: Filters out ALL previously analyzed items (not just sent ones!)
3. **API Cost Optimization**: Avoids re-analyzing items Gemini already rejected
4. **Auto-Cleanup**: History older than 7 days is automatically removed
5. **Persistent Storage**: Uses `sent_news_history.json` to store the history

### Workflow

```
Fetch News → Filter Already-Analyzed → AI Analysis → Mark as Analyzed → Filter Opportunities → Send to Telegram → Save History
```

### File Structure

The `sent_news_history.json` file stores:
```json
{
  "hash_id_1": 1699123456.789,
  "hash_id_2": 1699234567.890
}
```
- **Key**: MD5 hash of "title|link"
- **Value**: Unix timestamp when sent

### Benefits

✅ **Simple**: No external dependencies or API setup  
✅ **Fast**: Local file access  
✅ **Reliable**: No network calls needed  
✅ **Private**: Data stays on your machine  
✅ **Automatic**: Cleans up old entries (7 days)  

### Alternative: Google Sheets (Not Implemented)

If you prefer Google Sheets for tracking:

**Pros:**
- Accessible from anywhere
- Easy to view/edit manually
- Can share with team

**Cons:**
- Requires Google API setup
- Slower (network calls)
- More complex authentication
- API quota limits

**To implement Google Sheets:**
1. Install: `pip install gspread google-auth`
2. Set up Google Cloud credentials
3. Replace `_load_history()` and `_save_history()` methods

### Monitoring

The bot logs duplicate detection:
```
🔍 Filtered out 3 duplicate(s), 2 new opportunities to send
```

### Manual Management

To reset history (send all news again):
```bash
rm sent_news_history.json
```

To view current history:
```bash
cat sent_news_history.json | python -m json.tool
```

### Customization

Change retention period in `_load_history()`:
```python
# Current: 7 days
if current_time - timestamp < 7 * 24 * 60 * 60

# Change to 3 days:
if current_time - timestamp < 3 * 24 * 60 * 60

# Change to 30 days:
if current_time - timestamp < 30 * 24 * 60 * 60
```
