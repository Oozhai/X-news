# 🚀 Crypto News Twitter Bot

An automated Twitter bot that fetches the latest cryptocurrency news from multiple sources, rewrites headlines into engaging tweets, and posts them with relevant images and hashtags.

## ✨ Features

- **Multi-Source News Fetching**: Pulls from CoinTelegraph, CoinDesk, Decrypt, Bitcoin Magazine, and more
- **Intelligent Rewriting**: Transforms news headlines into catchy, Twitter-friendly content
- **Smart Media Integration**: Automatically fetches and attaches crypto-related images
- **Hashtag & Mention Management**: Adds relevant hashtags and mentions crypto accounts
- **Flexible Scheduling**: Post 1-6 times daily at custom times or evenly distributed
- **Duplicate Prevention**: Avoids posting the same news twice
- **Error Handling**: Continues working even if some sources fail
- **Analytics Tracking**: Monitor posting success rates and performance
- **Production Ready**: Designed for deployment on free hosting platforms

## 📁 Project Structure

```
crypto-twitter-bot/
├── config.py          # API keys and configuration
├── news_fetcher.py     # RSS feed and news source handling
├── rewriter.py         # Content rewriting and tweet generation
├── twitter_bot.py      # Twitter API integration and media handling
├── main.py            # Main orchestrator and scheduler
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

#### Twitter/X API Keys (Required)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app and generate:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token

#### Unsplash API Key (Optional but recommended)
1. Go to [Unsplash Developers](https://unsplash.com/developers)
2. Create a new app and get your Access Key

### 3. Configure the Bot

Open `config.py` and replace the placeholder values:

```python
# Replace these with your actual API keys
TWITTER_API_KEY = 'your_actual_api_key'
TWITTER_API_SECRET = 'your_actual_api_secret' 
TWITTER_ACCESS_TOKEN = 'your_actual_access_token'
TWITTER_ACCESS_TOKEN_SECRET = 'your_actual_access_token_secret'
TWITTER_BEARER_TOKEN = 'your_actual_bearer_token'
UNSPLASH_ACCESS_KEY = 'your_actual_unsplash_key'
```

### 4. Customize Settings (Optional)

Edit `config.py` to customize:

- **Hashtags**: Add/remove crypto hashtags in `CRYPTO_HASHTAGS`
- **Mentions**: Modify accounts to mention in `CRYPTO_ACCOUNTS`
- **Posting Schedule**: Adjust times and frequency in `POSTING_SCHEDULE`
- **News Sources**: Enable/disable sources in `NEWS_SOURCES`

## 🚀 Usage

### Start the Bot (Scheduled Mode)

```bash
python main.py
```

This starts the bot with automatic scheduling. It will post according to your configured schedule.

### Manual Commands

#### Post Immediately (Testing)
```bash
python main.py --post-now
```

#### Post Multiple Tweets
```bash
python main.py --post-now --count 3
```

#### View Statistics
```bash
python main.py --stats
```

#### Test Components
```bash
python main.py --test
```

### Environment Variables (Alternative Setup)

Instead of editing `config.py`, you can set environment variables:

```bash
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
export TWITTER_BEARER_TOKEN="your_bearer_token"
export UNSPLASH_ACCESS_KEY="your_unsplash_key"
```

## 🔧 Customization Guide

### Adding New News Sources

Edit the `NEWS_SOURCES` dictionary in `config.py`:

```python
NEWS_SOURCES = {
    'your_source_name': {
        'rss_url': 'https://example.com/rss',
        'enabled': True
    }
}
```

### Adjusting Tweet Style

Modify these settings in `config.py`:

```python
CONTENT_SETTINGS = {
    'max_tweet_length': 250,        # Character limit
    'max_words': 60,                # Word limit
    'hashtags_per_tweet': 3,        # Number of hashtags
    'include_mentions': True,       # Include account mentions
    'attach_images': True,          # Attach images to tweets
}
```

### Changing Posting Schedule

Update `POSTING_SCHEDULE` in `config.py`:

```python
POSTING_SCHEDULE = {
    'posts_per_day': 4,
    'post_times': ['08:00', '12:00', '16:00', '20:00'],
    'timezone': 'UTC',
    'min_hours_between_posts': 3
}
```

## 🌐 Deployment Options

### Free Hosting Platforms

#### GitHub Actions (Recommended)
Create `.github/workflows/bot.yml`:

```yaml
name: Crypto Twitter Bot
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run bot
      env:
        TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
        TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
        TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
        TWITTER_ACCESS_TOKEN_SECRET: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
        TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
        UNSPLASH_ACCESS_KEY: ${{ secrets.UNSPLASH_ACCESS_KEY }}
      run: python main.py --post-now
