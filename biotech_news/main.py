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
        
        # 뉴스 텍스트 생성
        news_list_text = ""
        for i, item in enumerate(news[:5]): # 상위 5개만
            title = html.escape(item['title'])
            link = html.escape(item['link'])
            news_list_text += f"{i+1}. {title}\nLink: {link}\n\n"
        
        # 프롬프트 템플릿 (summarize.py에서 가져옴)
        prompt_template = f"""
----------------------------------------
[AI 프롬프트 시작]

너는 최첨단 바이오테크 및 생명공학 기술의 핵심을 꿰뚫어 보는 기술 분석 전문 AI야. 
전문가와 기술 관심층이 정보를 한눈에 파악할 수 있도록 핵심 성과와 그 임팩트 위주로 매우 임팩트 있게 작성해줘.

주제:
{news_list_text}

필수 룰 – 절대 어기지 마:
- 첫 문장은 볼드 효과를 주어 강하게 헤드라인으로 시작 (Unicode Sans-serif Bold 사용: 𝗕𝗢𝗟𝗗 𝗧𝗘𝗫𝗧 이런 식으로 써)
- 본문(헤드라인 제외)에는 특수 스타일(이탤릭, 볼드 등)을 적용하지 말고 일반 텍스트를 사용해.
- 가독성을 위해 문장 사이에 엔터(줄바꿈)를 적절히 쳐서 한 눈에 들어오게 해.
- 모든 마크다운 기호를 절대 쓰지 마. X(트위터)용이므로 오직 텍스트와 허용된 Unicode 변환 문자만 사용해야 함.
- 불필요한 서술은 제외하고 핵심 결과와 향후 기대 효과 위주로 매우 간결하게 구성.
- 이모지 1~2개 적절히 사용 (🧬 🚀 등).
- 바이오 테크에 관심없는 대중들에게 어떤 의미를 가지는지 마지막에 한두문장으로 설명.
- 해시태그 3개 내외 (예: #바이오테크)
- 출처 무조건 포함: 포스팅 맨 끝에 "출처: [매체명 + 연월]" 형식으로 넣어.
- 전체 길이 280자 이내 (최적 160~200자).
- 말투는 전문적이고 단호하게.
- 답변은 반드시 한국어로 작성해줘.
- 완성된 포스팅 텍스트만 출력해.

[AI 프롬프트 끝]
----------------------------------------
위 내용을 전체 복사하여 GPT나 Claude 등에 넣고 답변을 받으세요. 
그 후 받은 답변을 이 봇에게 다시 보내주시면 X에 포스팅됩니다!
"""
        send_to_telegram(prompt_template)
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
