import os
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_news(news_items: list, ticker: str) -> str:
    """
    Summarizes a list of news items into a single X (Twitter) post using Gemini.
    
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

    genai.configure(api_key=api_key)
    
    # Prepare the input text
    news_text = ""
    for idx, item in enumerate(news_items[:5]): # Limit to top 5
        news_text += f"{idx+1}. {item['title']} (Source: {item['publisher']})\n"

    prompt = f"""
    You are a professional stock market news assistant.
    Your task is to summarize the following recent news for the stock '{ticker}' into a concise post for X (Twitter) in Korean.
    
    Requirements:
    1. Language: Korean.
    2. Format: Headline followed by bullet points.
    3. Currency: If any USD amounts are mentioned, convert them to KRW (keep USD in brackets). Assume 1 USD = 1,450 KRW.
    4. Tone: Professional, informative, and concise.
    5. Length: Keep it under 500 characters if possible (for a long tweet or thread).
    6. Ending: Add hashtags like #{ticker} #주식 #미국주식.
    
    News Data:
    {news_text}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Error generating summary."

if __name__ == "__main__":
    # Test stub
    logger.info("Test run...")
    # Mock data
    mock_news = [
        {'title': 'Ginkgo Bioworks Signs New Partnership with Pfizer', 'publisher': 'Yahoo Finance'},
        {'title': 'DNA Stock falls 5% amid market correction', 'publisher': 'Bloomberg'}
    ]
    # Ideally set GEMINI_API_KEY in env before running
    # print(summarize_news(mock_news, "Ginkgo Bioworks"))