```

Add your API keys as GitHub Secrets in repository settings.

#### Replit
1. Create a new Python Repl
2. Upload all files
3. Add API keys as environment variables in Secrets tab
4. Use Replit's Always On feature (paid) or cron jobs

#### Railway
1. Connect your GitHub repository
2. Add environment variables
3. Deploy automatically

### VPS/Server Deployment

#### Using systemd (Linux)

Create `/etc/systemd/system/crypto-bot.service`:

```ini
[Unit]
Description=Crypto Twitter Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/crypto-twitter-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=60
Environment=PYTHONPATH=/path/to/crypto-twitter-bot

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl enable crypto-bot
sudo systemctl start crypto-bot
sudo systemctl status crypto-bot
```

#### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t crypto-bot .
docker run -d --name crypto-bot \
  -e TWITTER_API_KEY="your_key" \
  -e TWITTER_API_SECRET="your_secret" \
  crypto-bot
```

## 📊 Monitoring and Logs

### View Logs
```bash
tail -f crypto_bot.log
```

### Check Statistics
```bash
python main.py --stats
```

### Monitor Files
- `crypto_bot.log` - Detailed application logs
- `bot_stats.json` - Performance statistics
- Console output - Real-time status

## 🛡️ Best Practices

### Rate Limiting
- The bot respects Twitter's rate limits
- Minimum 4-hour gap between posts by default
- Automatic retry logic for failed requests

### Content Quality
- Avoids duplicate posts within 24 hours
- Rewrites content to avoid copyright issues
- Filters for recent news only (6-24 hours)

### Error Handling
- Continues working if individual news sources fail
- Posts text-only tweets if image fetching fails
- Automatic retry for temporary failures

### Security
- Use environment variables for API keys in production
- Regularly rotate API keys
- Monitor for unusual activity

## 🔍 Troubleshooting

### Common Issues

#### "Authentication failed"
- Verify all Twitter API keys are correct
- Check that your Twitter app has write permissions
- Ensure Bearer Token is included

#### "No news articles found"
- Check if RSS feeds are accessible
- Verify internet connection
- Try expanding time range in `news_fetcher.py`

#### "Image upload failed"
- Check Unsplash API key
- Verify image processing (PIL) is working
- Disable images temporarily: `'attach_images': False`

#### Bot not posting on schedule
- Check system timezone settings
- Verify schedule configuration in `config.py`
- Look for errors in `crypto_bot.log`

### Debug Mode

Enable detailed logging in `config.py`:
```python
LOGGING_CONFIG = {
    'log_level': 'DEBUG'
}
```

### Manual Testing

Test individual components:
```bash
# Test news fetching
python news_fetcher.py

# Test rewriting
python rewriter.py

# Test Twitter connection
python twitter_bot.py
```

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review logs for error messages
3. Test individual components
4. Verify API keys and permissions

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks
- Monitor API usage and limits
- Update news source URLs if they change
- Refresh hashtags and mentions periodically
- Check for Twitter API updates

### Updating the Bot
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## ⚠️ Important Notes

- **Compliance**: Ensure your bot usage complies with Twitter's Terms of Service
- **Content**: The bot rephrases news content but you're responsible for what gets posted
- **Rate Limits**: Twitter has strict rate limits - don't modify timing without understanding limits
- **Monitoring**: Always monitor your bot's activity, especially in the first few days

---

**Ready to launch your crypto news bot? Follow the setup steps above and start posting automated crypto updates!** 🚀💰