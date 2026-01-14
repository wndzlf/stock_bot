import os
from google import genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_and_comment(content_items: list, content_type: str = "tweets") -> str:
    """
    Translate content to Korean and add investment commentary.
    
    Args:
        content_items (list): List of tweet or blog post dictionaries.
        content_type (str): "tweets" or "blog"
        
    Returns:
        str: Korean translation with commentary for X post.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("환경 변수에서 GEMINI_API_KEY를 찾을 수 없습니다.")
        return "오류: API 키가 없습니다."

    if not content_items:
        return "오늘 깅코바이오웍스 관련 콘텐츠가 없습니다."

    # Prepare content text based on type
    content_text = ""
    if content_type == "tweets":
        for idx, item in enumerate(content_items[:3], 1):
            content_text += f"{idx}. @{item['author']} ({item['author_name']}):\n"
            content_text += f"   \"{item['text']}\"\n"
            content_text += f"   (좋아요: {item['likes']}, 리트윗: {item['retweets']})\n\n"
    else:  # blog posts
        for idx, item in enumerate(content_items[:3], 1):
            content_text += f"{idx}. {item['title']}\n"
            content_text += f"   {item['summary']}\n"
            content_text += f"   링크: {item['link']}\n\n"

    source_description = "해외 바이오테크 전문가들의 최근 트윗" if content_type == "tweets" else "깅코바이오웍스 공식 블로그의 최근 포스트"
    
    prompt = f"""
    당신은 바이오테크 전문 애널리스트입니다.
    다음은 깅코바이오웍스(Ginkgo Bioworks)에 대한 {source_description}입니다.
    한국 투자자들을 위해 이를 요약하고 해설해주세요.
    
    필수 요구사항:
    1. 회사명: "깅코바이오웍스" 사용
    
    2. 형식:
       - 헤드라인: 핵심 트렌드 요약 (1줄)
       - 각 항목별로:
         * {'작성자 소개 (누구인지, 왜 신뢰할 만한지)' if content_type == 'tweets' else '포스트 제목'}
         * 내용 한글 번역/요약
         * 투자 시사점
       
    3. 톤: 전문적이지만 쉽게 이해 가능하게
    
    4. 길이: 10줄 이하로 간결하게
    
    5. 마무리:
       - 출처: {'각 트윗 작성자 명시' if content_type == 'tweets' else 'Ginkgo 공식 블로그'}
       - 해시태그: #DNA #깅코바이오웍스 #바이오테크
    
    콘텐츠:
    {content_text}
    """
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"번역 및 해설 생성 오류: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    # Test stub
    logger.info("테스트 실행...")
    mock_tweets = [
        {
            'text': 'Exciting partnership announcement from Ginkgo!',
            'author': 'jasonjkelly',
            'author_name': 'Jason Kelly',
            'likes': 150,
            'retweets': 45
        }
    ]
    # print(translate_and_comment(mock_tweets))
