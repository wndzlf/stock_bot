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
        url = "https://investors.ginkgobioworks.com/news-releases"
        
        logger.info(f"Ginkgo IR 보도자료 페이지 스크래핑 중: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find press release items (structure may vary, adjust selectors as needed)
        # Common patterns: article tags, div with class containing 'news' or 'release'
        press_releases = []
        
        # Try to find news items (adjust selector based on actual page structure)
        news_items = soup.find_all('article', limit=10) or \
                     soup.find_all('div', class_=lambda x: x and ('news' in x.lower() or 'release' in x.lower()), limit=10)
        
        if not news_items:
            # Fallback: try finding links in main content
            news_items = soup.find_all('a', href=lambda x: x and 'news' in x.lower(), limit=10)
        
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        for item in news_items[:5]:  # Process top 5
            try:
                # Extract title
                title_elem = item.find('h2') or item.find('h3') or item.find('a') or item
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                
                # Extract link
                link_elem = item.find('a', href=True)
                link = link_elem['href'] if link_elem else url
                if link and not link.startswith('http'):
                    link = f"https://investors.ginkgobioworks.com{link}"
                
                # Extract summary/description
                summary_elem = item.find('p') or item.find('div', class_=lambda x: x and 'summary' in x.lower())
                summary = summary_elem.get_text(strip=True)[:500] if summary_elem else title
                
                press_releases.append({
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'Ginkgo Investor Relations'
                })
            except Exception as e:
                logger.warning(f"보도자료 항목 파싱 오류: {e}")
                continue
        
        logger.info(f"Ginkgo IR 보도자료 {len(press_releases)}개를 찾았습니다.")
        return press_releases[:3]  # Return top 3
        
    except Exception as e:
        logger.error(f"Ginkgo IR 페이지 스크래핑 오류: {e}")
        return []

if __name__ == "__main__":
    # Test
    posts = fetch_ginkgo_blog()
    for post in posts:
        print(f"{post['title']}: {post['summary'][:100]}...")
