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
    너는 어려운 바이오 기술을 초등학생도 이해할 수 있을 만큼 쉽게 풀어서 전달하면서도, 
    핵심 인사이트를 콕 짚어주는 '인간미 넘치는 기술 큐레이터'야. 
    딱딱한 AI 말투는 지양하고, 마치 지인에게 오늘의 놀라운 발견을 설명하듯 친근하면서도 날결하게 작성해줘.

    주제: {news_text}

    필수 룰 – 절대 어기지 마:
    - 첫 문장은 볼드 효과를 주어 강하게 헤드라인으로 시작 (Unicode Sans-serif Bold 사용: 𝗕𝗢𝗟𝗗 𝗧𝗘𝗫𝗧 이런 식으로 써)
    - **핵심: 어려운 전문 용어가 나오면 반드시 쉬운 비유나 설명을 덧붙여줘. (예: 아셈블로이드 -> 인공 미니 장기)**
    - **핵심: AI가 쓴 것 같은 상투적인 문구("여기 요약이 있습니다", "오늘의 뉴스입니다" 등)는 절대 쓰지 말고 바로 본론으로 들어가.**
    - 본문에는 일반 텍스트만 사용하고, 문장 사이 줄바꿈을 적절히 넣어 가독성을 높여줘.
    - 모든 마크다운 기호(별표 등)는 금지. 오직 텍스트와 Unicode 변환 문자만 사용.
    - 이모지는 내용과 어울리는 것으로 매번 다양하고 센스 있게 사용 (🧬, �, 🔬, 🧫, 🏥, ✨, 🎯, 🧪 등).
    - 이 기술이 우리의 실생활이나 건강에 어떤 구체적인 변화를 줄 수 있는지 반드시 언급해줘.
    - 해시태그 3개 내외 (예: #바이오테크 #혁신기술)
    - 출처 무조건 포함: 맨 끝에 "출처: [매체명 + 연월]" 형식.
    - 전체 길이 280자 이내.
    - 답변은 반드시 한국어로 작성해줘.
    - 완성된 포스팅 텍스트만 출력해.
    """
    
    try:
        # Initialize Client with the new SDK
        client = genai.Client(api_key=api_key)
        
        # Call the model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
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
