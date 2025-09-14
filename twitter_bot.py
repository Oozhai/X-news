"""
Twitter API integration module for Crypto News Bot
Handles authentication, media upload, and tweet posting
"""

import tweepy
import requests
import logging
import tempfile
import os
from typing import Optional, Dict, Any
from PIL import Image
import io
from config import (
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN, 
    UNSPLASH_ACCESS_KEY, CONTENT_SETTINGS, ERROR_SETTINGS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterBot:
    """Main Twitter bot class for posting tweets with media."""
    
    def __init__(self):
        self.api_v1 = None
        self.api_v2 = None
        self.unsplash_session = requests.Session()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Twitter API v1.1 and v2."""
        try:
            # Twitter API v1.1 (for media upload)
            auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
            self.api_v1 = tweepy.API(auth)
            
            # Twitter API v2 (for tweet posting)
            self.api_v2 = tweepy.Client(
                bearer_token=TWITTER_BEARER_TOKEN,
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            # Test authentication
            self._test_authentication()
            logger.info("Twitter API authentication successful")
            
        except Exception as e:
            logger.error(f"Twitter API authentication failed: {e}")
            raise
    
    def _test_authentication(self):
        """Test Twitter API authentication."""
        try:
            # Test v2 API
            me = self.api_v2.get_me()
            logger.info(f"Authenticated as: @{me.data.username}")
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            raise
    
    def fetch_crypto_image(self, keyword: str = "cryptocurrency") -> Optional[str]:
        """
        Fetch a crypto-related image from Unsplash.
        
        Args:
            keyword: Search keyword for images
            
        Returns:
            Path to downloaded image file, or None if failed
        """
        if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == 'your_unsplash_access_key_here':
            logger.warning("Unsplash API key not configured")
            return None
        
        try:
            # Search for images on Unsplash
            search_url = "https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
            params = {
                "query": keyword,
                "orientation": "landscape",
                "per_page": 10,
                "order_by": "relevant"
            }
            
            response = self.unsplash_session.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('results'):
                logger.warning(f"No images found for keyword: {keyword}")
                return None
            
            # Get a random image from results
            import random
            image_data = random.choice(data['results'])
            image_url = image_data['urls']['regular']  # Use regular size (good for Twitter)
            
            # Download the image
            image_response = self.unsplash_session.get(image_url, timeout=15)
            image_response.raise_for_status()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            
            # Process image to ensure it meets Twitter requirements
            image = Image.open(io.BytesIO(image_response.content))
            
            # Resize if too large (Twitter max: 3MB, 3200x1800px)
            if image.width > 3200 or image.height > 1800:
                image.thumbnail((3200, 1800), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save optimized image
            image.save(temp_file.name, 'JPEG', quality=85, optimize=True)
            
            logger.info(f"Downloaded image: {image_url}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error fetching image: {e}")
            return None
    
    def upload_media(self, media_path: str) -> Optional[str]:
        """
        Upload media to Twitter and return media_id.
        
        Args:
            media_path: Path to media file
            
        Returns:
            Media ID string, or None if failed
        """
        try:
            # Upload media using API v1.1
            media = self.api_v1.media_upload(filename=media_path)
            logger.info(f"Media uploaded successfully: {media.media_id}")
            return media.media_id
            
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            return None
        finally:
            # Clean up temp file
            if os.path.exists(media_path):
                try:
                    os.unlink(media_path)
                except:
                    pass
    
    def post_tweet(self, text: str, media_ids: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """
        Post a tweet with optional media.
        
        Args:
            text: Tweet text
            media_ids: List of media IDs to attach
            
        Returns:
            Tweet data if successful, None if failed
        """
        try:
            # Post tweet using API v2
            response = self.api_v2.create_tweet(
                text=text,
                media_ids=media_ids
            )
            
            tweet_id = response.data['id']
            logger.info(f"Tweet posted successfully: https://twitter.com/user/status/{tweet_id}")
            
            return {
                'id': tweet_id,
                'text': text,
                'url': f"https://twitter.com/user/status/{tweet_id}"
            }
            
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None
    
    def post_tweet_with_image(self, text: str, image_keyword: str = None) -> Optional[Dict[str, Any]]:
        """
        Post a tweet with an automatically fetched image.
        
        Args:
            text: Tweet text
            image_keyword: Keyword for image search (optional)
            
        Returns:
            Tweet data if successful, None if failed
        """
        media_ids = None
        
        # Try to attach image if enabled
        if CONTENT_SETTINGS['attach_images']:
            if not image_keyword:
                image_keyword = random.choice(CONTENT_SETTINGS['image_keywords'])
            
            image_path = self.fetch_crypto_image(image_keyword)
            if image_path:
                media_id = self.upload_media(image_path)
                if media_id:
                    media_ids = [media_id]
        
        # Post tweet (with or without media)
        return self.post_tweet(text, media_ids)
    
    def get_tweet_analytics(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get basic analytics for a tweet.
        
        Args:
            tweet_id: Twitter tweet ID
            
        Returns:
            Analytics data if available
        """
        try:
            tweet = self.api_v2.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            if tweet.data:
                return {
                    'tweet_id': tweet_id,
                    'created_at': tweet.data.created_at,
                    'metrics': tweet.data.public_metrics
                }
            
        except Exception as e:
            logger.error(f"Error fetching tweet analytics: {e}")
        
        return None
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet.
        
        Args:
            tweet_id: Twitter tweet ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.api_v2.delete_tweet(tweet_id)
            logger.info(f"Tweet {tweet_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting tweet {tweet_id}: {e}")
            return False

class TwitterBotManager:
    """High-level manager for Twitter bot operations."""
    
    def __init__(self):
        self.bot = TwitterBot()
        self.posted_tweets = []  # Track posted tweets
    
    def post_crypto_news(self, tweet_text: str, news_url: str = "", 
                        image_keyword: str = None) -> bool:
        """
        Post a crypto news tweet with all enhancements.
        
        Args:
            tweet_text: The tweet content
            news_url: Optional news article URL
            image_keyword: Optional keyword for image search
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            # Add URL to tweet if provided and space allows
            final_text = tweet_text
            if news_url and len(tweet_text) + len(news_url) + 1 <= CONTENT_SETTINGS['max_tweet_length']:
                final_text = f"{tweet_text} {news_url}"
            
            # Post tweet with image
            result = self.bot.post_tweet_with_image(final_text, image_keyword)
            
            if result:
                self.posted_tweets.append(result)
                logger.info(f"Successfully posted crypto news tweet: {result['id']}")
                return True
            else:
                logger.error("Failed to post crypto news tweet")
                return False
                
        except Exception as e:
            logger.error(f"Error in post_crypto_news: {e}")
            return False
    
    def get_recent_tweets(self, count: int = 10) -> list:
        """Get recently posted tweets."""
        return self.posted_tweets[-count:] if self.posted_tweets else []
    
    def cleanup_old_data(self, keep_last: int = 100):
        """Keep only the last N tweets in memory."""
        if len(self.posted_tweets) > keep_last:
            self.posted_tweets = self.posted_tweets[-keep_last:]

def test_twitter_bot():
    """Test Twitter bot functionality."""
    try:
        bot = TwitterBot()
        print("✅ Twitter authentication successful")
        
        # Test image fetching
        print("Testing image fetching...")
        image_path = bot.fetch_crypto_image("bitcoin")
        if image_path:
            print(f"✅ Image fetched: {image_path}")
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
        else:
            print("⚠️  Image fetching failed (check Unsplash API key)")
        
        print("Twitter bot test completed successfully!")
        
    except Exception as e:
        print(f"❌ Twitter bot test failed: {e}")

if __name__ == "__main__":
    test_twitter_bot()