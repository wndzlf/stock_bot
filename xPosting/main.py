import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.post_tweet import post_to_x
from xPosting.src.fetch_tweets import fetch_ginkgo_tweets
from xPosting.src.fetch_blog_rss import fetch_ginkgo_blog
from xPosting.src.translate_tweets import translate_and_comment

# Load environment variables from .env file for local development
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(dry_run: bool = False):
    logger.info("깅코바이오웍스 X 큐레이션 봇을 시작합니다...")
    
    # 1. Try fetching tweets from experts first
    content_source = "tweets"
    tweets = fetch_ginkgo_tweets(lookback_hours=24)
    
    # 2. Fallback to Ginkgo blog RSS if X API fails
    if not tweets:
        logger.info("X API에서 트윗을 가져올 수 없습니다. Ginkgo 블로그 RSS로 전환합니다...")
        content_source = "blog"
        tweets = fetch_ginkgo_blog(lookback_hours=168)  # 7 days
    
    if not tweets:
        logger.info("보고할 콘텐츠가 없습니다.")
        return

    # 3. Translate and add commentary
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY가 없습니다. 번역을 건너뜁니다.")
        return
        
    content = translate_and_comment(tweets, content_type=content_source)
    logger.info("번역 및 해설 생성 완료:")
    print("-" * 40)
    print(content)
    print("-" * 40)

    if content.startswith("Error"):
        logger.error("번역 생성 실패. 트위터 포스팅을 건너뜁니다.")
        return

    # 3. Post to X
    if dry_run:
        logger.info("테스트 모드 활성화. 트위터 포스팅을 건너뜁니다.")
    else:
        post_to_x(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ginkgo Bioworks X Curation Bot")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to X")
    
    args = parser.parse_args()
    
    main(dry_run=args.dry_run)
