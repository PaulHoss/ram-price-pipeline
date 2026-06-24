# RAM Price Tracker

An automated data pipeline that scrapes daily RAM prices from e-commerce retailers, archives them to a Bronze data lake on S3, models them through Silver/Gold layers in dbt, and surfaces insights through a live Evidence dashboard on GitHub Pages.

## Live Dashboard

🔗 **[ram-price-pipeline dashboard](https://paulhoss.github.io/ram-price-pipeline/)**

## Project Goal

Portfolio project demonstrating end-to-end data engineering and analytics engineering skills — from raw data collection through transformation and visualization.

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
     Athena                ← SQL queries over S3 data (via Glue Data Catalog)
        │
        ▼
  dbt (Silver / Gold)      ← data modeling and transformation
        │
        ▼
  Evidence Dashboard       ← interactive charts, deployed to GitHub Pages
  (GitHub Pages)
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
├── scraper.py                       # Main scraper and pipeline orchestrator
├── product_registry.py              # Product/retailer URL matrix
├── data_lake_manager.py             # S3 Bronze lake append logic
├── json_checker.py                  # Diagnostic tool for JSON-LD verification
├── requirements.txt
├── data/
│   └── raw/                         # Local Bronze layer — daily JSONL scrape archives
├── infrastructure/
│   └── setup_athena.py              # One-time Glue database/table provisioning for Athena
├── scripts/
│   └── export_csv.py                # Queries Gold Athena table, exports CSV for dashboard
├── ram_price_dbt/                   # dbt project (Silver/Gold transformation layer)
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_scrapes.sql      # Silver: cleans/casts/validates raw Bronze scrapes
│   │   └── marts/
│   │       └── fct_ram_prices.sql   # Gold: analytics-ready fact table with price deltas
│   └── dbt_project.yml
├── dashboard/                       # Evidence dashboard (GitHub Pages)
│   ├── pages/
│   │   └── index.md                 # Main dashboard page (SQL + charts)
│   └── sources/prices/              # CSV data source consumed by Evidence
└── .github/
    └── workflows/
        ├── run_scraper.yml          # Daily schedule: runs scraper.py (00:00 UTC)
        ├── setup_athena.yml         # One-time manual trigger: provisions Glue/Athena
        ├── run_dbt.yml              # Daily schedule: runs dbt models (00:30 UTC)
        └── deploy_dashboard.yml     # Triggers after dbt run; builds & deploys to Pages
```

## How It Works

1. **Registry** — `product_registry.py` defines all target products and their retailer URLs in a cross-join matrix.
2. **Fetch** — `scraper.py` requests each product page, with `curl_cffi` as a browser-impersonation fallback for bot-protected sites like Best Buy.
3. **Parse** — Price data is extracted from JSON-LD structured data (`<script type="application/ld+json">`) embedded in each page. This is more stable than scraping raw HTML.
4. **Store (Bronze)** — Results are appended to a daily-partitioned JSONL file under `data/raw/` and also written to an S3 Bronze layer.
5. **Catalog** — `infrastructure/setup_athena.py` (run once) registers an AWS Glue database/external table over the Bronze S3 path so the raw JSONL can be queried directly with Athena SQL.
6. **Transform (Silver/Gold)** — dbt models in `ram_price_dbt/` read from Athena: `stg_scrapes` (Silver) filters and casts raw scrapes, and `fct_ram_prices` (Gold) adds day-over-day price deltas and a price rank within each RAM generation.
7. **Export** — `scripts/export_csv.py` queries the Gold Athena table and writes results to `dashboard/sources/prices/prices.csv` for Evidence to consume at build time.
8. **Dashboard** — Evidence builds a static site from SQL + Markdown in `dashboard/pages/` and deploys it to GitHub Pages.
9. **Orchestrate** — GitHub Actions runs the full chain daily: scraper (00:00 UTC) → dbt (00:30 UTC) → dashboard deploy (on dbt success).

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

### Scraper (Python 3.14)

```bash
git clone https://github.com/paulhoss/ram-price-pipeline.git
cd ram-price-pipeline
pip install -r requirements.txt
python scraper.py
```

### dbt (Python 3.12 — separate environment)

dbt-core does not yet officially support Python 3.14, so dbt runs in its own virtual environment:

```bash
python3.12 -m venv dbt-env
source dbt-env/bin/activate   # Windows: dbt-env\Scripts\activate
pip install dbt-core dbt-athena
cd ram_price_dbt
dbt run
dbt test
```

### Dashboard (local preview)

```bash
cd dashboard
npm install
npm run sources
npm run dev
```

**Required environment variables** (set as GitHub Secrets for Actions, or locally in a `.env` file):

| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 access (scraper) |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 access (scraper) |
| `AWS_S3_BUCKET` | Target S3 bucket name (`ram-price-tracker`) |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `DBT_AWS_ACCESS_KEY_ID` | Credentials for the dedicated `github-actions-dbt` least-privilege IAM user |
| `DBT_AWS_SECRET_ACCESS_KEY` | Credentials for the dedicated `github-actions-dbt` least-privilege IAM user |

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | Standard HTTP fetching |
| `beautifulsoup4` | HTML parsing |
| `curl_cffi` | Browser-impersonation fallback for bot-protected retailers |
| `boto3` | AWS S3/Glue/Athena client for Bronze lake writes and infrastructure setup |
| `dbt-core`, `dbt-athena` | Silver/Gold transformations over Athena (separate Python 3.12 venv) |
| `evidence` | Open-source BI framework for the dashboard (Node.js) |

## Diagnostic Tool

`json_checker.py` is a standalone script for verifying that a product page exposes JSON-LD structured data before adding it to the scraper. Run it interactively to inspect any URL:

```bash
python json_checker.py
```

## Infrastructure Notes

- **Athena/Glue** is provisioned once via `infrastructure/setup_athena.py`, triggered manually through the `setup_athena.yml` GitHub Actions workflow. It does not need to be re-run unless the Glue database/table is dropped.
- **Cost hygiene**: an S3 lifecycle rule expires the `athena-results/` query-output prefix after 7 days. Raw `raw/` Bronze data and dbt's `dbt/` output prefix are unaffected.
- **IAM**: a dedicated `github-actions-dbt` user with a least-privilege policy (Glue catalog DDL, Athena query execution, and S3 bucket/object access — including `GetBucketLocation` and `GetTableVersions`) is used for dbt runs and dashboard CSV export, separate from the scraper's credentials.
- **Free tier**: this project is designed to run entirely within AWS free tier and GitHub Actions free tier limits for personal accounts.

## Roadmap

- [x] Newegg scraping (JSON-LD)
- [x] S3 Bronze layer writes
- [x] GitHub Actions daily automation (scraper)
- [x] AWS Athena integration (query Bronze layer with SQL)
- [x] dbt models (Silver cleaning layer, Gold aggregation layer)
- [x] GitHub Actions daily automation (dbt)
- [x] Evidence dashboard (GitHub Pages)
- [ ] Best Buy scraping
- [ ] Add more retailers (Amazon, Micro Center)
- [ ] Price drop alerts

## Status

> Newegg scraping, the S3 Bronze layer, Athena/Glue cataloging, the dbt Silver/Gold transformation layer, and the Evidence dashboard deployed to GitHub Pages are all fully functional with daily automated runs. Best Buy support is in development.