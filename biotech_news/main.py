import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.post_tweet import post_to_x
from biotech_news.src.fetch_biotech import fetch_biotech_news
from biotech_news.src.summarize import summarize_biotech_news
from src.telegram_bot import send_to_telegram
import html

# Load environment variables from .env file for local development
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(dry_run: bool = False, hitl: bool = False):
    logger.info("오늘의 바이오테크 기술 요약 봇을 시작합니다...")
    
    # 1. Fetch News (최근 24시간)
    news = fetch_biotech_news(lookback_hours=24)
    if not news:
        logger.info("최근 24시간 내에 보고할 뉴스가 없습니다. 48시간으로 범위를 확대합니다.")
        news = fetch_biotech_news(lookback_hours=48)
        
    if not news:
        logger.info("보고할 뉴스가 없습니다.")
        return

    if hitl:
        logger.info("HITL 모드 활성화: 텔레그램으로 뉴스 원문을 전송합니다.")
        raw_text = "<b>[바이오테크 뉴스 원문]</b>\n\n"
        for i, item in enumerate(news[:5]): # 상위 5개만
            title = html.escape(item['title'])
            link = html.escape(item['link'])
            raw_text += f"{i+1}. {title}\n"
            raw_text += f"Link: {link}\n\n"
        
        raw_text += "위 내용을 복사하여 원하는 모델에서 요약본을 만든 후, 이 봇에게 답변으로 보내주세요."
        send_to_telegram(raw_text)
        logger.info("텔레그램 전송 완료. 프로그램을 종료합니다.")
        return

    # 2. Summarize (Auto Mode with Gemini)
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY가 없습니다. 요약을 건너뜜니다.")
        return
        
    summary = summarize_biotech_news(news)
    logger.info("바이오테크 요약 생성 완료:")
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
    parser = argparse.ArgumentParser(description="Biotech Technology News Bot")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to X")
    parser.add_argument("--hitl", action="store_true", help="Human-In-The-Loop mode: Send raw news to Telegram")
    
    args = parser.parse_args()
    
    main(dry_run=args.dry_run, hitl=args.hitl)
