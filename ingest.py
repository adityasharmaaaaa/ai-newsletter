import feedparser
import psycopg2
from datetime import datetime
from time import mktime

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def fetch_and_store_articles():
    feed_urls = [
        "https://bair.berkeley.edu/blog/feed.xml",
        "https://aws.amazon.com/blogs/machine-learning/feed/",
        "https://ai.googleblog.com/feeds/posts/default?alt=rss",
        "https://developer.nvidia.com/blog/category/deep-learning/feed/"
    ]
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # FIX 1: Move the counter OUTSIDE the loop so it keeps a running total
        inserted_count = 0 
        
        for feed_url in feed_urls:
            print(f"\nFetching RSS feed from {feed_url}...")
            
            # Some servers block Python bots. Giving it a standard User-Agent helps bypass this.
            d = feedparser.parse(feed_url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            
            print(f" -> Found {len(d.entries)} articles in this feed.")
            
            insert_query = """
                INSERT INTO articles (title, url, content, published_date) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE
                SET published_date = EXCLUDED.published_date;
            """
            
            for entry in d.entries:
                title = entry.title
                url = entry.link
                # Use .get() so it doesn't crash if the summary is missing
                content = entry.get('summary', '') 
                
                # FIX 2: Check for published_parsed first, fallback to updated_parsed, fallback to right now.
                raw_time_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                
                if raw_time_struct:
                    published_date = datetime(*raw_time_struct[:6])
                else:
                    published_date = datetime.now() # Ultimate safety net

                cursor.execute(insert_query, (title, url, content, published_date))
                inserted_count += cursor.rowcount
            
        conn.commit()
        print(f"\n==========================================")
        print(f"SUCCESS! Processed {inserted_count} rows in the database.")
        print(f"==========================================\n")
        
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    fetch_and_store_articles()