from mcp.server.fastmcp import FastMCP
import psycopg2

# Initialize the MCP Server
mcp = FastMCP("ContentCurator")

DB_CONFIG = {
    "dbname": "content_curator",
    "user": "",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

@mcp.tool()
def get_recent_ai_summaries(limit: int = 5) -> str:
    """
    Fetches the most recently published AI/ML engineering articles that have been verified as technically relevant. 
    Returns the article titles and their AI-generated summaries. 
    Use this when the user asks for the latest AI news, research, or engineering updates.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query for relevant articles that actually have summaries
        query = """
            SELECT title, summary 
            FROM articles 
            WHERE is_relevant = 1 AND summary IS NOT NULL 
            ORDER BY id DESC 
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        if not rows:
            return "No relevant AI articles found in the database yet."
            
        # Format the output into a clean string for the LLM to read
        formatted_result = "Here are the latest curated AI articles:\n\n"
        for title, summary in rows:
            formatted_result += f"- **{title}**: {summary}\n"
            
        return formatted_result
        
    except Exception as e:
        return f"Database error occurred: {str(e)}"
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    print("Starting Content Curator MCP Server...", flush=True)
    mcp.run()