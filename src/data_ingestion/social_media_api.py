"""
Social media API integration for data collection.
Handles Twitter, Facebook, Instagram, and TikTok data ingestion.
"""

import tweepy
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Generator
from dataclasses import dataclass
from src.utils.logger import get_logger, log_api_request
from src.utils.config import get_config
import pandas as pd

logger = get_logger(__name__)


@dataclass
class SocialMediaPost:
    """Data class for social media posts."""
    platform: str
    post_id: str
    user_id: str
    username: str
    content: str
    created_at: datetime
    metadata: Dict[str, Any]


class TwitterAPI:
    """Twitter API integration for data collection."""
    
    def __init__(self):
        config = get_config()
        api_config = config.get_api_config()
        
        # Initialize Twitter API v2
        self.client = tweepy.Client(
            bearer_token=api_config["twitter_bearer_token"],
            consumer_key=api_config["twitter_api_key"],
            consumer_secret=api_config["twitter_api_secret"],
            access_token=api_config["twitter_access_token"],
            access_token_secret=api_config["twitter_access_token_secret"],
            wait_on_rate_limit=True
        )
        
        # Rate limiting
        self.rate_limit_remaining = 300
        self.rate_limit_reset = None
    
    def search_tweets(self, 
                     query: str, 
                     max_results: int = 100,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> List[SocialMediaPost]:
        """Search for tweets based on query."""
        try:
            start_time_str = start_time.isoformat() if start_time else None
            end_time_str = end_time.isoformat() if end_time else None
            
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time_str,
                end_time=end_time_str,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'verified'],
                expansions=['author_id']
            )
            
            posts = []
            if response.data:
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for tweet in response.data:
                    user = users.get(tweet.author_id)
                    post = SocialMediaPost(
                        platform="twitter",
                        post_id=tweet.id,
                        user_id=tweet.author_id,
                        username=user.username if user else "unknown",
                        content=tweet.text,
                        created_at=tweet.created_at,
                        metadata={
                            "public_metrics": tweet.public_metrics,
                            "context_annotations": tweet.context_annotations,
                            "verified": user.verified if user else False
                        }
                    )
                    posts.append(post)
            
            # Log API request
            log_api_request(
                endpoint="/2/tweets/search/recent",
                method="GET",
                status_code=200,
                response_time=0.1
            )
            
            logger.info(f"Collected {len(posts)} tweets for query: {query}")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            log_api_request(
                endpoint="/2/tweets/search/recent",
                method="GET",
                status_code=500,
                response_time=0.1
            )
            return []
    
    def get_user_tweets(self, 
                       username: str, 
                       max_results: int = 100) -> List[SocialMediaPost]:
        """Get tweets from a specific user."""
        try:
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"User {username} not found")
                return []
            
            response = self.client.get_users_tweets(
                id=user.data.id,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            posts = []
            if response.data:
                for tweet in response.data:
                    post = SocialMediaPost(
                        platform="twitter",
                        post_id=tweet.id,
                        user_id=user.data.id,
                        username=username,
                        content=tweet.text,
                        created_at=tweet.created_at,
                        metadata={
                            "public_metrics": tweet.public_metrics,
                            "context_annotations": tweet.context_annotations
                        }
                    )
                    posts.append(post)
            
            logger.info(f"Collected {len(posts)} tweets from user: {username}")
            return posts
            
        except Exception as e:
            logger.error(f"Error getting user tweets for {username}: {e}")
            return []


class FacebookAPI:
    """Facebook Graph API integration for data collection."""
    
    def __init__(self):
        config = get_config()
        api_config = config.get_api_config()
        
        self.app_id = api_config["facebook_app_id"]
        self.app_secret = api_config["facebook_app_secret"]
        self.access_token = self._get_access_token()
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def _get_access_token(self) -> str:
        """Get Facebook access token."""
        try:
            url = f"{self.base_url}/oauth/access_token"
            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "client_credentials"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data["access_token"]
            
        except Exception as e:
            logger.error(f"Error getting Facebook access token: {e}")
            return ""
    
    def search_posts(self, 
                    query: str, 
                    limit: int = 100) -> List[SocialMediaPost]:
        """Search for Facebook posts."""
        try:
            url = f"{self.base_url}/search"
            params = {
                "q": query,
                "type": "post",
                "limit": min(limit, 100),
                "access_token": self.access_token,
                "fields": "id,message,created_time,from"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for post_data in data.get("data", []):
                post = SocialMediaPost(
                    platform="facebook",
                    post_id=post_data["id"],
                    user_id=post_data.get("from", {}).get("id", ""),
                    username=post_data.get("from", {}).get("name", ""),
                    content=post_data.get("message", ""),
                    created_at=datetime.fromisoformat(post_data["created_time"].replace("Z", "+00:00")),
                    metadata={"from": post_data.get("from", {})}
                )
                posts.append(post)
            
            logger.info(f"Collected {len(posts)} Facebook posts for query: {query}")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching Facebook posts: {e}")
            return []


class InstagramAPI:
    """Instagram Basic Display API integration."""
    
    def __init__(self):
        config = get_config()
        api_config = config.get_api_config()
        
        self.access_token = api_config["instagram_access_token"]
        self.base_url = "https://graph.instagram.com"
    
    def get_user_media(self, 
                      user_id: str = "me", 
                      limit: int = 100) -> List[SocialMediaPost]:
        """Get Instagram media from a user."""
        try:
            url = f"{self.base_url}/{user_id}/media"
            params = {
                "access_token": self.access_token,
                "fields": "id,caption,media_type,media_url,permalink,timestamp",
                "limit": min(limit, 100)
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for media_data in data.get("data", []):
                post = SocialMediaPost(
                    platform="instagram",
                    post_id=media_data["id"],
                    user_id=user_id,
                    username="instagram_user",
                    content=media_data.get("caption", ""),
                    created_at=datetime.fromisoformat(media_data["timestamp"].replace("Z", "+00:00")),
                    metadata={
                        "media_type": media_data.get("media_type"),
                        "media_url": media_data.get("media_url"),
                        "permalink": media_data.get("permalink")
                    }
                )
                posts.append(post)
            
            logger.info(f"Collected {len(posts)} Instagram posts from user: {user_id}")
            return posts
            
        except Exception as e:
            logger.error(f"Error getting Instagram media: {e}")
            return []


class TikTokAPI:
    """TikTok Research API integration (simulated)."""
    
    def __init__(self):
        # Note: TikTok Research API requires special approval
        # This is a simulated implementation
        self.base_url = "https://open.tiktokapis.com/v2"
        self.access_token = "simulated_token"
    
    def search_videos(self, 
                     query: str, 
                     limit: int = 100) -> List[SocialMediaPost]:
        """Search for TikTok videos (simulated)."""
        try:
            # Simulated response for demonstration
            posts = []
            
            # In a real implementation, this would make API calls to TikTok
            logger.info(f"Simulated collection of {limit} TikTok videos for query: {query}")
            
            return posts
            
        except Exception as e:
            logger.error(f"Error searching TikTok videos: {e}")
            return []


class SocialMediaCollector:
    """Main social media data collector."""
    
    def __init__(self):
        self.twitter = TwitterAPI()
        self.facebook = FacebookAPI()
        self.instagram = InstagramAPI()
        self.tiktok = TikTokAPI()
    
    def collect_hate_speech_data(self, 
                                keywords: List[str],
                                platforms: List[str] = None,
                                max_posts_per_platform: int = 1000,
                                time_range_days: int = 7) -> List[SocialMediaPost]:
        """Collect hate speech data from multiple platforms."""
        
        if platforms is None:
            platforms = ["twitter", "facebook", "instagram", "tiktok"]
        
        all_posts = []
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=time_range_days)
        
        for platform in platforms:
            logger.info(f"Collecting data from {platform}")
            
            try:
                if platform == "twitter":
                    posts = self._collect_twitter_data(keywords, max_posts_per_platform, start_time, end_time)
                elif platform == "facebook":
                    posts = self._collect_facebook_data(keywords, max_posts_per_platform)
                elif platform == "instagram":
                    posts = self._collect_instagram_data(max_posts_per_platform)
                elif platform == "tiktok":
                    posts = self._collect_tiktok_data(keywords, max_posts_per_platform)
                else:
                    logger.warning(f"Unsupported platform: {platform}")
                    continue
                
                all_posts.extend(posts)
                logger.info(f"Collected {len(posts)} posts from {platform}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting data from {platform}: {e}")
                continue
        
        logger.info(f"Total collected posts: {len(all_posts)}")
        return all_posts
    
    def _collect_twitter_data(self, 
                             keywords: List[str], 
                             max_posts: int,
                             start_time: datetime,
                             end_time: datetime) -> List[SocialMediaPost]:
        """Collect Twitter data."""
        posts = []
        posts_per_keyword = max_posts // len(keywords)
        
        for keyword in keywords:
            query = f"{keyword} lang:it"  # Italian language filter
            keyword_posts = self.twitter.search_tweets(
                query=query,
                max_results=posts_per_keyword,
                start_time=start_time,
                end_time=end_time
            )
            posts.extend(keyword_posts)
        
        return posts
    
    def _collect_facebook_data(self, 
                              keywords: List[str], 
                              max_posts: int) -> List[SocialMediaPost]:
        """Collect Facebook data."""
        posts = []
        posts_per_keyword = max_posts // len(keywords)
        
        for keyword in keywords:
            keyword_posts = self.facebook.search_posts(
                query=keyword,
                limit=posts_per_keyword
            )
            posts.extend(keyword_posts)
        
        return posts
    
    def _collect_instagram_data(self, max_posts: int) -> List[SocialMediaPost]:
        """Collect Instagram data."""
        return self.instagram.get_user_media(limit=max_posts)
    
    def _collect_tiktok_data(self, 
                            keywords: List[str], 
                            max_posts: int) -> List[SocialMediaPost]:
        """Collect TikTok data."""
        posts = []
        posts_per_keyword = max_posts // len(keywords)
        
        for keyword in keywords:
            keyword_posts = self.tiktok.search_videos(
                query=keyword,
                limit=posts_per_keyword
            )
            posts.extend(keyword_posts)
        
        return posts
    
    def save_to_database(self, posts: List[SocialMediaPost]):
        """Save collected posts to database."""
        try:
            from src.database.db_connector import DatabaseConnector
            
            db = DatabaseConnector()
            session = db.get_session()
            
            saved_count = 0
            for post in posts:
                try:
                    # Convert to database model
                    from src.database.schema_manager import SocialMediaPost as DBPost
                    
                    db_post = DBPost(
                        platform=post.platform,
                        post_id=post.post_id,
                        user_id=post.user_id,
                        username=post.username,
                        content=post.content,
                        created_at=post.created_at,
                        metadata=post.metadata
                    )
                    
                    session.add(db_post)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving post {post.post_id}: {e}")
                    continue
            
            session.commit()
            session.close()
            
            logger.info(f"Saved {saved_count} posts to database")
            
        except Exception as e:
            logger.error(f"Error saving posts to database: {e}")
    
    def export_to_csv(self, posts: List[SocialMediaPost], filename: str):
        """Export posts to CSV file."""
        try:
            data = []
            for post in posts:
                data.append({
                    "platform": post.platform,
                    "post_id": post.post_id,
                    "user_id": post.user_id,
                    "username": post.username,
                    "content": post.content,
                    "created_at": post.created_at.isoformat(),
                    "metadata": json.dumps(post.metadata)
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            
            logger.info(f"Exported {len(posts)} posts to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")


if __name__ == "__main__":
    # Test social media collection
    collector = SocialMediaCollector()
    
    # Define hate speech keywords
    keywords = [
        "ebrei", "islam", "migrazione", "genere", "omosessualità", "disabilità",
        "antisemitismo", "islamofobia", "xenofobia", "misoginia", "omofobia"
    ]
    
    # Collect data
    posts = collector.collect_hate_speech_data(
        keywords=keywords,
        platforms=["twitter", "facebook"],
        max_posts_per_platform=100,
        time_range_days=1
    )
    
    # Export to CSV
    collector.export_to_csv(posts, "data/raw/social_media/collected_posts.csv")
    
    print(f"Collected {len(posts)} posts")
