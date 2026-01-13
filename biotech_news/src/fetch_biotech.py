import feedparser
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_biotech_news(lookback_hours: int = 24) -> list:
    """
    Nature Biotechnology RSS 피드에서 최신 기술 뉴스를 가져옵니다.
    
    Args:
        lookback_hours (int): 현재 시간 기준 조회할 시간 범위 (기본값: 24시간).
        
    Returns:
        list: 뉴스 항목 리스트 (title, summary, link, published_at).
    """
    rss_url = "https://www.nature.com/nbt.rss"
    logger.info(f"Nature Biotechnology RSS 피드 가져오는 중: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning("RSS 피드에서 항목을 찾을 수 없습니다.")
            return []
            
        news_items = []
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        for entry in feed.entries:
            # RSS 피드의 날짜 형식은 다양할 수 있으므로 안전하게 파싱
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                pub_date = datetime.fromtimestamp(time.mktime(published_parsed))
            else:
                pub_date = datetime.utcnow()
                
            if pub_date >= cutoff_time:
                news_items.append({
                    'title': entry.get('title', '제목 없음'),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'link': entry.get('link', ''),
                    'published_at': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'publisher': 'Nature Biotechnology'
                })
        
        logger.info(f"{len(news_items)}개의 최신 바이오테크 뉴스를 찾았습니다.")
        return news_items
        
    except Exception as e:
        logger.error(f"RSS 피드 가져오기 오류: {e}")
        return []

if __name__ == "__main__":
    # 테스트 코드
    items = fetch_biotech_news(lookback_hours=168) # 7일 데이터 조회
    for i, item in enumerate(items[:3]):
        print(f"{i+1}. {item['title']} ({item['published_at']})")
        print(f"Link: {item['link']}\n")
