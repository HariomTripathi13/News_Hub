import feedparser
from newspaper import Article
from sentence_transformers import SentenceTransformer
import time
from time import mktime
from datetime import datetime
import psycopg2
from urllib.parse import quote_plus
import os
from newspaper import Config

# --- CONFIGURATION ---

# 1. The PIN Secerecy
db_pin = os.getenv("DB_PASSWORD")
if not db_pin:
    raise ValueError("❌ Error: Database password not found in environment variables.")

# 2. Password Encoding
encoded_password = quote_plus(db_pin)

# 3. Connection String (IPv4 Compatible & SSL)
DB_URI = f"postgresql://postgres.furwcwgvvvziblenvhzc:{encoded_password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"

# 4. RSS Feed List
FEED_CONFIG = [
{"source": "Times of India", "url": "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"},
{"source": "News 18", "url": "https://www.news18.com/commonfeeds/v1/eng/rss/india.xml"},
{"source": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-india-news"},
{"source": "Indian Express", "url": "https://indianexpress.com/section/india/feed/"},
{"source": "Zee News", "url": "https://zeenews.india.com/rss/india-national-news.xml"},
{"source": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss"},
{"source": "The Economic Times", "url": "https://economictimes.indiatimes.com/news/india/rssfeeds/81582957.cms"},
{"source": "India Today", "url": "https://www.indiatoday.in/rss/1206514"},
{"source": "Times Now", "url": "https://www.timesnownews.com/feeds/gns-en-india.xml"}
]

# --- INITIALIZATION ---
print("🧠 Loading AI Model... (This takes a moment)")
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- UPDATED DATABASE FUNCTION: ACCEPTS CURSOR ---
def save_to_db(cur, title, url, description, content_snippet, published_at, source, image_url, embedding):
    try:
        query = """
        INSERT INTO article 
        (title, url, description, content_snippet, published_at, source, image_url, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """
        cur.execute(query, (title, url, description, content_snippet, published_at, source, image_url, embedding))
        return True
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return False

# --- MAIN PROCESSING FUNCTION ---
def process_all_feeds():
    total_articles = 0
    
    # --- FIX: OPENS CONNECTION ONCE (High Performance) ---
    print("🔌 Connecting to Database...")
    try:
        conn = psycopg2.connect(DB_URI, sslmode='require')
        cur = conn.cursor()
        print("✅ Connected to Supabase!")
    except Exception as e:
        print(f"❌ CRITICAL: Could not connect to DB. {e}")
        return

    # LOOP THROUGH FEEDS
    for feed_info in FEED_CONFIG:
        source_name = feed_info["source"]
        rss_url = feed_info["url"]
        
        print(f"\n📡 Connecting to: {source_name}...")
        
        try:
            feed = feedparser.parse(rss_url)
            print(f"   Found {len(feed.entries)} entries. Processing...")

            for entry in feed.entries:  # Process top 50 entries

                # --- "MISSING DATA BUG" SAFEGAURD ---
                url = getattr(entry, 'link', None)
                title = getattr(entry, 'title', 'No Title Available') # Default if missing
                
                if not url:
                    print("   ⚠️ Skipping: Entry has no URL")
                    continue

                # --- DATE FORMATTING SAFETY ---
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    # Converts struct_time -> "2025-01-05 14:30:00"
                    published = datetime.fromtimestamp(mktime(entry.published_parsed))
                else:
                    # Fallback to None (NULL in DB) if date is totally broken
                    published = None

                description = getattr(entry, 'summary', '')

                try:
                    # [BOT MASKING]
                    config = Config()
                    config.request_args = {''
                    'headers': {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'referer': 'https://www.google.com',
                                'Accept-Language': 'en-US,en;q=0.5',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                                },
                                'timeout': 15
                            }

                    # [EXTRACTION]
                    article = Article(url, config=config)
                    article.download()
                    article.parse()
                    
                    text_snippet = article.text[:1000]
                    image_url = article.top_image

                    # [INTELLIGENCE]
                    full_content = f"{title}. {description}. {text_snippet}"
                    vector = model.encode(full_content).tolist()

                    print(f"   ✅ [{source_name}] Saving: {title[:40]}...")
                    
                    # [MEMORY] Pass 'cur' to the function
                    save_to_db(cur, title, url, description, text_snippet, published, source_name, image_url, vector)
                    
                    # Commit (Save) after every article so we don't lose progress if it crashes later
                    conn.commit()
                    total_articles += 1

                except Exception as e:
                    print(f"   ⚠️ Skipping article: {e}")
                    continue

        except Exception as e:
            print(f"❌ Failed to read feed {source_name}: {e}")

    # CLEAN UP
    cur.close()
    conn.close()     
    print(f"\n🎉 DONE. Saved {total_articles} articles.")

# --- RUNNING FETCHER SCRIPT ---
if __name__ == "__main__":
    process_all_feeds()