import os
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_news(news_items: list, ticker: str) -> str:
    """
    Summarizes a list of news items into a single X (Twitter) post using Grok (xAI).
    
    Args:
        news_items (list): List of news dictionaries (title, link, published_at).
        ticker (str): The stock ticker symbol.
        
    Returns:
        str: The generated tweet content.
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        logger.error("XAI_API_KEY not found in environment variables.")
        return "Error: API Key missing."

    if not news_items:
        return f"오늘 {ticker} 관련 주요 뉴스가 없습니다."

    # Prepare the input text
    news_text = ""
    for idx, item in enumerate(news_items[:3]): # Limit to top 3 to save tokens
        news_text += f"{idx+1}. {item['title']} (Source: {item['publisher']})\n"

    prompt = f"""
    You are a professional stock market news assistant.
    Your task is to summarize the following recent news for the stock '{ticker}' into a concise post for X (Twitter) in Korean.
    
    Requirements:
    1. Language: Korean.
    2. Format: Headline followed by 3-4 bullet points max.
    3. Currency: Convert USD to KRW (approx 1 USD = 1,450 KRW).
    4. Tone: Professional, informative, and concise.
    5. Length: STRICTLY under 10 lines of text.
    6. Ending: Add hashtags like #{ticker} #주식.
    
    News Data:
    {news_text}
    """
    
    try:
        # Initialize xAI client
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        
        # Call Grok
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes stock news in Korean."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating summary with Grok: {e}")
        return f"Error generating summary: {e}"

if __name__ == "__main__":
    # Test stub
    logger.info("Test run...")
    mock_news = [
        {'title': 'Test News', 'publisher': 'Test Publisher'}
    ]
    # print(summarize_news(mock_news, "TEST"))
