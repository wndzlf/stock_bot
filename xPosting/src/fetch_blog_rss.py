import feedparser
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_ginkgo_blog(lookback_hours: int = 168) -> list:
    """
    Fetch recent posts from Ginkgo's official blog as fallback.
    
    Args:
        lookback_hours (int): How many hours back to search (default: 168 = 7 days).
        
    Returns:
        list: List of blog post dictionaries.
    """
    try:
        rss_url = "https://www.ginkgobioworks.com/feed/"
        
        logger.info(f"Ginkgo 블로그 RSS 가져오는 중: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.info("Ginkgo 블로그 RSS 항목을 찾을 수 없습니다.")
            return []
        
        # Filter by time
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        posts = []
        
        for entry in feed.entries:
            pub_date = datetime(*entry.published_parsed[:6])
            
            if pub_date >= cutoff_time:
                posts.append({
                    'title': entry.title,
                    'summary': entry.get('summary', '')[:500],  # First 500 chars
                    'link': entry.link,
                    'published_at': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'Ginkgo Official Blog'
                })
        
        logger.info(f"최근 {lookback_hours}시간 내 Ginkgo 블로그 포스트 {len(posts)}개를 찾았습니다.")
        return posts[:3]  # Return top 3 most recent
        
    except Exception as e:
        logger.error(f"Ginkgo 블로그 RSS 가져오기 오류: {e}")
        return []

if __name__ == "__main__":
    # Test
    posts = fetch_ginkgo_blog()
    for post in posts:
        print(f"{post['title']}: {post['summary'][:100]}...")
