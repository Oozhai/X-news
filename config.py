"""
Configuration file for Crypto News Twitter Bot
This file contains all API keys, settings, and customizable lists.
Replace placeholder values with your actual API credentials.
"""

import os
from typing import List

# =============================================================================
# TWITTER/X API CREDENTIALS
# Get these from: https://developer.twitter.com/en/portal/dashboard
# IMPORTANT: Never put real API keys here! Use environment variables or GitHub Secrets
# =============================================================================
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

# =============================================================================
# UNSPLASH API (for crypto-related images)
# Get free API key from: https://unsplash.com/developers
# IMPORTANT: Never put real API keys here! Use environment variables or GitHub Secrets
# =============================================================================
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')

# =============================================================================
# NEWS SOURCES CONFIGURATION
# RSS feeds and APIs for crypto news
# =============================================================================
NEWS_SOURCES = {
    'cointelegraph': {
        'rss_url': 'https://cointelegraph.com/rss',
        'enabled': True
    },
    'coindesk': {
        'rss_url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'enabled': True
    },
    'decrypt': {
        'rss_url': 'https://decrypt.co/feed',
        'enabled': True
    },
    'bitcoin_magazine': {
        'rss_url': 'https://bitcoinmagazine.com/.rss/full/',
        'enabled': True
    },
    'cryptonews': {
        'rss_url': 'https://cryptonews.com/news/feed/',
        'enabled': True
    }
}

# =============================================================================
# CRYPTO HASHTAGS
# Add or remove hashtags as needed. Bot will randomly select 2-3 per tweet.
# =============================================================================
CRYPTO_HASHTAGS: List[str] = [
    '#Bitcoin', '#BTC', '#Ethereum', '#ETH', '#Crypto', '#Cryptocurrency',
    '#Blockchain', '#DeFi', '#Web3', '#Altcoin', '#Trading', '#Investing',
    '#HODL', '#Binance', '#Coinbase', '#NFT', '#Solana', '#Cardano', 'Oozhai',
    '#Polkadot', '#Chainlink', '#CryptoNews', '#DigitalAssets', '#Fintech',
    '#Metaverse', '#GameFi', '#Yield', '#Staking', '#Layer2', '#Lightning'
]

# =============================================================================
# CRYPTO TWITTER ACCOUNTS TO MENTION
# Bot will randomly mention one account per tweet. Include @ symbol.
# =============================================================================
CRYPTO_ACCOUNTS: List[str] = [
    '@CoinTelegraph', '@CoinDesk', '@cz_binance', '@elonmusk', '@VitalikButerin',
    '@aantonop', '@APompliano', '@naval', '@balajis',
    '@CryptoWendyO', '@DocumentingBTC', '@Bitcoin', '@ethereum', '@solana',
    '@cardano', '@Polkadot', '@chainlink', '@MessariCrypto', '@glassnode',
    '@CryptoBirb', '@TheCryptoDog', '@CoinGecko', '@CoinMarketCap'
]

# =============================================================================
# POSTING SCHEDULE CONFIGURATION
# =============================================================================
POSTING_SCHEDULE = {
    # How many times per day to post (12 times every 2 hours)
    'posts_per_day': 12,
    
    # Specific times to post (24-hour format) - every 2 hours
    'post_times': ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', 
                   '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    
    # Timezone (use your local timezone)
    'timezone': 'UTC',
    
    # Minimum hours between posts (reduced for high frequency posting)
    'min_hours_between_posts': 1
}

# =============================================================================
# CONTENT GENERATION SETTINGS
# =============================================================================
CONTENT_SETTINGS = {
    # Maximum tweet length in characters (Twitter limit is 280)
    'max_tweet_length': 250,
    
    # Maximum words in tweet (roughly 60 words = 250 chars)
    'max_words': 60,
    
    # Number of hashtags to add per tweet (reduced for high volume)
    'hashtags_per_tweet': 2,
    
    # Whether to include account mentions (reduced frequency for high volume)
    'include_mentions': True,
    
    # Whether to try attaching images to tweets
    'attach_images': True,
    
    # Unsplash search terms for crypto images (expanded list for variety)
    'image_keywords': [
        'cryptocurrency', 'bitcoin', 'blockchain', 'finance', 'technology',
        'digital currency', 'trading', 'investment', 'fintech', 'money',
        'ethereum', 'crypto trading', 'financial technology', 'digital finance',
        'market analysis', 'crypto coins', 'digital assets', 'defi'
    ]
}

# =============================================================================
# ERROR HANDLING SETTINGS
# =============================================================================
ERROR_SETTINGS = {
    # Whether to continue posting if one news source fails
    'continue_on_source_error': True,
    
    # Whether to post without image if image fetching fails
    'post_without_image_on_error': True,
    
    # Maximum retries for failed operations
    'max_retries': 3,
    
    # Delay between retries (seconds)
    'retry_delay': 5
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_file': 'crypto_bot.log',
    'max_log_size_mb': 10,
    'backup_count': 5
}

# =============================================================================
# VALIDATION FUNCTION
# =============================================================================
def validate_config():
    """Validate that all required configuration is present."""
    required_twitter_keys = [
        TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN
    ]
    
    if any(key == f'your_{key.lower()}_here' for key in required_twitter_keys):
        return False, "Twitter API keys not configured"
    
    if not NEWS_SOURCES:
        return False, "No news sources configured"
    
    if not CRYPTO_HASHTAGS:
        return False, "No hashtags configured"
    
    return True, "Configuration valid"

if __name__ == "__main__":
    is_valid, message = validate_config()
    print(f"Configuration validation: {message}")
