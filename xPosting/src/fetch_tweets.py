import os
import tweepy
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Target biotech expert accounts
EXPERT_ACCOUNTS = [
    "jasonjkelly",      # Ginkgo CEO
    "andrewhessel",     # Humane Genomics
    "robcarlson",       # Bioeconomy Capital
    "ARKInvest",        # Cathie Wood
    "FierceBiotech",    # Biotech news
]

def fetch_ginkgo_tweets(lookback_hours: int = 24) -> list:
    """
    Fetch tweets from biotech experts mentioning Ginkgo Bioworks.
    
    Args:
        lookback_hours (int): How many hours back to search (default: 24).
        
    Returns:
        list: List of tweet dictionaries with text, author, timestamp, url.
    """
    consumer_key = os.getenv("X_CONSUMER_KEY")
    consumer_secret = os.getenv("X_CONSUMER_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("X_BEARER_TOKEN")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        logger.error("X API 인증 정보가 없습니다.")
        return []

    try:
        # Initialize Tweepy client
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Build search query
        # Search for Ginkgo-related keywords from expert accounts
        # Note: $DNA (cashtag) not supported in Basic tier
        keywords = "(Ginkgo OR \"Ginkgo Bioworks\" OR DNA OR synbio)"
        accounts_query = " OR ".join([f"from:{acc}" for acc in EXPERT_ACCOUNTS])
        query = f"{keywords} ({accounts_query}) -is:retweet"
        
        # Calculate time range
        start_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        logger.info(f"X 검색 중: {query}")
        
        # Search tweets
        response = client.search_recent_tweets(
            query=query,
            start_time=start_time,
            max_results=10,
            tweet_fields=['created_at', 'author_id', 'public_metrics'],
            expansions=['author_id'],
            user_fields=['username', 'name']
        )
        
        if not response.data:
            logger.info("Ginkgo 관련 트윗을 찾을 수 없습니다.")
            return []
        
        # Process tweets
        tweets = []
        users_dict = {user.id: user for user in response.includes['users']}
        
        for tweet in response.data:
            author = users_dict.get(tweet.author_id)
            tweets.append({
                'text': tweet.text,
                'author': f"@{author.username}" if author else "Unknown",
                'author_name': author.name if author else "Unknown",
                'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'url': f"https://twitter.com/{author.username}/status/{tweet.id}" if author else "",
                'likes': tweet.public_metrics['like_count'],
                'retweets': tweet.public_metrics['retweet_count']
            })
        
        # Sort by engagement (likes + retweets)
        tweets.sort(key=lambda x: x['likes'] + x['retweets'], reverse=True)
        
        logger.info(f"최근 {lookback_hours}시간 내 Ginkgo 관련 트윗 {len(tweets)}개를 찾았습니다.")
        return tweets[:3]  # Return top 3 most engaging tweets
        
    except Exception as e:
        logger.error(f"트윗 가져오기 오류: {e}")
        return []

if __name__ == "__main__":
    # Test
    tweets = fetch_ginkgo_tweets()
    for tweet in tweets:
        print(f"{tweet['author']}: {tweet['text'][:100]}...")
