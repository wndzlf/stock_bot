import feedparser
import logging
from datetime import datetime, timedelta
import time
import requests
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_biotech_news(lookback_hours: int = 24) -> list:
    """
    여러 바이오테크 뉴스 소스(Nature, FierceBiotech 등)에서 랜덤하게 하나를 선택하여 최신 기술 뉴스를 가져옵니다.
    
    Args:
        lookback_hours (int): 현재 시간 기준 조회할 시간 범위 (기본값: 24시간).
        
    Returns:
        list: 뉴스 항목 리스트 (title, summary, link, published_at).
    """
    rss_sources = [
        {"name": "Fierce Biotech", "url": "https://www.fiercebiotech.com/rss"},
        {"name": "BioPharma Dive", "url": "https://www.biopharmadive.com/feeds/news/"},
        {"name": "Endpoints News", "url": "https://endpts.com/feed"},
        {"name": "GEN (Genetic Engineering & Biotechnology News)", "url": "https://www.genengnews.com/feed"},
        {"name": "Nature Biotechnology", "url": "https://www.nature.com/nbt.rss"},
        {"name": "STAT News", "url": "https://www.statnews.com/feed/"}
    ]
    
    # 랜덤하게 순서 섞기
    random.shuffle(rss_sources)
    
    cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for source in rss_sources:
        source_news_items = []
        logger.info(f"오늘의 랜덤 소스 선택: {source['name']} ({source['url']})")
        
        try:
            response = requests.get(source['url'], headers=headers, timeout=15)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning(f"{source['name']}에서 항목을 찾을 수 없습니다.")
                continue
                
            for entry in feed.entries:
                published_parsed = entry.get('published_parsed')
                if published_parsed:
                    pub_date = datetime.fromtimestamp(time.mktime(published_parsed))
                else:
                    pub_date = datetime.utcnow()
                    
                if pub_date >= cutoff_time:
                    source_news_items.append({
                        'title': entry.get('title', '제목 없음'),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'link': entry.get('link', ''),
                        'published_at': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'publisher': source['name']
                    })
            
            if source_news_items:
                logger.info(f"{source['name']}에서 {len(source_news_items)}개의 최신 뉴스를 찾았습니다.")
                return source_news_items
            else:
                logger.info(f"{source['name']}에 최근 {lookback_hours}시간 내 뉴스가 없습니다. 다음 소스로 시도합니다.")
                
        except Exception as e:
            logger.error(f"{source['name']} 피드 가져오기 오류: {e}")
            
    logger.info("모든 소스에서 최신 뉴스를 찾지 못했습니다.")
    return []

if __name__ == "__main__":
    # 테스트 코드
    items = fetch_biotech_news(lookback_hours=168) # 7일 데이터 조회
    for i, item in enumerate(items[:3]):
        print(f"{i+1}. {item['title']} ({item['published_at']})")
        print(f"Link: {item['link']}\n")
