---
title: RAM Price Tracker
---

# RAM Price Tracker

Daily prices for 32GB (2x16GB) DDR4 and DDR5 desktop memory kits, scraped from Newegg. 
Data flows from a Python scraper → S3 Bronze layer → AWS Athena → dbt Silver/Gold → this dashboard.

_Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}_

---

```sql prices
select
    price_date,
    brand,
    model,
    gen,
    marketplace,
    price,
    price_change,
    price_change_pct,
    price_rank_within_gen
from prices.prices
order by price_date asc
```

```sql latest_prices
select
    brand,
    model,
    gen,
    marketplace,
    price,
    price_change,
    price_change_pct,
    price_rank_within_gen
from prices.prices
where price_date = (select max(price_date) from prices.prices)
order by gen desc, price asc
```

```sql ddr5_history
select
    price_date,
    brand || ' ' || model as product,
    price
from prices.prices
where gen = 'DDR5'
order by price_date asc
```

```sql ddr4_history
select
    price_date,
    brand || ' ' || model as product,
    price
from prices.prices
where gen = 'DDR4'
order by price_date asc
```

## Current Prices

<DataTable data={latest_prices} rows=10>
    <Column id="brand" title="Brand"/>
    <Column id="model" title="Model"/>
    <Column id="gen" title="Gen"/>
    <Column id="marketplace" title="Retailer"/>
    <Column id="price" title="Price (USD)" fmt="$#,##0.00"/>
    <Column id="price_change" title="1-Day Change" fmt="$+#,##0.00;$-#,##0.00"/>
    <Column id="price_change_pct" title="Change %" fmt="+0.00'%';-0.00'%'"/>
    <Column id="price_rank_within_gen" title="Rank"/>
</DataTable>

---

## DDR5 Price History

<LineChart
    data={ddr5_history}
    x=price_date
    y=price
    series=product
    title="DDR5 6000 MT/s — 32GB Kit Prices"
    yAxisTitle="Price (USD)"
    xAxisTitle="Date"
/>

---

## DDR4 Price History

<LineChart
    data={ddr4_history}
    x=price_date
    y=price
    series=product
    title="DDR4 — 32GB Kit Prices"
    yAxisTitle="Price (USD)"
    xAxisTitle="Date"
/>

---

## All Products — Price Comparison

```sql price_comparison
select
    brand || ' ' || model as product,
    gen,
    price
from prices.prices
where price_date = (select max(price_date) from prices.prices)
order by gen desc, price asc
```

<BarChart
    data={price_comparison}
    x=product
    y=price
    series=gen
    title="Current Price by Product"
    yAxisTitle="Price (USD)"
    swapXY=true
/>

---

<details>
<summary>About this project</summary>

This dashboard is part of an end-to-end data engineering portfolio project tracking RAM prices across retailers.

**Pipeline:**
- **Scraper** — Python scrapes JSON-LD structured data from retailer product pages daily via GitHub Actions
- **Bronze layer** — Raw JSONL files appended to S3 (`s3://ram-price-tracker/raw/`)
- **Athena/Glue** — AWS Glue Data Catalog exposes Bronze layer for SQL queries via Athena
- **dbt Silver** — Cleans and validates raw scrapes, casts types, filters failed runs
- **dbt Gold** — Adds day-over-day price deltas and price rankings within each DDR generation
- **Dashboard** — This Evidence app queries the Gold Athena table at build time and deploys to GitHub Pages

**Source:** [github.com/pault/ram-price-pipeline](https://github.com)

</details>
