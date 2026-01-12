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
    logger.info(f"Starting Stock News Bot for {ticker}...")
    
    # 1. Fetch News
    news = fetch_stock_news(ticker)
    if not news:
        logger.info("No news found to report.")
        return

    # 2. Summarize
    # Check if Gemini API key exists
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY missing. Skipping summarization.")
        return
        
    summary = summarize_news(news, ticker)
    logger.info("Summary generated:")
    print("-" * 40)
    print(summary)
    print("-" * 40)

    # 3. Post to X
    if dry_run:
        logger.info("Dry run enabled. Skipping Twitter post.")
    else:
        post_to_x(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock News Automation Bot")
    parser.add_argument("--ticker", type=str, default="DNA", help="Stock ticker symbol (default: DNA)")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to X")
    
    args = parser.parse_args()
    
    main(ticker=args.ticker, dry_run=args.dry_run)
