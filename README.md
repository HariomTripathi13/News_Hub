# 📰 AI-Powered News Aggregator (Backend)

> **Status:** 🟢 Active | **Deployment:** GitHub Actions | **Database:** Supabase (PostgreSQL)

## 📖 Overview

This project is the **backend infrastructure** for an automated news aggregation engine. It autonomously fetches, processes, and stores news articles from various RSS feeds on a scheduled basis.

Key features include **automated data ingestion**, **AI-powered semantic analysis** (generating embeddings for future clustering), and **self-maintaining storage** via a "janitor" protocol.

## ⚙️ Tech Stack & Architecture

* **Language:** Python 3.11
* **Automation:** GitHub Actions (Cron Scheduler)
* **Database:** PostgreSQL (hosted on Supabase)
* **AI/ML:** `sentence-transformers` (All-MiniLM-L6-v2) for generating vector embeddings.
* **Data Processing:** `feedparser`, `requests`, `newspaper3k` (with custom headers to bypass 403 blocks).

## 🚀 How It Works

The system operates on a fully automated "Serverless" architecture using GitHub Actions workflows:

### 1. The Scheduler (`daily_news.yml`)

* **Trigger:** Runs automatically every hour (Cron: `0 * * * *`).
* **Environment:** Boots a fresh Ubuntu container with Python 3.11.

### 2. The Data Fetcher (`data_fetcher.py`)

* **Ingestion:** Connects to RSS feeds and identifies new articles.
* **Anti-Bot Bypass:** Uses a custom "Manual Override" strategy with rotated browser headers to legally access news content protected by standard bot filters.
* **Processing:** Extracts the title, summary, source, and publication date.
* **AI Enrichment:** Passes the article summary through a Transformer model to generate a **384-dimensional vector embedding**. This prepares the data for advanced semantic search and clustering (in development).
* **Storage:** Saves structured data into Supabase (PostgreSQL), ensuring no duplicates via URL checking.

### 3. The Janitor (`janitor.py`)

* **Trigger:** Runs once daily at 3:00 AM UTC.
* **Function:** Automatically scans the database for "stale" data and optimizes storage to keep the system lightweight and cost-effective.

## 🛠️ Installation & Setup

If you want to run this locally:

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/news_hub_backend.git
cd news_hub_backend

```


2. **Set up Virtual Environment**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Environment Variables**
You need a `.env` file or system environment variables for:
* `DB_PASSWORD`: Your Supabase database password.


5. **Run the Scripts**
```bash
# Run the news fetcher
python data_fetcher.py

# Run the cleanup tool
python janitor.py

```



## 🔮 Roadmap (In Progress)

* [x] Automated Data Pipeline (GitHub Actions)
* [x] PostgreSQL Integration (Supabase)
* [x] AI Vector Embeddings Generation
* [ ] **In Progress:** Clustering Engine (Grouping similar news topics)
* [ ] **Next Step:** Frontend Development & API Integration

---

**Author:** [Hariom Tripathi]
**License:** PolyForm Noncommercial License 1.0.0
