import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def create_schema():
    try:
        print("Connecting to Cloud PostgreSQL (Neon)...")
        # Connect using the single URL string
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            url VARCHAR UNIQUE NOT NULL,
            content TEXT,
            published_date TIMESTAMP,
            is_relevant INTEGER,
            summary TEXT,
            keywords TEXT[]
        );
        """
        
        print("Executing schema creation...")
        cursor.execute(create_table_query)
        conn.commit()
        
        print("Success! Table 'articles' is ready on the cloud.")
        
    except Exception as e:
        print(f"Cloud DB Error: {e}")
        
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    create_schema()