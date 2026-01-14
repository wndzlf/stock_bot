import requests
import feedparser

rss_sources = [
    {"name": "Fierce Biotech", "url": "https://www.fiercebiotech.com/rss/biotech-news"},
    {"name": "BioPharma Dive", "url": "https://www.biopharmadive.com/feeds/news/"},
    {"name": "Endpoints News", "url": "https://endpts.com/feed"},
    {"name": "BioSpace", "url": "https://www.biospace.com/feed"},
    {"name": "GEN", "url": "https://www.genengnews.com/feed"},
    {"name": "Nature Biotechnology", "url": "https://www.nature.com/nbt.rss"},
    {"name": "STAT News", "url": "https://www.statnews.com/feed/"}
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for source in rss_sources:
    try:
        print(f"Testing {source['name']}...")
        response = requests.get(source['url'], headers=headers, timeout=10)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            if feed.entries:
                print(f"  ✅ Success! Found {len(feed.entries)} entries.")
            else:
                print(f"  ⚠️  Fetched but no entries found (Parser issue?).")
        else:
            print(f"  ❌ Failed with status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print("-" * 30)
