import psycopg2

DB_CONFIG = {
    "dbname": "content_curator",
    "user": "",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

def migrate_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Executing schema migration...")
        # Add summary column
        cursor.execute("ALTER TABLE articles ADD COLUMN IF NOT EXISTS summary TEXT;")
        # Add keywords array column
        cursor.execute("ALTER TABLE articles ADD COLUMN IF NOT EXISTS keywords TEXT[];")
        
        conn.commit()
        print("Database migration successful. Schema upgraded!")
        
    except Exception as e:
        print(f"Migration Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_database()