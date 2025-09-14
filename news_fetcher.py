"""
News fetcher module for Crypto News Twitter Bot
Handles fetching news from multiple RSS feeds and APIs
UPDATED FOR HIGH VOLUME POSTING (more articles, longer timeframe)
"""

import feedparser
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import random
from config import NEWS_SOURCES, ERROR_SETTINGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsItem:
    """Data class to represent a news article."""
    
    def __init__(self, title: str, summary: str, url: str, published: datetime, source: str, image_url: Optional[str] = None):
        self.title = title
        self.summary = summary
        self.url = url
        self.published = published
        self.source = source
        self.image_url = image_url
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for easy serialization."""
        return {
            'title': self.title,
            'summary': self.summary,
            'url': self.url,
            'published': self.published.isoformat(),
            'source': self.source,
            'image_url': self.image_url
        }

class CryptoNewsFetcher:
    """Main class for fetching crypto news from various sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoNewsBot/1.0 (RSS Feed Reader)'
        })
        
    def fetch_rss_feed(self, url: str, source_name: str) -> List[NewsItem]:
        """Fetch news from an RSS feed.
        UPDATED: Gets more articles per source for high-volume posting"""
        news_items = []
        
        try:
            logger.info(f"Fetching RSS feed from {source_name}: {url}")
            
            # Add timeout and retries
            for attempt in range(ERROR_SETTINGS['max_retries']):
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {source_name}: {e}")
                    if attempt == ERROR_SETTINGS['max_retries'] - 1:
                        raise
                    time.sleep(ERROR_SETTINGS['retry_delay'])
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"RSS feed from {source_name} has parsing issues")
            
            for entry in feed.entries[:15]:  # Increased from 10 to 15 for high-volume posting
                try:
                    # Parse publication date
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    
                    # Skip articles older than 48 hours (expanded for high-volume)
                    if published < datetime.now() - timedelta(hours=48):
                        continue
                    
                    # Extract image URL if available
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url')
                    elif hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if enclosure.type.startswith('image/'):
                                image_url = enclosure.href
                                break
                    
                    # Create news item
                    news_item = NewsItem(
                        title=entry.title,
                        summary=entry.get('summary', entry.title),
                        url=entry.link,
                        published=published,
                        source=source_name,
                        image_url=image_url
                    )
                    
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.error(f"Error parsing entry from {source_name}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(news_items)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source_name}: {e}")
            if not ERROR_SETTINGS['continue_on_source_error']:
                raise
        
        return news_items
    
    def fetch_all_news(self, hours_back: int = 24) -> List[NewsItem]:
        """Fetch news from all enabled sources."""
        all_news = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for source_name, source_config in NEWS_SOURCES.items():
            if not source_config.get('enabled', False):
                logger.info(f"Skipping disabled source: {source_name}")
                continue
            
            try:
                if 'rss_url' in source_config:
                    news_items = self.fetch_rss_feed(
                        source_config['rss_url'], 
                        source_name
                    )
                    
                    # Filter by time
                    recent_news = [
                        item for item in news_items 
                        if item.published > cutoff_time
                    ]
                    
                    all_news.extend(recent_news)
                    
            except Exception as e:
                logger.error(f"Failed to fetch from {source_name}: {e}")
                if not ERROR_SETTINGS['continue_on_source_error']:
                    raise
        
        # Remove duplicates based on title similarity
        all_news = self._remove_duplicates(all_news)
        
        # Sort by publication time (newest first)
        all_news.sort(key=lambda x: x.published, reverse=True)
        
        logger.info(f"Total unique articles fetched: {len(all_news)}")
        return all_news
    
    def _remove_duplicates(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate articles based on title similarity."""
        unique_news = []
        seen_titles = set()
        
        for item in news_items:
            # Simple duplicate detection based on normalized title
            normalized_title = item.title.lower().strip()
            
            # Remove common prefixes that might vary between sources
            prefixes_to_remove = [
                'breaking:', 'update:', 'news:', 'crypto:', 'bitcoin:',
                'ethereum:', 'exclusive:', 'analysis:'
            ]
            
            for prefix in prefixes_to_remove:
                if normalized_title.startswith(prefix):
                    normalized_title = normalized_title[len(prefix):].strip()
            
            # Check for similarity (simple approach)
            is_duplicate = False
            for seen_title in seen_titles:
                if self._titles_similar(normalized_title, seen_title):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(normalized_title)
                unique_news.append(item)
        
        return unique_news
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.7) -> bool:
        """Check if two titles are similar (simple word overlap method)."""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity >= threshold
    
    def get_random_recent_news(self, count: int = 1) -> List[NewsItem]:
        """Get random recent news items for posting."""
        all_news = self.fetch_all_news(hours_back=6)  # Last 6 hours for freshness
        
        if not all_news:
            logger.warning("No recent news found, fetching from last 24 hours")
            all_news = self.fetch_all_news(hours_back=24)
        
        if not all_news:
            logger.error("No news articles found")
            return []
        
        # Select random articles
        selected_count = min(count, len(all_news))
        return random.sample(all_news, selected_count)

def test_news_fetcher():
    """Test function to verify news fetching works."""
    fetcher = CryptoNewsFetcher()
    
    print("Testing news fetcher...")
    news_items = fetcher.fetch_all_news(hours_back=24)
    
    print(f"Found {len(news_items)} articles:")
    for i, item in enumerate(news_items[:5]):  # Show first 5
        print(f"\n{i+1}. {item.title}")
        print(f"   Source: {item.source}")
        print(f"   Published: {item.published}")
        print(f"   URL: {item.url}")
        print(f"   Summary: {item.summary[:100]}...")
        if item.image_url:
            print(f"   Image: {item.image_url}")

if __name__ == "__main__":
    test_news_fetcher()