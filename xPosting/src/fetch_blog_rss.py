import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_ginkgo_blog(lookback_hours: int = 168) -> list:
    """
    Fetch recent press releases from Ginkgo's Investor Relations page as fallback.
    
    Args:
        lookback_hours (int): How many hours back to search (default: 168 = 7 days).
        
    Returns:
        list: List of press release dictionaries.
    """
    try:
        url = "https://investors.ginkgobioworks.com/news/default.aspx"
        
        logger.info(f"Ginkgo IR 보도자료 페이지 스크래핑 중: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Referer': 'https://investors.ginkgobioworks.com/',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Identified selectors from browser analysis
        news_items = soup.select('.module_item')
        
        if not news_items:
            logger.warning("뉴스 항목(.module_item)을 찾을 수 없습니다. 페이지 구조 확인 필요.")
            return []
        
        press_releases = []
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        for item in news_items:
            try:
                # Extract Headline Link
                link_elem = item.select_one('.module_headline-link')
                if not link_elem:
                    continue
                
                # Title typically in <h4> or the link text itself
                title_elem = link_elem.find('h4') or link_elem
                title = title_elem.get_text(strip=True)
                
                # Link handling
                link = link_elem['href']
                if link and not link.startswith('http'):
                    link = f"https://investors.ginkgobioworks.com{link}"
                
                # Date extraction
                date_elem = item.select_one('.module_date-text')
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                
                # Parse date (Format: Jan 12, 2024)
                # If parsing fails, use current time but keep original string
                pub_date = datetime.utcnow()
                try:
                    if date_str:
                        pub_date = datetime.strptime(date_str, "%b %d, %Y")
                except:
                    pass
                
                if pub_date >= cutoff_time:
                    press_releases.append({
                        'title': title,
                        'summary': f"발표일: {date_str}\n{title}",
                        'link': link,
                        'published_at': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'Ginkgo Investor Relations'
                    })
                
                if len(press_releases) >= 3:
                    break
                    
            except Exception as e:
                logger.warning(f"항목 파싱 중 오류: {e}")
                continue
        
        logger.info(f"Ginkgo IR 보도자료 {len(press_releases)}개를 찾았습니다.")
        return press_releases
        
    except Exception as e:
        logger.error(f"Ginkgo IR 페이지 스크래핑 오류: {e}")
        return []

if __name__ == "__main__":
    # Test
    posts = fetch_ginkgo_blog()
    for post in posts:
        print(f"{post['title']}: {post['summary'][:100]}...")
