import feedparser
from newspaper import Article
from newspaper import Config
from sentence_transformers import SentenceTransformer
import time
import psycopg2

# Database Connection Setup
DB_URI = "postgresql://postgres.furwcwgvvvziblenvhzc:HariomTripathi%40132003@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"

# CONFIGURATION: PASTE YOUR FEEDS HERE
FEED_CONFIG = [
{"source": "Buisness Standard", "url": "https://www.indiatoday.in/rss/1206514" },
]

# [SETUP] Load the AI Brain once
print("🧠 Loading AI Model... (This takes a moment)")
model = SentenceTransformer('all-MiniLM-L6-v2')
    
def process_all_feeds():
    total_articles = 0
    
    # OUTER LOOP: GO THROUGH EACH WEBSITE
    for feed_info in FEED_CONFIG:
        source_name = feed_info["source"]
        rss_url = feed_info["url"]
        
        print(f"\n📡 Connecting to: {source_name}...")
        
        try:
            feed = feedparser.parse(rss_url)
            print(f"   Found {len(feed.entries)} entries. Processing top 5...")

            # INNER LOOP: PROCESS ARTICLES IN THIS FEED
            for entry in feed.entries[:5]: 
                url = entry.link
                title = entry.title
                
                # specific date handling for different RSS formats
                published = getattr(entry, 'published', None) 
                description = getattr(entry, 'summary', '')

                try:
                    # [EXTRACTION]
                    # A "Browser Config" to fool the server
                    config = Config()
                    Config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                    Config.request_timeout = 10 # 10 seconds timeout before giving up

                    #Passing the config to Article object
                    article = Article(url, config=config)
                    article.download()
                    article.parse() 
                    article = Article(url)
                    article.download()
                    article.parse()
                    
                    text_snippet = article.text[:1000]
                    image_url = article.top_image

                    # [INTELLIGENCE]
                    full_content_to_vectorize = f"{title}. {description}. {text_snippet}"
                    vector = model.encode(full_content_to_vectorize).tolist()

                    # [OUTPUT] (Simulating the Save)
                    print(f"   ✅ [{source_name}] Vectorized: {title[:40]}...")
                    
                    # Here you would call your save_to_db function
                    # save_to_db(cur, title, url, description, text_snippet, published, source_name, image_url, vector)
                    
                    total_articles += 1

                except Exception as e:
                    print(f"   ⚠️ Skipping article: {e}")
                    continue

        except Exception as e:
            print(f"❌ Failed to read feed {source_name}: {e}")
            
    print(f"\n🎉 DONE. Processed {total_articles} articles across {len(FEED_CONFIG)} sources.")

if __name__ == "__main__":
    process_all_feeds()