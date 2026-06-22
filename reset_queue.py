import psycopg2

DB_CONFIG = {
    "dbname": "content_curator",
    "user": "",      
    "password": "",  # Add your password if you set one
    "host": "localhost",
    "port": "5432"
}

def reset_database_queue():
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # This query sets everything back to 'unprocessed'
        print("Resetting article queue...")
        cursor.execute("""
            UPDATE articles 
            SET is_relevant = NULL, 
                summary = NULL, 
                keywords = NULL;
        """)
        
        conn.commit()
        print(f"Success! {cursor.rowcount} articles have been sent back to the queue.")
        
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    reset_database_queue()