"""
Main orchestrator for Crypto News Twitter Bot
Coordinates news fetching, rewriting, and posting with scheduling
UPDATED FOR HIGH VOLUME POSTING (48 tweets/day)
"""

import schedule
import time
import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional
import sys
import signal
import json
import os

# Import bot modules
from news_fetcher import CryptoNewsFetcher, NewsItem
from rewriter import TweetRewriter
from twitter_bot import TwitterBotManager
from config import (
    POSTING_SCHEDULE, CONTENT_SETTINGS, LOGGING_CONFIG,
    validate_config, ERROR_SETTINGS
)

# Configure logging
def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['log_level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['log_file']),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

class CryptoNewsBot:
    """Main bot class that orchestrates all components."""
    
    def __init__(self):
        self.news_fetcher = CryptoNewsFetcher()
        self.rewriter = TweetRewriter()
        self.twitter_bot = TwitterBotManager()
        self.is_running = False
        self.posted_articles = set()  # Track posted articles to avoid duplicates
        self.stats = {
            'total_posts': 0,
            'successful_posts': 0,
            'failed_posts': 0,
            'last_post_time': None,
            'start_time': datetime.now()
        }
        
        # Load previous stats if they exist
        self.load_stats()
    
    def load_stats(self):
        """Load bot statistics from file."""
        try:
            if os.path.exists('bot_stats.json'):
                with open('bot_stats.json', 'r') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                    if self.stats['last_post_time']:
                        self.stats['last_post_time'] = datetime.fromisoformat(
                            self.stats['last_post_time']
                        )
                    if self.stats['start_time']:
                        self.stats['start_time'] = datetime.fromisoformat(
                            self.stats['start_time']
                        )
        except Exception as e:
            logger.warning(f"Could not load stats: {e}")
    
    def save_stats(self):
        """Save bot statistics to file."""
        try:
            stats_to_save = self.stats.copy()
            if stats_to_save['last_post_time']:
                stats_to_save['last_post_time'] = stats_to_save['last_post_time'].isoformat()
            if stats_to_save['start_time']:
                stats_to_save['start_time'] = stats_to_save['start_time'].isoformat()
            
            with open('bot_stats.json', 'w') as f:
                json.dump(stats_to_save, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save stats: {e}")
    
    def select_news_for_posting(self, count: int = 1) -> List[NewsItem]:
        """
        Select news articles for posting, avoiding duplicates.
        UPDATED: Expanded search for high-volume posting
        
        Args:
            count: Number of articles to select
            
        Returns:
            List of selected news items
        """
        try:
            # Get recent news (expand search for high-volume posting)
            all_news = self.news_fetcher.fetch_all_news(hours_back=12)
            
            if not all_news:
                logger.warning("No recent news found, expanding search to 48 hours")
                all_news = self.news_fetcher.fetch_all_news(hours_back=48)
            
            if not all_news:
                logger.error("No news articles available")
                return []
            
            # Filter out already posted articles
            available_news = [
                item for item in all_news 
                if item.url not in self.posted_articles
            ]
            
            if not available_news:
                logger.warning("All recent articles already posted, clearing history")
                self.posted_articles.clear()
                available_news = all_news
            
            # Select random articles
            selected_count = min(count, len(available_news))
            selected_news = random.sample(available_news, selected_count)
            
            logger.info(f"Selected {len(selected_news)} articles for posting")
            return selected_news
            
        except Exception as e:
            logger.error(f"Error selecting news for posting: {e}")
            return []
    
    def create_and_post_tweet(self, news_item: NewsItem) -> bool:
        """
        Create and post a tweet from a news item.
        
        Args:
            news_item: News article to tweet about
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Creating tweet for: {news_item.title}")
            
            # Create tweet content
            tweet_text = self.rewriter.create_complete_tweet(
                title=news_item.title,
                summary=news_item.summary,
                url=news_item.url
            )
            
            # Select image keyword based on content
            image_keyword = self.select_image_keyword(news_item.title)
            
            # Post tweet
            success = self.twitter_bot.post_crypto_news(
                tweet_text=tweet_text,
                news_url=news_item.url,
                image_keyword=image_keyword
            )
            
            if success:
                # Mark as posted
                self.posted_articles.add(news_item.url)
                
                # Update stats
                self.stats['successful_posts'] += 1
                self.stats['last_post_time'] = datetime.now()
                
                logger.info(f"Successfully posted tweet for: {news_item.title}")
                return True
            else:
                self.stats['failed_posts'] += 1
                logger.error(f"Failed to post tweet for: {news_item.title}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating/posting tweet: {e}")
            self.stats['failed_posts'] += 1
            return False
        finally:
            self.stats['total_posts'] += 1
            self.save_stats()
    
    def select_image_keyword(self, title: str) -> str:
        """Select appropriate image keyword based on article title."""
        title_lower = title.lower()
        
        # Map keywords in title to image search terms
        keyword_map = {
            'bitcoin': 'bitcoin',
            'btc': 'bitcoin',
            'ethereum': 'ethereum',
            'eth': 'ethereum',
            'crypto': 'cryptocurrency',
            'defi': 'decentralized finance',
            'nft': 'nft blockchain',
            'trading': 'crypto trading',
            'market': 'financial market',
            'regulation': 'finance regulation',
            'adoption': 'blockchain technology',
            'investment': 'investment finance'
        }
        
        for keyword, image_term in keyword_map.items():
            if keyword in title_lower:
                return image_term
        
        # Default fallback
        return random.choice(CONTENT_SETTINGS['image_keywords'])
    
    def post_scheduled_content(self):
        """Main method called by scheduler to post content."""
        try:
            logger.info("Starting scheduled posting...")
            
            # Check if we should post (avoid too frequent posting)
            if self.should_skip_posting():
                logger.info("Skipping post due to recent activity")
                return
            
            # Select news to post
            news_items = self.select_news_for_posting(count=1)
            
            if not news_items:
                logger.warning("No news items selected for posting")
                return
            
            # Post the selected news
            for news_item in news_items:
                success = self.create_and_post_tweet(news_item)
                if success:
                    logger.info("Scheduled posting completed successfully")
                    break  # Post one article per scheduled run
                else:
                    logger.warning("Failed to post, trying next article...")
            else:
                logger.error("All selected articles failed to post")
            
        except Exception as e:
            logger.error(f"Error in scheduled posting: {e}")
    
    def should_skip_posting(self) -> bool:
        """Check if we should skip posting due to recent activity."""
        if not self.stats['last_post_time']:
            return False
        
        time_since_last_post = datetime.now() - self.stats['last_post_time']
        min_interval = timedelta(hours=POSTING_SCHEDULE['min_hours_between_posts'])
        
        return time_since_last_post < min_interval
    
    def post_now(self, count: int = 1) -> bool:
        """
        Manually trigger posting (for testing).
        UPDATED: Faster posting for high-volume
        
        Args:
            count: Number of tweets to post
            
        Returns:
            True if at least one tweet was posted successfully
        """
        logger.info(f"Manual posting triggered for {count} tweets")
        
        news_items = self.select_news_for_posting(count=count)
        if not news_items:
            logger.error("No news items available for posting")
            return False
        
        successful_posts = 0
        for news_item in news_items:
            if self.create_and_post_tweet(news_item):
                successful_posts += 1
                # Small delay between multiple posts to avoid rate limiting
                if len(news_items) > 1:
                    time.sleep(10)  # Reduced from 30 to 10 seconds for faster posting
        
        logger.info(f"Manual posting completed: {successful_posts}/{len(news_items)} successful")
        return successful_posts > 0
    
    def setup_schedule(self):
        """Setup the posting schedule."""
        logger.info("Setting up posting schedule...")
        
        post_times = POSTING_SCHEDULE.get('post_times', [])
        
        if post_times:
            # Schedule at specific times
            for post_time in post_times:
                schedule.every().day.at(post_time).do(self.post_scheduled_content)
                logger.info(f"Scheduled daily post at {post_time}")
        else:
            # Distribute posts evenly throughout the day
            posts_per_day = POSTING_SCHEDULE.get('posts_per_day', 3)
            
            if posts_per_day == 1:
                schedule.every().day.at("12:00").do(self.post_scheduled_content)
            elif posts_per_day == 2:
                schedule.every().day.at("09:00").do(self.post_scheduled_content)
                schedule.every().day.at("18:00").do(self.post_scheduled_content)
            elif posts_per_day == 3:
                schedule.every().day.at("09:00").do(self.post_scheduled_content)
                schedule.every().day.at("14:00").do(self.post_scheduled_content)
                schedule.every().day.at("19:00").do(self.post_scheduled_content)
            else:
                # For more than 3 posts, distribute every few hours
                interval_hours = 24 // posts_per_day
                for i in range(posts_per_day):
                    hour = (8 + i * interval_hours) % 24  # Start at 8 AM
                    schedule.every().day.at(f"{hour:02d}:00").do(self.post_scheduled_content)
        
        logger.info(f"Schedule setup complete. Next run: {schedule.next_run()}")
    
    def start(self):
        """Start the bot with scheduling."""
        logger.info("Starting Crypto News Bot...")
        
        # Validate configuration
        is_valid, message = validate_config()
        if not is_valid:
            logger.error(f"Configuration error: {message}")
            return
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.is_running = True
        self.setup_schedule()
        
        logger.info("Bot started successfully. Press Ctrl+C to stop.")
        
        # Main loop
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
                # Periodic cleanup
                if random.random() < 0.01:  # 1% chance each minute
                    self.cleanup()
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.shutdown()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False
    
    def cleanup(self):
        """Perform periodic cleanup tasks.
        UPDATED: Handles more data for high-volume posting"""
        logger.debug("Performing cleanup tasks...")
        
        # Clear old posted articles (increased limit for high-volume posting)
        if len(self.posted_articles) > 2000:
            self.posted_articles = set(list(self.posted_articles)[-1000:])
        
        # Cleanup Twitter bot data
        self.twitter_bot.cleanup_old_data(keep_last=50)
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down Crypto News Bot...")
        self.save_stats()
        logger.info("Bot shutdown complete")
    
    def print_stats(self):
        """Print bot statistics."""
        uptime = datetime.now() - self.stats['start_time']
        success_rate = (
            (self.stats['successful_posts'] / self.stats['total_posts'] * 100) 
            if self.stats['total_posts'] > 0 else 0
        )
        
        print(f"\n=== Crypto News Bot Statistics ===")
        print(f"Uptime: {uptime}")
        print(f"Total posts attempted: {self.stats['total_posts']}")
        print(f"Successful posts: {self.stats['successful_posts']}")
        print(f"Failed posts: {self.stats['failed_posts']}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Last post: {self.stats['last_post_time'] or 'Never'}")
        print(f"Articles posted: {len(self.posted_articles)}")
        print(f"Next scheduled run: {schedule.next_run() or 'Not scheduled'}")
        print("=" * 40)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto News Twitter Bot')
    parser.add_argument('--post-now', action='store_true', 
                       help='Post immediately instead of scheduling')
    parser.add_argument('--count', type=int, default=1,
                       help='Number of tweets to post (for --post-now)')
    parser.add_argument('--stats', action='store_true',
                       help='Show bot statistics')
    parser.add_argument('--test', action='store_true',
                       help='Test bot components without posting')
    
    args = parser.parse_args()
    
    bot = CryptoNewsBot()
    
    if args.stats:
        bot.print_stats()
        return
    
    if args.test:
        logger.info("Running bot tests...")
        # Test each component
        print("Testing news fetcher...")
        news_items = bot.news_fetcher.get_random_recent_news(1)
        if news_items:
            print(f"✅ Found {len(news_items)} news articles")
            
            print("Testing rewriter...")
            tweet_text = bot.rewriter.create_complete_tweet(news_items[0].title)
            print(f"✅ Created tweet: {tweet_text}")
            
            print("✅ All tests passed! (Twitter posting not tested)")
        else:
            print("❌ No news articles found")
        return
    
    if args.post_now:
        logger.info("Manual posting mode")
        success = bot.post_now(count=args.count)
        if success:
            print(f"✅ Successfully posted {args.count} tweet(s)")
        else:
            print("❌ Failed to post tweets")
    else:
        # Normal scheduled operation
        bot.start()

if __name__ == "__main__":
    main()