import os
from google import genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_news(news_items: list, ticker: str) -> str:
    """
    Summarizes a list of news items into a single X (Twitter) post using Gemini (New SDK).
    
    Args:
        news_items (list): List of news dictionaries (title, link, published_at).
        ticker (str): The stock ticker symbol.
        
    Returns:
        str: The generated tweet content.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("환경 변수에서 GEMINI_API_KEY를 찾을 수 없습니다.")
        return "오류: API 키가 없습니다."

    if not news_items:
        return f"오늘 {ticker} 관련 주요 뉴스가 없습니다."

    # Prepare the input text
    news_text = ""
    for idx, item in enumerate(news_items[:3]): # Limit to top 3 to save tokens
        news_text += f"{idx+1}. {item['title']} (Source: {item['publisher']})\n"

    prompt = f"""
    You are a professional stock market analyst writing for Korean retail investors.
    Summarize the following recent news for '{ticker}' (깅코바이오웍스, Ginkgo Bioworks) into a concise X (Twitter) post in Korean.
    
    CRITICAL Requirements:
    1. Company Name: ALWAYS use "깅코바이오웍스" (NOT 진코바이오웍스)
    
    2. Source Attribution: 
       - At the end, ALWAYS add "출처: [언론사명]" for each major news item
       - Example: "출처: Bloomberg, Reuters"
    
    3. Currency & Financial Impact:
       - Convert ALL USD amounts to KRW (1 USD = 1,450 KRW)
       - Format: "약 X억원 (약 $Y million)"
       - ALWAYS explain the financial impact: "이는 회사의 [매출/손실/투자] 측면에서 [긍정적/부정적] 영향을 미칠 것으로 예상됩니다"
    
    4. Format: 
       - Catchy headline about the key trend
       - 2-3 bullet points with investment insights
       - Focus on: partnerships, financial results, products, regulatory news
       - Include financial impact analysis for any monetary figures
    
    5. Tone: Professional but accessible for retail investors
    
    6. Length: STRICTLY under 10 lines
    
    7. Ending: 
       - Source attribution line
       - Hashtags: #DNA #깅코바이오웍스
    
    News Data (last 10 days):
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
    # Test stub
    logger.info("Test run...")
    mock_news = [
        {'title': 'Test News', 'publisher': 'Test Publisher'}
    ]
    # print(summarize_news(mock_news, "TEST"))
