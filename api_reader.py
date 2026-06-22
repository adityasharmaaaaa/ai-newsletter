import psycopg2
import redis
import json
import time

# --- 1. Infrastructure Connections ---

# Connect to PostgreSQL (Running on your Mac)
DB_CONFIG = {
    "dbname": "content_curator",
    "user": "",
    "password": "",
    "host": "localhost", # Still localhost because we are running this script locally for now
    "port": "5432"
}

# Connect to Redis (Running inside Docker, exposed to Mac)
# decode_responses=True ensures Redis returns standard Python strings instead of bytes
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_article_data(article_id):
    # --- STEP 1: Check Redis (The Cache) ---
    cache_key = f"article:{article_id}:summary"
    start_time = time.time()
    
    cached_summary = cache.get(cache_key)
    
    if cached_summary:
        # CACHE HIT!
        latency = (time.time() - start_time) * 1000
        print(f"🟢 CACHE HIT! Retrieved in {latency:.2f} ms")
        return cached_summary
    
    # --- STEP 2: Fallback to PostgreSQL (Cache Miss) ---
    print("🔴 CACHE MISS! Querying PostgreSQL hard drive...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT summary FROM articles WHERE id = %s;", (article_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            return "No summary available for this article."
            
        summary = row[0]
        db_latency = (time.time() - start_time) * 1000
        print(f"   Retrieved from DB in {db_latency:.2f} ms")
        
        # --- STEP 3: Update Redis ---
        print("   Saving to Redis for future requests (TTL: 60 seconds)...")
        cache.set(cache_key, summary, ex=60)
        
        return summary
        
    except Exception as e:
        print(f"Database Error: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    print("--- FIRST REQUEST ---")
    get_article_data(1)
    
    print("\n--- SECOND REQUEST ---")
    get_article_data(1)