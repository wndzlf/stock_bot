import tweepy
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def post_to_x(content: str):
    """
    Posts a tweet to X using Tweepy (API v2).
    
    Args:
        content (str): The text to tweet.
    """
    # Load credentials
    consumer_key = os.getenv("X_CONSUMER_KEY")
    consumer_secret = os.getenv("X_CONSUMER_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("X_BEARER_TOKEN")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        logger.error("X API 인증 정보가 없습니다. X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET을 설정해주세요.")
        return

    try:
        # Client for API v2
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Split logic if content is too long (basic chunking)
        # Note: X Blue allows longer tweets, but free tier is 280 chars unless configured.
        # For now, we assume the summary fits or we let it fail if too long to warn the user.
        # A simple check:
        if len(content) > 280:
             logger.warning("내용이 280자를 초과합니다. 프리미엄이 아닌 경우 실패할 수 있습니다.")
        
        response = client.create_tweet(text=content)
        logger.info(f"트윗 포스팅 성공! ID: {response.data['id']}")
        
    except tweepy.TweepyException as e:
        logger.error(f"트윗 포스팅 오류: {e}")

if __name__ == "__main__":
    # Test stub
    logger.info("Test run...")
    # post_to_x("This is a test tweet from my automated bot. #Python")
