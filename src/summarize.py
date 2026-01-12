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
        logger.error("GEMINI_API_KEY not found in environment variables.")
        return "Error: API Key missing."

    if not news_items:
        return f"오늘 {ticker} 관련 주요 뉴스가 없습니다."

    # Prepare the input text
    news_text = ""
    for idx, item in enumerate(news_items[:3]): # Limit to top 3 to save tokens
        news_text += f"{idx+1}. {item['title']} (Source: {item['publisher']})\n"

    prompt = f"""
    You are a professional stock market analyst writing for Korean retail investors.
    Summarize the following recent news for '{ticker}' (Ginkgo Bioworks) into a concise X (Twitter) post in Korean.
    
    Requirements:
    1. Language: Korean (natural, easy to understand for retail investors).
    2. Format: 
       - Start with a catchy headline about the key trend
       - 2-3 bullet points highlighting investment-relevant insights
       - Focus on: partnerships, financial results, product developments, regulatory news
    3. Currency: Convert all USD amounts to KRW (1 USD = 1,450 KRW). Show both: "약 X억원 ($Y million)"
    4. Tone: Professional but accessible. Explain technical terms simply.
    5. Length: STRICTLY under 10 lines.
    6. Ending: Add hashtags #{ticker} #진코바이오웍스 #바이오주 #미국주식
    
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
        logger.error(f"Error generating summary: {e}")
        return f"Error generating summary: {e}"

if __name__ == "__main__":
    # Test stub
    logger.info("Test run...")
    mock_news = [
        {'title': 'Test News', 'publisher': 'Test Publisher'}
    ]
    # print(summarize_news(mock_news, "TEST"))
