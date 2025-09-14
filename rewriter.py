"""
Content rewriter module for Crypto News Twitter Bot
Transforms news headlines and summaries into engaging tweets
"""

import re
import random
import logging
from typing import List, Dict, Optional
from config import CONTENT_SETTINGS, CRYPTO_HASHTAGS, CRYPTO_ACCOUNTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TweetRewriter:
    """Main class for rewriting news content into tweet format."""
    
    def __init__(self):
        # Synonym dictionary for common crypto terms
        self.synonyms = {
            'bitcoin': ['BTC', 'Bitcoin', 'digital gold'],
            'ethereum': ['ETH', 'Ethereum', 'smart contracts platform'],
            'cryptocurrency': ['crypto', 'digital currency', 'virtual currency'],
            'blockchain': ['distributed ledger', 'DLT', 'blockchain tech'],
            'price': ['value', 'trading at', 'worth'],
            'increases': ['rises', 'surges', 'climbs', 'jumps', 'spikes'],
            'decreases': ['falls', 'drops', 'declines', 'dips', 'slides'],
            'reaches': ['hits', 'touches', 'achieves'],
            'announces': ['reveals', 'unveils', 'declares'],
            'partnership': ['collaboration', 'alliance', 'deal'],
            'investment': ['funding', 'capital injection', 'backing'],
            'regulation': ['rules', 'oversight', 'compliance'],
            'adoption': ['acceptance', 'integration', 'implementation'],
            'market': ['trading', 'exchange', 'marketplace'],
            'significant': ['major', 'important', 'key', 'crucial'],
            'development': ['advancement', 'progress', 'breakthrough'],
            'launch': ['debut', 'release', 'rollout'],
            'platform': ['network', 'ecosystem', 'infrastructure']
        }
        
        # Action words to make tweets more engaging
        self.action_starters = [
            "🚨 Breaking:", "⚡ Alert:", "📈 Update:", "💎 News:",
            "🔥 Hot:", "⭐ Latest:", "📢 Announcement:", "🎯 Focus:",
            "💥 Big move:", "🌟 Spotlight:", "📊 Market update:",
            "🚀 Major news:", "💰 Financial update:", "🔔 Notice:"
        ]
        
        # Engaging endings
        self.engaging_endings = [
            "Thoughts?", "What do you think?", "Big news!", "Stay tuned!",
            "More to come!", "Bullish or bearish?", "Game changer?",
            "This could be huge!", "Exciting times!", "Keep watching!",
            "To the moon? 🚀", "WAGMI! 💎", "LFG! 🔥"
        ]
    
    def rewrite_headline(self, original_title: str, original_summary: str = "") -> str:
        """
        Rewrite a news headline into an engaging tweet format.
        
        Args:
            original_title: Original news headline
            original_summary: Optional summary for context
            
        Returns:
            Rewritten tweet text (without hashtags/mentions)
        """
        try:
            # Clean and normalize the input
            title = self._clean_text(original_title)
            
            # Apply rewriting techniques
            rewritten = self._apply_rewriting_rules(title)
            
            # Add engaging elements
            final_tweet = self._make_engaging(rewritten)
            
            # Ensure it meets length requirements
            final_tweet = self._ensure_length_limits(final_tweet)
            
            logger.info(f"Rewritten: '{original_title}' -> '{final_tweet}'")
            return final_tweet
            
        except Exception as e:
            logger.error(f"Error rewriting headline: {e}")
            # Fallback: return cleaned original title
            return self._clean_text(original_title)[:200]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common prefixes from news sites
        prefixes_to_remove = [
            'Breaking:', 'BREAKING:', 'Update:', 'UPDATE:', 'News:', 'NEWS:',
            'Exclusive:', 'EXCLUSIVE:', 'Alert:', 'ALERT:', 'Analysis:',
            'Opinion:', 'Editorial:', 'Report:', 'REPORT:'
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
    
    def _apply_rewriting_rules(self, text: str) -> str:
        """Apply synonym replacement and structural changes."""
        words = text.split()
        rewritten_words = []
        
        for word in words:
            # Clean word (remove punctuation for matching)
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            # Check for synonyms
            replacement = word
            for key, synonyms in self.synonyms.items():
                if clean_word == key:
                    replacement = random.choice(synonyms)
                    # Preserve capitalization pattern
                    if word[0].isupper():
                        replacement = replacement.capitalize()
                    break
            
            rewritten_words.append(replacement)
        
        rewritten_text = ' '.join(rewritten_words)
        
        # Apply structural changes
        rewritten_text = self._apply_structural_changes(rewritten_text)
        
        return rewritten_text
    
    def _apply_structural_changes(self, text: str) -> str:
        """Apply structural changes to make text more tweet-friendly."""
        
        # Convert passive to active voice (simple patterns)
        text = re.sub(r'is expected to', 'will likely', text, flags=re.IGNORECASE)
        text = re.sub(r'are expected to', 'will likely', text, flags=re.IGNORECASE)
        text = re.sub(r'has been', 'got', text, flags=re.IGNORECASE)
        text = re.sub(r'have been', 'got', text, flags=re.IGNORECASE)
        
        # Simplify complex phrases
        replacements = {
            'in order to': 'to',
            'despite the fact that': 'despite',
            'due to the fact that': 'because',
            'for the reason that': 'because',
            'at this point in time': 'now',
            'with regard to': 'about',
            'in the event that': 'if',
            'as a result of': 'from',
        }
        
        for old_phrase, new_phrase in replacements.items():
            text = re.sub(old_phrase, new_phrase, text, flags=re.IGNORECASE)
        
        return text
    
    def _make_engaging(self, text: str) -> str:
        """Add engaging elements to make the tweet more compelling."""
        
        # Sometimes add an action starter (30% chance)
        if random.random() < 0.3:
            starter = random.choice(self.action_starters)
            text = f"{starter} {text}"
        
        # Sometimes add an engaging ending (40% chance)
        if random.random() < 0.4:
            ending = random.choice(self.engaging_endings)
            text = f"{text} {ending}"
        
        return text
    
    def _ensure_length_limits(self, text: str) -> str:
        """Ensure tweet meets length requirements."""
        words = text.split()
        
        # First check word count
        if len(words) > CONTENT_SETTINGS['max_words']:
            words = words[:CONTENT_SETTINGS['max_words']]
            text = ' '.join(words)
        
        # Then check character count (reserve space for hashtags and mentions)
        reserved_chars = 50  # Space for hashtags and mentions
        max_content_chars = CONTENT_SETTINGS['max_tweet_length'] - reserved_chars
        
        if len(text) > max_content_chars:
            # Truncate at word boundary
            words = text.split()
            truncated = ""
            for word in words:
                if len(truncated + " " + word) <= max_content_chars - 3:  # -3 for "..."
                    truncated += (" " if truncated else "") + word
                else:
                    break
            text = truncated + "..."
        
        return text
    
    def add_hashtags_and_mentions(self, tweet_text: str) -> str:
        """Add hashtags and mentions to the tweet."""
        
        # Select random hashtags
        num_hashtags = CONTENT_SETTINGS['hashtags_per_tweet']
        selected_hashtags = random.sample(CRYPTO_HASHTAGS, 
                                        min(num_hashtags, len(CRYPTO_HASHTAGS)))
        
        # Select random mention if enabled
        mention = ""
        if CONTENT_SETTINGS['include_mentions'] and CRYPTO_ACCOUNTS:
            mention = random.choice(CRYPTO_ACCOUNTS)
        
        # Combine everything
        hashtags_str = " ".join(selected_hashtags)
        
        if mention:
            final_tweet = f"{tweet_text} {mention} {hashtags_str}"
        else:
            final_tweet = f"{tweet_text} {hashtags_str}"
        
        # Final length check
        if len(final_tweet) > CONTENT_SETTINGS['max_tweet_length']:
            # Remove hashtags one by one until it fits
            while len(final_tweet) > CONTENT_SETTINGS['max_tweet_length'] and selected_hashtags:
                selected_hashtags.pop()
                hashtags_str = " ".join(selected_hashtags)
                if mention:
                    final_tweet = f"{tweet_text} {mention} {hashtags_str}"
                else:
                    final_tweet = f"{tweet_text} {hashtags_str}"
        
        return final_tweet.strip()
    
    def create_complete_tweet(self, title: str, summary: str = "", url: str = "") -> str:
        """
        Create a complete tweet from news content.
        
        Args:
            title: News headline
            summary: Optional summary
            url: Optional URL (will be auto-shortened by Twitter)
            
        Returns:
            Complete tweet text ready for posting
        """
        # Rewrite the content
        rewritten_content = self.rewrite_headline(title, summary)
        
        # Add hashtags and mentions
        tweet_with_tags = self.add_hashtags_and_mentions(rewritten_content)
        
        # Add URL if provided and space allows
        if url and len(tweet_with_tags) + len(url) + 1 <= CONTENT_SETTINGS['max_tweet_length']:
            tweet_with_tags += f" {url}"
        
        return tweet_with_tags

def test_rewriter():
    """Test the rewriter with sample headlines."""
    rewriter = TweetRewriter()
    
    test_headlines = [
        "Bitcoin Price Reaches New All-Time High of $75,000 Amid Institutional Investment",
        "Ethereum Network Successfully Completes Major Upgrade, Reducing Gas Fees by 40%",
        "SEC Announces New Cryptocurrency Regulations Expected to Impact Trading Platforms",
        "Major Bank Partners with Blockchain Company to Launch Digital Currency Initiative",
        "Crypto Market Experiences Significant Volatility Following Federal Reserve Announcement"
    ]
    
    print("Testing tweet rewriter...")
    for i, headline in enumerate(test_headlines, 1):
        rewritten = rewriter.create_complete_tweet(headline)
        print(f"\n{i}. Original: {headline}")
        print(f"   Rewritten: {rewritten}")
        print(f"   Length: {len(rewritten)} characters")

if __name__ == "__main__":
    test_rewriter()
