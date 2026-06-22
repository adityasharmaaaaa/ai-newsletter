import os
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader # NEW IMPORT
from dotenv import load_dotenv

load_dotenv()

if "GROQ_API_KEY" not in os.environ:
    raise ValueError("GROQ_API_KEY environment variable not found.")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# --- 1. Define the Shared State Structure ---
class AgentState(TypedDict):
    url: str          # NEW: We now pass the URL to the agent
    raw_text: str     # We will store the scraped text here
    summary: str
    keywords: list[str]

# --- 2. Define the Graph Nodes ---

def scrape_and_summarize_node(state: AgentState) -> Dict[str, Any]:
    print(f"\n--- [Node: Scrape & Analyze] Processing URL: {state['url']} ---")
    
    # 1. Scrape the full article using LangChain
    try:
        loader = WebBaseLoader(state["url"])
        docs = loader.load()
        full_article_text = docs[0].page_content
    except Exception as e:
        print(f"Scraping failed: {e}")
        # Fallback to whatever text was originally provided if scraping fails
        full_article_text = state.get("raw_text", "No content available.")
    
    # 2. Create a Deep-Dive Prompt Blueprint
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior AI Solutions Architect. 
        Read the following technical article and write a comprehensive, 3-paragraph technical deep-dive.
        
        You MUST format your response exactly like this:
        **The Core Concept:** (Explain the primary technology, model, or methodology being discussed. Minimum 3 sentences.)
        
        **Technical Implementation:** (Explain how it works under the hood. What is the architecture? How does it handle data or compute? Minimum 3 sentences.)
        
        **Why it Matters:** (Explain the business or engineering impact. Does it reduce latency? Lower costs? Improve accuracy? Minimum 3 sentences.)
        """),
        ("user", "Full Article Text: {input_text}")
    ])
    
    # 3. Chain and Execute
    chain = prompt | llm
    
    # Llama 3 70B has a massive context window, so it can easily read the whole article
    response = chain.invoke({"input_text": full_article_text})
    
    return {"summary": response.content, "raw_text": full_article_text}

# ... (Keep your existing extract_keywords_node below this) ...

def extract_keywords_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- [Node: Extract Keywords] Contacting Groq LLM ---")
    summary = state["summary"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical data extractor. Extract 3 to 5 core technical keywords from the summary. Output ONLY a comma-separated list of words. No intro, no formatting."),
        ("user", "Summary: {input_summary}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"input_summary": summary})
    
    raw_string = response.content
    keyword_list = [word.strip() for word in raw_string.split(",")]
    
    return {"keywords": keyword_list}

workflow = StateGraph(AgentState)
workflow.add_node("summarizer", scrape_and_summarize_node)
workflow.add_node("keyword_extractor", extract_keywords_node)

workflow.add_edge(START, "summarizer")
workflow.add_edge("summarizer", "keyword_extractor")
workflow.add_edge("keyword_extractor", END)

app = workflow.compile()

if __name__ == "__main__":
    print("Initializing LangGraph AI Pipeline...")
    
    initial_input = {
        "raw_text": "We introduce a new method for training Large Language Models called Parameter-Efficient Fine-Tuning (PEFT). By freezing the majority of the network weights and only updating a small adapter layer using Low-Rank Adaptation (LoRA), we reduced GPU memory consumption by 80% while maintaining state-of-the-art accuracy on natural language tasks."
    }
    
    final_state = app.invoke(initial_input)
    
    print("\n==========================================")
    print("GRAPH EXECUTION COMPLETE")
    print("Final Shared State Object contents:")
    print("==========================================")
    import pprint
    pprint.pprint(final_state)