import feedparser
import logging
import urllib.parse
from datetime import datetime, timedelta
from time import mktime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_stock_news(ticker_symbol: str, lookback_hours: int = 24) -> list:
    """
    Fetches news for a given stock ticker using Google News RSS.
    
    Args:
        ticker_symbol (str): The stock ticker (e.g., "DNA").
        lookback_hours (int): How many hours back to filter news for.
        
    Returns:
        list: A list of dictionaries containing news metadata.
    """
    try:
        # URL Encode the query
        query = urllib.parse.quote(f"{ticker_symbol} stock")
        
        # Google News RSS URL (English, US)
        # We fetch English news because it's more abundant for US stocks.
        # The summarizer will translate it anyway.
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Fetching RSS: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.info(f"No RSS entries found for {ticker_symbol}")
            return []
            
        filtered_news = []
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        for entry in feed.entries:
            # entry.published_parsed is a struct_time
            if hasattr(entry, 'published_parsed'):
                pub_dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                
                if pub_dt > cutoff_time:
                    filtered_news.append({
                        'title': entry.title,
                        'link': entry.link,
                        'publisher': entry.source.title if hasattr(entry, 'source') else 'Google News',
                        'published_at': pub_dt.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        logger.info(f"Found {len(filtered_news)} items for {ticker_symbol} in the last {lookback_hours} hours via Google News.")
        return filtered_news

    except Exception as e:
        logger.error(f"Error fetching news for {ticker_symbol}: {e}")
        return []

if __name__ == "__main__":
    # Test run
    results = fetch_stock_news("TSLA", lookback_hours=72)
    for news_item in results:
        print(f"- {news_item['title']} ({news_item['published_at']})")
