import yfinance as yf
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_stock_news(ticker_symbol: str, lookback_hours: int = 72) -> list:
    """
    Fetches news for a given stock ticker using yfinance.
    
    Args:
        ticker_symbol (str): The stock ticker (e.g., "DNA").
        lookback_hours (int): How many hours back to filter news for.
        
    Returns:
        list: A list of dictionaries containing news metadata.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        
        if not news:
            logger.info(f"No news found for {ticker_symbol}")
            return []
            
        filtered_news = []
        # Calculate the cutoff time (current time - lookback period)
        # Note: yfinance news usually returns a timestamp (seconds since epoch)
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        for item in news:
            # item.get('providerPublishTime') is a unix timestamp
            pub_time = item.get('providerPublishTime')
            if pub_time:
                pub_dt = datetime.fromtimestamp(pub_time)
                if pub_dt > cutoff_time:
                    filtered_news.append({
                        'title': item.get('title'),
                        'link': item.get('link'),
                        'publisher': item.get('publisher'),
                        'published_at': pub_dt.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        logger.info(f"Found {len(filtered_news)} items for {ticker_symbol} in the last {lookback_hours} hours.")
        return filtered_news

    except Exception as e:
        logger.error(f"Error fetching news for {ticker_symbol}: {e}")
        return []

if __name__ == "__main__":
    # Test run
    results = fetch_stock_news("DNA")
    for news_item in results:
        print(f"- {news_item['title']} ({news_item['publisher']})")
