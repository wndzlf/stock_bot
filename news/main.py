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
import html

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
        
        # 뉴스 텍스트 생성
        news_list_text = ""
        for i, item in enumerate(news[:5]):
            title = html.escape(item['title'])
            link = html.escape(item['link'])
            news_list_text += f"{i+1}. {title}\nLink: {link}\n\n"
        
        # 프롬프트 템플릿 (summarize.py에서 가져옴)
        prompt_template = f"""
----------------------------------------
[AI 프롬프트 시작]

You are a professional stock market analyst writing for Korean retail investors.
Summarize the following recent news for '{ticker}' into a concise X (Twitter) post in Korean.

주제:
{news_list_text}

CRITICAL Requirements:
1. Company Name: ALWAYS use "깅코바이오웍스" (NOT 진코바이오웍스)
2. Source Attribution: At the end, ALWAYS add "출처: [언론사명]" for each major news item.
3. Currency & Financial Impact: Convert ALL USD amounts to KRW (1 USD = 1,450 KRW). Format: "약 X억원 (약 $Y million)". ALWAYS explain the financial impact.
4. Format: Catchy headline, 2-3 bullet points with investment insights. Focus on partnerships, financial results, products, regulatory news.
5. Tone: Professional but accessible for retail investors.
6. Length: STRICTLY under 10 lines.
7. Ending: Source attribution line, Hashtags: #{ticker} #깅코바이오웍스
8. 언어: 답변은 반드시 한국어(Korean)로 작성해줘.

[AI 프롬프트 끝]
----------------------------------------
위 내용을 전체 복사하여 GPT나 Claude 등에 넣고 답변을 받으세요. 
그 후 받은 답변을 이 봇에게 다시 보내주시면 X에 포스팅됩니다!
"""
        send_to_telegram(prompt_template)
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
