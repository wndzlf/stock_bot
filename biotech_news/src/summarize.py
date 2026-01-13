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
    너는 최첨단 바이오테크 및 생명공학 기술의 핵심을 꿰뚫어 보는 기술 분석 전문 AI야. 
    전문가와 기술 관심층이 정보를 한눈에 파악할 수 있도록 핵심 성과와 그 임팩트 위주로 매우 임팩트 있게 작성해줘.

    주제: {news_text}

    필수 룰 – 절대 어기지 마:
    - 첫 문장은 **전체 볼드**로 핵심 기술/성과를 강하게 시작 (Unicode Mathematical Bold 사용: 𝗕𝗢𝗟𝗗 𝗧𝗘𝗫𝗧 이런 식으로 써. 예: **𝗔𝗜를 활용한 난치병 치료제 설계 성공**)
    - 중요한 메커니즘/수치/핵심 단어는 *이탤릭*으로 강조 (Unicode Mathematical Italic: *𝑖𝑡𝑎𝑙𝑖𝑐 𝑡𝑒𝑥𝑡* 이런 식. 예: *99% 정확도 달성*)
    - 불필요한 서술은 제외하고 핵심 결과와 향후 기대 효과 위주로 구성.
    - 이모지 2~4개 적절히 사용 (🧬 🔬 🚀 🧪 등)
    - 마지막에 기술적 질문이나 시장의 변화를 묻는 진지한 질문 넣기 (예: "이 기술이 상용화되면 기존 시장의 판도는 어떻게 바뀔까?")
    - 해시태그 3~5개 (예: #바이오테크 #신약개발 #기술혁신 #Biotech #FutureMedicine)
    - **출처 무조건 포함**: 포스팅 맨 끝에 "출처: [간단한 출처 이름 + 년월 or URL 짧게]" 형식으로 넣어.
    - 전체 길이 280자 이내 (최적 180~230자).
    - 말투는 전문적이고 단호하게 (Slang이나 가벼운 표현 금지).
    - 출력은 **완성된 포스팅 텍스트만** 줘. 설명이나 ``` 같은 거 붙이지 말고 바로 복붙 가능한 텍스트로.
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
