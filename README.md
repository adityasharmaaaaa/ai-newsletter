# AI Engineering Weekly: Automated Content Curator

An end-to-end, fully automated AI engineering pipeline that ingests technical RSS feeds, filters them using a custom PyTorch classification model, performs deep-dive technical analysis using a LangGraph web-scraping agent, and delivers a categorized, industry-grade Markdown newsletter to subscribers.

---

## 🧠 Architecture Overview

This project implements a complete microservices and ML pipeline architecture, running autonomously in the cloud.

| Module | File | Description |
|--------|------|-------------|
| **Data Ingestion** | `ingest.py` | Fetches the latest articles from high-signal AI engineering RSS feeds (BAIR, AWS ML, Google AI, Nvidia Deep Learning) and stores them in a Neon PostgreSQL database. |
| **ML Relevance Filtering** | `inference.py` / `pipeline_runner.py` | A custom-trained PyTorch embedding model evaluates raw text and calculates a relevance probability. Only high-signal technical articles pass the filter. |
| **Agentic Web Scraping & Analysis** | `agent_pipeline.py` | A LangGraph agent dynamically visits the URL of relevant articles, scrapes the full text, and uses Groq (Llama 3 70B) to generate a structured, 3-paragraph technical deep dive *(Core Concept, Technical Implementation, Business Impact)*. |
| **Newsletter Generation** | `newsletter_generator.py` | An LLM formatting engine categorizes the week's processed articles and structures them into a clean, comprehensive Markdown report. |
| **Automated Dispatch** | `email_dispatcher.py` | Converts the payload and dispatches the raw `.md` file as a downloadable attachment to all active subscribers via secure SMTP. |
| **Frontend & API** | `api_server.py` & `index.html` | A FastAPI web server hosting a modern HTML/CSS landing page to capture new subscriber emails, deployed seamlessly on Render. |

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Machine Learning** | PyTorch, MLflow (Experiment Tracking) |
| **Agentic AI / LLMs** | LangChain, LangGraph, Groq (Llama 3.3 70B Versatile) |
| **Backend & API** | FastAPI, Uvicorn, Python |
| **Database & Caching** | PostgreSQL (Neon.tech), Redis (Dockerized), psycopg2 |
| **Automation & Deployment** | GitHub Actions (Cron), Render.com |
| **Web Scraping** | BeautifulSoup4, LangChain WebBaseLoader |

---

## 📂 Project Structure

```
├── .github/workflows/
│   └── weekly_newsletter.yml  # GitHub Actions CI/CD and Cron automation
├── api_server.py              # FastAPI backend for subscriber registration
├── index.html                 # Frontend landing page for the API
├── ingest.py                  # RSS parser and DB population script
├── pipeline_runner.py         # Main orchestrator for PyTorch -> LangGraph
├── agent_pipeline.py          # LangGraph agent (Web scraping + LLM Analysis)
├── newsletter_generator.py    # LLM formatting engine for Markdown curation
├── email_dispatcher.py        # SMTP email client and Markdown attachment handler
├── model.py                   # PyTorch neural network architecture
├── train.py                   # PyTorch training loop with MLflow tracking
├── inference.py               # PyTorch inference engine
├── data_pipeline.py           # PyTorch Dataset and DataLoader classes
├── tokenizer.py               # Custom text tokenization logic
├── db_setup.py                # Database schema creation script
├── db_migrate_newsletter.py   # Database migration for subscribers table
├── mcp_server.py              # FastMCP server exposing data to other AI agents
└── api_reader.py              # Read-through Redis cache implementation
```

---

## ⚙️ Local Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-content-curator.git
cd ai-content-curator
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory and add the following keys:

```env
DATABASE_URL="postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=require"
GROQ_API_KEY="your_groq_api_key"
SMTP_USER="your_email@gmail.com"
SMTP_PASS="your_16_digit_app_password"
```

### 4. Initialize the Database

Run the database setup scripts to create the required tables in your Neon Postgres instance:

```bash
python3 db_setup.py
python3 db_migrate_newsletter.py
```

---

## 🚀 Usage & Execution

### Run the API Server (Local Frontend)

```bash
python3 api_server.py
```

Navigate to `http://localhost:8000/` to view the landing page and subscribe.

### Run the Pipeline Manually

To manually trigger the full curation pipeline:

```bash
# 1. Fetch new RSS articles
python3 ingest.py

# 2. Run PyTorch filter and LangGraph Web Scraper
python3 pipeline_runner.py

# 3. Generate and dispatch the Markdown newsletter
python3 email_dispatcher.py
```

---

## ☁️ Cloud Deployment

This project is designed to run entirely on **free-tier cloud infrastructure**:

- **Database:** Hosted on [Neon.tech](https://neon.tech) (Serverless Postgres).
- **Web Server:** Hosted on [Render.com](https://render.com) (Free Web Service). Simply deploy the repository and set the `DATABASE_URL` environment variable.
- **Automation:** Managed by GitHub Actions. The `.github/workflows/weekly_newsletter.yml` file is configured to execute the pipeline every **Friday at 09:00 UTC** using your repository secrets.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/ai-content-curator/issues).

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
