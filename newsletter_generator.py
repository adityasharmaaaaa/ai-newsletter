import psycopg2
from langchain_core.prompts import ChatPromptTemplate
# Import the Groq LLM engine you already built!
from agent_pipeline import llm 

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")


def fetch_weekly_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        query = """
           SELECT title,url,summary
           FROM articles
           WHERE is_relevant = 1 and published_date>=CURRENT_DATE-INTERVAL '100 days' and summary is NOT NULL
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        formatted_row=[{
            "title":row[0],
            "url":row[1],
            "summary":row[2]
            }
            for row in rows
        ]
        return formatted_row
        
        
    except Exception as e:
        print(f"Database Error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def generate_markdown_newsletter(weekly_data: list) -> str:
    if not weekly_data:
        return "# No AI News This Week\n\nIt looks like it was a quiet week in the AI engineering world!"

   
    raw_context = ""
    for item in weekly_data:
        raw_context += f"Title: {item['title']}\nURL: {item['url']}\nSummary: {item['summary']}\n\n"
        
    print("Sending context to Groq for formatting...")

    
    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior AI industry technical editor.

Your job is to transform a collection of AI news articles into a professional weekly newsletter.

Instructions:

1. Analyze all provided articles.
2. Group them into 5 to 10 meaningful categories.
3. Produce clean Markdown output.

Formatting requirements:

# AI Engineering Weekly Newsletter

## Category Name

### Article Title

Summary paragraph.

Read more: URL

Rules:

- Every article MUST appear exactly once.
- ALWAYS include the URL.
- Keep summaries concise.
- Do not invent facts.
- Do not add information not present in the input.
- Do not output conversational filler.
- Output ONLY Markdown.
"""
    ),
    ("user", "Here is the raw data for this week:\n\n{context}")
])
    
    chain = prompt | llm
    response = chain.invoke({"context": raw_context})
    
    return response.content

if __name__ == "__main__":
    print("Fetching weekly data...")
    data = fetch_weekly_data()
    print(f"Found {len(data)} relevant articles this week.")
    
    if len(data) > 0:
        markdown_output = generate_markdown_newsletter(data)
        
        print("\n==========================================")
        print("GENERATED NEWSLETTER (MARKDOWN)")
        print("==========================================")
        print(markdown_output)