import psycopg2
# Importing the brains you built!
from inference import predict
from agent_pipeline import app

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def process_next_article():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # We wrap the core logic in a loop
        while True:
            print("Fetching next unprocessed article...")
            # Grabbing one at a time is still safe for memory, but now it loops!
            cursor.execute("SELECT id, title,url, content FROM articles WHERE is_relevant IS NULL LIMIT 1;")
            row = cursor.fetchone()
            
            if not row:
                print("Queue is empty! All articles processed.")
                break # Exit the loop when done
                
            article_id, title,url, content = row

            print(f"\n--- Processing Article ID {article_id} ---")
            print(f"Title: '{title}'")
            
            # 2. PyTorch Inference (Stage 1)
            print("\nPassing content to custom PyTorch Classifier...")
            # We append title + content to give our PyTorch model enough context
            text_to_evaluate = title + ". " + content
            ai_probability = predict(text_to_evaluate)
            print(f"PyTorch Relevance Probability: {ai_probability:.4f}")
            
            # 3. Decision Logic
            if ai_probability > 0.5:
                print("Article deemed RELEVANT. Initiating LangGraph LLM Pipeline...")
                
                # Run LangGraph (Stage 3)
                final_state = app.invoke({
                "url": url, 
                "raw_text": text_to_evaluate 
                })
                summary = final_state["summary"]
                keywords = final_state["keywords"]
                
                # 4. Save Enriched Data to PostgreSQL (Stage 2)
                print("Saving summary and keywords back to PostgreSQL...")
                update_query = """
                    UPDATE articles 
                    SET is_relevant = 1, summary = %s, keywords = %s
                    WHERE id = %s;
                """
                # psycopg2 automatically converts the Python list into a PostgreSQL array!
                cursor.execute(update_query, (summary, keywords, article_id))
                
            else:
                print("Article deemed IRRELEVANT. Skipping LLM enrichment.")
                update_query = "UPDATE articles SET is_relevant = 0 WHERE id = %s;"
                cursor.execute(update_query, (article_id,))
                
            conn.commit()
            print(f"Finished Article {article_id}. Moving to the next...\n")
        
    except Exception as e:
        print(f"Pipeline Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    process_next_article()