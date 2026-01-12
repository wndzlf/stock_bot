import os
from google import genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_and_comment(tweets: list) -> str:
    """
    Translate tweets to Korean and add investment commentary.
    
    Args:
        tweets (list): List of tweet dictionaries.
        
    Returns:
        str: Korean translation with commentary for X post.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("환경 변수에서 GEMINI_API_KEY를 찾을 수 없습니다.")
        return "오류: API 키가 없습니다."

    if not tweets:
        return "오늘 깅코바이오웍스 관련 전문가 트윗이 없습니다."

    # Prepare tweet text
    tweets_text = ""
    for idx, tweet in enumerate(tweets[:3], 1):  # Top 3 tweets
        tweets_text += f"{idx}. @{tweet['author']} ({tweet['author_name']}):\n"
        tweets_text += f"   \"{tweet['text']}\"\n"
        tweets_text += f"   (좋아요: {tweet['likes']}, 리트윗: {tweet['retweets']})\n\n"

    prompt = f"""
    당신은 바이오테크 전문 애널리스트입니다.
    다음은 깅코바이오웍스(Ginkgo Bioworks)에 대한 해외 바이오테크 전문가들의 최근 트윗입니다.
    한국 투자자들을 위해 이를 요약하고 해설해주세요.
    
    필수 요구사항:
    1. 회사명: "깅코바이오웍스" 사용
    
    2. 형식:
       - 헤드라인: 핵심 트렌드 요약 (1줄)
       - 각 트윗별로:
         * 작성자 소개 (누구인지, 왜 신뢰할 만한지)
         * 트윗 내용 한글 번역
         * 투자 시사점 (이게 투자자에게 의미하는 바)
       
    3. 톤: 전문적이지만 쉽게 이해 가능하게
    
    4. 길이: 10줄 이하로 간결하게
    
    5. 마무리:
       - 출처: 각 트윗 작성자 명시
       - 해시태그: #DNA #깅코바이오웍스 #바이오테크
    
    전문가 트윗:
    {tweets_text}
    """
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
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
