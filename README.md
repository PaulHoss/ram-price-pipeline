# RAM Price Tracker

An automated data pipeline that scrapes daily RAM prices from e-commerce retailers, archives them to a Bronze data lake on S3, and will ultimately surface insights through a full analytics stack.

## Project Goal

Building this as a portfolio project to demonstrate end-to-end data engineering and analytics engineering skills — from raw data collection through transformation and visualization.

## Pipeline Architecture

```
GitHub Actions (orchestration)
        │
        ▼
   Scraper (Python)
        │
        ▼
  S3 Bronze Layer          ← raw JSONL files, one per day
        │
        ▼
     Athena                ← SQL queries over S3 data
        │
        ▼
  dbt (Silver / Gold)      ← data modeling and transformation
        │
        ▼
Dashboard / README viz     ← final reporting layer (in progress)
```

## Tracked Products

All products are 32GB (2x16GB) desktop memory kits.

| Brand | Model | Generation | Speed |
|-------|-------|------------|-------|
| Corsair | Vengeance | DDR5 | 6000 MT/s |
| G.SKILL | Ripjaws S5 | DDR5 | 6000 MT/s |
| G.SKILL | Trident Z5 | DDR5 | 6000 MT/s |
| Corsair | Vengeance LPX | DDR4 | 3200 MT/s |
| G.SKILL | Ripjaws V | DDR4 | 3200 MT/s |
| G.SKILL | Trident Z RGB | DDR4 | 3600 MT/s |

## Retailers

| Retailer | Status |
|----------|--------|
| Newegg | ✅ Functional |
| Best Buy | 🔧 In development |

## Project Structure

```
├── scraper.py              # Main scraper and pipeline orchestrator
├── product_registry.py     # Product/retailer URL matrix
├── data_lake_manager.py    # S3 Bronze lake append logic
├── json_checker.py         # Diagnostic tool for JSON-LD verification
├── requirements.txt
├── data/
│   └── raw/                # Local Bronze layer — daily JSONL scrape archives
└── .github/
    └── workflows/
        └── run_scraper.yml # GitHub Actions daily schedule (runs 00:00 UTC)
```

## How It Works

1. **Registry** — `product_registry.py` defines all target products and their retailer URLs in a cross-join matrix.
2. **Fetch** — `scraper.py` requests each product page, with `curl_cffi` as a browser-impersonation fallback for bot-protected sites like Best Buy.
3. **Parse** — Price data is extracted from JSON-LD structured data (`<script type="application/ld+json">`) embedded in each page for search engine crawlers. This is more stable than scraping raw HTML.
4. **Store** — Results are appended to a daily-partitioned JSONL file under `data/raw/` and also written to an S3 Bronze layer.
5. **Orchestrate** — GitHub Actions runs the full pipeline daily at 00:00 UTC and auto-commits any new data back to the repository.

## Data Format

Each line in a JSONL file is one price observation:

```json
{
  "mpn": "CMK32GX5M2B6000C30",
  "brand": "Corsair",
  "gen": "DDR5",
  "model": "Vengeance",
  "scraped_title": "CORSAIR Vengeance 32GB (2 x 16GB) 288-Pin PC RAM DDR5 6000...",
  "price": 519.99,
  "currency": "USD",
  "availability": "InStock",
  "condition": "NewCondition",
  "seller": "Newegg",
  "marketplace": "Newegg",
  "date": "2026-06-17",
  "timestamp": "2026-06-17T17:00:55.384863+00:00",
  "pipeline_status": "Pass",
  "url_fetch_method": "STANDARD_REQUESTS",
  "fetch_error": null,
  "parse_error": null
}
```

## Setup

```bash
git clone <repo-url>
cd ram-price-tracker
pip install -r requirements.txt
python scraper.py
```

**Required environment variables** (set as GitHub Secrets for Actions, or locally in a `.env` file):

| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 access |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 access |
| `AWS_S3_BUCKET` | Target S3 bucket name |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | Standard HTTP fetching |
| `beautifulsoup4` | HTML parsing |
| `curl_cffi` | Browser-impersonation fallback for bot-protected retailers |
| `boto3` | AWS S3 client for Bronze lake writes |

## Diagnostic Tool

`json_checker.py` is a standalone script for verifying that a product page exposes JSON-LD structured data before adding it to the scraper. Run it interactively to inspect any URL:

```bash
python json_checker.py
```

## Roadmap

- [x] Newegg scraping (JSON-LD)
- [x] S3 Bronze layer writes
- [x] GitHub Actions daily automation
- [ ] Best Buy scraping
- [ ] AWS Athena integration (query Bronze layer with SQL)
- [ ] dbt models (Silver cleaning layer, Gold aggregation layer)
- [ ] Price trend dashboard or README visualization

## Status

> **Work in progress.** Newegg scraping is fully functional with daily automated runs. Best Buy support, Athena integration, and the dbt transformation layer are planned for upcoming iterations.
