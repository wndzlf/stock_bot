import os
from google import genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_biotech_news(news_items: list) -> str:
    """
    바이오테크 기술 뉴스를 Gemini를 사용하여 X(트위터) 포스팅용으로 요약합니다.
    
    Args:
        news_items (list): 뉴스 항목 리스트 (title, summary, link, publisher).
        
    Returns:
        str: 생성된 트윗 내용.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("환경 변수에서 GEMINI_API_KEY를 찾을 수 없습니다.")
        return "오류: API 키가 없습니다."

    if not news_items:
        return "오늘의 주요 바이오테크 기술 뉴스가 없습니다."

    # Prepare the input text
    news_text = ""
    for idx, item in enumerate(news_items[:3]): # 상위 3개 뉴스만 사용
        news_text += f"{idx+1}. 제목: {item['title']}\n내용 요약: {item['summary']}\n출처: {item['publisher']}\n\n"

    prompt = f"""
    당신은 최첨단 바이오테크 및 생명공학 기술에 정통한 전문 기술 분석가입니다.
    다음의 최신 바이오테크 기술 뉴스들을 한국의 기술 관심층과 투자자들을 위해 핵심 요약하여 X(트위터) 포스팅용으로 작성해주세요.

    요구사항:
    1. 핵심 기술 요약: 복잡한 기술적 내용을 일반인도 이해하기 쉽지만 전문성을 잃지 않게 핵심만 짚어주세요.
    2. 톤: 혁신적이고 정보 중심적인 톤 (Professional & Insightful).
    3. 구조:
       - 🚀 오늘의 바이오테크 기술 혁신 (임팩트 있는 헤드라인)
       - 기술별 핵심 포인트 (불렛 포인트 사용, 최대 3개)
       - 왜 중요한지에 대한 짧은 통찰
    4. 출처 표기: 각 뉴스별 출처를 포함하세요 (예: 출처: Nature Biotechnology).
    5. 길이: X 포스팅 길이에 맞게 간결하게 (약 200자 내외).
    6. 해시태그: #바이오테크 #Biotech #기술혁신 #생명공학 #Nature

    뉴스 데이터:
    {news_text}
    """
    
    try:
        # Initialize Client with the new SDK
        client = genai.Client(api_key=api_key)
        
        # Call the model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"요약 생성 오류: {e}")
        return f"Error generating summary: {e}"

if __name__ == "__main__":
    # 테스트용 스텁
    mock_news = [
        {
            'title': 'CRISPR-based gene editing for heart disease',
            'summary': 'A new study shows successful long-term results in clinical trials.',
            'publisher': 'Nature Biotechnology'
        }
    ]
    # print(summarize_biotech_news(mock_news))
