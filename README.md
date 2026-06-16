# RAM Price Tracker

An automated pipeline that scrapes daily RAM prices from e-commerce retailers and archives them to a local Bronze data lake.

## Overview

This project tracks the prices of 32GB DDR4 and DDR5 desktop RAM kits across retailers like Newegg (with Best Buy support in progress). A GitHub Actions workflow runs the scraper daily and commits the results back to the repository as append-only JSONL files.

## Tracked Products

| Brand | Model | Generation |
|-------|-------|------------|
| Corsair | Vengeance | DDR5 |
| G.SKILL | Ripjaws S5 | DDR5 |
| G.SKILL | Trident Z5 | DDR5 |
| Corsair | Vengeance LPX | DDR4 |
| G.SKILL | Ripjaws V | DDR4 |
| G.SKILL | Trident Z RGB | DDR4 |

## Project Structure

```
├── scraper.py              # Main scraper and pipeline orchestrator
├── product_registry.py     # Product/retailer URL matrix
├── data_lake_manager.py    # Bronze lake append logic
├── json_checker.py         # Diagnostic tool for JSON-LD verification
├── requirements.txt
├── data/
│   └── raw/                # Bronze layer — daily JSONL scrape archives
└── .github/
    └── workflows/
        └── run_scraper.yml # GitHub Actions daily schedule
```

## How It Works

1. `product_registry.py` defines all target products and their retailer URLs.
2. `scraper.py` fetches each product page and extracts price data from JSON-LD structured data (`application/ld+json`).
3. Results are appended to a daily-partitioned JSONL file under `data/raw/`.
4. GitHub Actions runs the pipeline at 15:00 UTC each day and auto-commits any new data.

## Data Format

Each line in a JSONL file represents one price observation:

```json
{
  "mpn": "CMK32GX5M2B6000C30",
  "brand": "Corsair",
  "gen": "DDR5",
  "model": "Vengeance",
  "price": 519.99,
  "currency": "USD",
  "availability": "InStock",
  "marketplace": "Newegg",
  "date": "2026-06-16",
  "pipeline_status": "Pass"
}
```

## Setup

```bash
pip install -r requirements.txt
python scraper.py
```

## Dependencies

- `requests` — standard HTTP fetching
- `beautifulsoup4` — HTML parsing
- `curl_cffi` — browser-impersonation fallback for bot-protected sites

## Status

> **Work in progress.** Newegg scraping is functional. Best Buy support is in development. Additional retailers and a Silver/Gold analytics layer are planned for future iterations.

