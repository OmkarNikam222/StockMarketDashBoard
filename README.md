# Stock Market Dashboard

An end-to-end mini data engineering + visualization project in Python.

You start with a messy CSV of daily stock data and finish with an interactive Streamlit dashboard that shows price trends, sector breakdowns, risk/return profiles, and multi-ticker comparisons — all powered by a reproducible data pipeline.

---

## 🔍 Overview

This project covers the full workflow:

- **Raw CSV → Cleaned Parquet**
- **Cleaned Parquet → Aggregated analytics tables**
- **Aggregates → Interactive Streamlit web app**

It’s designed as a portfolio-friendly example for:
- Data wrangling and schema normalization  
- Basic time-series / returns analytics  
- Building interactive dashboards with filters and multiple charts  

---

## 🚀 Core Highlights

- **Automated Data Cleaning**
  - Normalizes column names and types  
  - Fixes date formats to `YYYY-MM-DD`  
  - Standardizes missing values (e.g., `"", "NA", "N/A", "null", "-"`)  
  - Removes duplicate rows and inconsistent records  
  - Saves a clean dataset as `data/cleaned.parquet`

- **Data Aggregations (Parquet-based)**
  - `agg1.parquet`: daily **average close price** by ticker  
  - `agg2.parquet`: **average volume** by sector  
  - `agg3.parquet`: **daily returns** by ticker  

- **Interactive Dashboard (Streamlit)**
  - Sidebar filters:
    - Ticker selector (detailed view)
    - Multi-ticker selection (comparison)
    - Date range picker
    - Light / Dark **theme toggle**
  - Main charts:
    - Line chart: daily average close price (per ticker)
    - Bar chart: average volume by sector
    - Pie chart: sector-wise volume share
    - Line chart: daily returns with range slider
    - Histogram: distribution of daily returns
    - Multi-ticker line chart: daily average close price by ticker
    - Box plot: daily return distribution per ticker (volatility)
    - Sankey diagram: **sector → ticker** flow (if sector info is available at ticker level)
  - Numeric comparison table:
    - Avg close, avg daily return, volatility (std of returns), trading days per ticker

- **Lightweight & Reproducible**
  - Uses Parquet for efficient storage  
  - Clear scripts (`stock_cleaning.py`, `stock_aggregations.py`, `app.py`)  
  - Easy to re-run end-to-end on a new CSV

---

## 📁 Project Structure

```text
.
├── data/
│   ├── stock_market.csv        # Raw input CSV (not committed, usually)
│   ├── cleaned.parquet         # Cleaned dataset
│   ├── agg1.parquet            # Daily avg close by ticker
│   ├── agg2.parquet            # Avg volume by sector
│   └── agg3.parquet            # Daily returns by ticker
├── app.py                      # Streamlit dashboard
├── stock_cleaning.py           # Cleaning + schema normalization
├── stock_aggregations.py       # Aggregation scripts (agg1/agg2/agg3)
└── README.md
