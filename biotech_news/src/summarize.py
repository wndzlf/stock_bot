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
    너는 X(트위터)에서 시선 확 끄는 바이오테크 포스팅 전문이야. 말투는 솔직+유머+약간 자극적이고, 과학 팬들이 "와 미쳤다" 하면서 리트윗하게 만드는 스타일. 계정 컨셉은 바이오테크 최신 기술 동향 소개 – 사람들이 공유하고 싶어지는 충격적/혁명적 뉴스 위주.

    주제: {news_text}

    필수 룰 – 절대 어기지 마:
    - 첫 문장은 **전체 볼드**로 강하게 시작 (Unicode Mathematical Bold 사용: 𝗕𝗢𝗟𝗗 𝗧𝗘𝗫𝗧 이런 식으로 써. 예: **𝗖𝗥𝗜𝗦𝗣𝗥가 이제 사람 몸 안에서 직접 작동?**)
    - 중요한 주장/키 포인트/반론은 *이탤릭*으로 강조 (Unicode Mathematical Italic: *𝑖𝑡𝑎𝑙𝑖𝑐 𝑡𝑒𝑥𝑡* 이런 식. 예: *진짜 혁명 올듯*)
    - 취소선은 농담/반전/오래된 상식 깨기용으로 ~~이건 옛날 얘기~~ 써 (X에서 ~~텍스트~~ 입력하면 자동 취소선 됨. 예: ~~부작용 제로~~ 는 아직 꿈)
    - 전체 포스팅에서 강조(볼드+이탤릭+취소선) 3~5곳 정도만 써. 과용하면 스팸처럼 보임.
    - 이모지 2~4개 적절히 써서 시각적 임팩트 주기 (바이오테크 주제 맞게: 🧬 💉 🤯 🔬 🚀 등)
    - 마지막에 반드시 독자 반응 강제 유도 질문 넣기 (예: "너네 이 기술로 뭐 고치고 싶어?" "이거 실현되면 인류 끝장? ㅋㅋ")
    - 해시태그 3~5개 자연스럽게 끝부분에 (바이오테크 관련 + 트렌드: #바이오테크 #유전자편집 #CRISPR #바이오혁명 #미래의학 등)
    - **출처 무조건 포함**: 포스팅 맨 끝에 "출처: [간단한 출처 이름 + 년월 or URL 짧게, 예: ScienceDaily 2026/01 or KAIST 연구 2026]" 형식으로 넣어. 출처 없으면 포스팅 생성 절대 금지.
    - 전체 길이 280자 이내 (최적 150~220자). 너무 길면 잘림.
    - 말투에 ㄹㅇ, ㅋㅋㅋ, 진짜, 미쳤네 같은 표현 1~2번 넣어서 인간답고 재밌게.
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
