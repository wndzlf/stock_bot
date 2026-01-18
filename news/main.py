import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.post_tweet import post_to_x
from news.src.fetch_news import fetch_stock_news
from news.src.summarize import summarize_news
from src.telegram_bot import send_to_telegram

# Load environment variables from .env file for local development
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(ticker: str, dry_run: bool = False, hitl: bool = False):
    logger.info(f"{ticker} 주식 뉴스 봇을 시작합니다...")
    
    # 1. Fetch News
    news = fetch_stock_news(ticker)
    if not news:
        logger.info("보고할 뉴스가 없습니다.")
        return

    if hitl:
        logger.info("HITL 모드 활성화: 텔레그램으로 뉴스 원문을 전송합니다.")
        raw_text = f"<b>[{ticker} 주식 뉴스 원문]</b>\n\n"
        for i, item in enumerate(news[:5]):
            raw_text += f"{i+1}. {item['title']}\n"
            raw_text += f"Link: {item['link']}\n\n"
        
        raw_text += "위 내용을 복사하여 원하는 모델에서 요약본을 만든 후, 이 봇에게 답변으로 보내주세요."
        send_to_telegram(raw_text)
        logger.info("텔레그램 전송 완료. 프로그램을 종료합니다.")
        return

    # 2. Summarize (Auto Mode)
    # Check if Gemini API key exists
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY가 없습니다. 요약을 건너뜜니다.")
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
    parser.add_argument("--hitl", action="store_true", help="Human-In-The-Loop mode: Send raw news to Telegram")
    
    args = parser.parse_args()
    
    main(ticker=args.ticker, dry_run=args.dry_run, hitl=args.hitl)
