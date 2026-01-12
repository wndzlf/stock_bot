import os
import argparse
import logging
from dotenv import load_dotenv

from src.fetch_news import fetch_stock_news
from src.summarize import summarize_news
from src.post_tweet import post_to_x

# Load environment variables from .env file for local development
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(ticker: str, dry_run: bool = False):
    logger.info(f"{ticker} 주식 뉴스 봇을 시작합니다...")
    
    # 1. Fetch News
    news = fetch_stock_news(ticker)
    if not news:
        logger.info("보고할 뉴스가 없습니다.")
        return

    # 2. Summarize
    # Check if Gemini API key exists
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY가 없습니다. 요약을 건너뜁니다.")
        return
        
    summary = summarize_news(news, ticker)
    logger.info("요약 생성 완료:")
    print("-" * 40)
    print(summary)
    print("-" * 40)

    if summary.startswith("Error"):
        logger.error("요약 생성 실패. 트위터 포스팅을 건너뜁니다.")
        return

    # 3. Post to X
    if dry_run:
        logger.info("테스트 모드 활성화. 트위터 포스팅을 건너뜁니다.")
    else:
        post_to_x(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock News Automation Bot")
    parser.add_argument("--ticker", type=str, default="DNA", help="Stock ticker symbol (default: DNA)")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to X")
    
    args = parser.parse_args()
    
    main(ticker=args.ticker, dry_run=args.dry_run)
