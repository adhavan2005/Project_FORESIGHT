# Project FORESIGHT: Demand Forecasting & Inventory Risk Intelligence

Project FORESIGHT is an end-to-end supply chain machine learning platform that forecasts multi-week product demand, prevents high-value stockouts, identifies trapped working capital in overstock lines, and automates operational action recommendations.

---

## Repository Architecture

```text
Project_FORESIGHT/
├── data/
│   ├── raw/                 # Input CSVs: sales_daily, sku_master, calendar, inventory_snapshots
│   └── processed/           # Processed datasets: weekly_sales_master.csv, latest_inventory.csv, sku_forecast_risk_summary.csv
├── notebooks/
│   ├── 01_EDA.ipynb         # Exploratory data analysis & data quality checks (D2)
│   └── 02_baseline.ipynb    # Seasonal-naive baseline model benchmarking (D3)
├── src/                     # Core Python modules
│   ├── pipeline.py          # Reproducible data ingestion, cleaning & weekly aggregation (D1)
│   ├── features.py          # Feature engineering (lags, rolling stats, promo flags)
│   └── model.py             # ML model training, WAPE backtesting, 6W forecasting & risk scoring (D3, D4)
├── app/
│   ├── dashboard.py         # Streamlit planning dashboard for ops team (D5)
│   └── api.py               # FastAPI microservice returning 6W forecast & risk per SKU (D6)
├── docs/
│   ├── insight_memo.md      # Data-quality & EDA findings (D2)
│   └── executive_readout/   # Stakeholder presentation quantifying rupee impact (D7)
│       └── README.md
├── requirements.txt         # Exact pinned dependencies
└── README.md                # End-to-end reproduction guide
```

---

## End-to-End Reproduction Guide

Follow these exact terminal commands to execute the complete pipeline from scratch:

### 1. Environment Setup

```bash
# Navigate to the project root
cd c:\Project_FORESIGHT

# Optional: Create and activate a Python virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell / CMD

# Install pinned dependencies
pip install -r requirements.txt
```

### 2. Execute Data Pipeline (Phase 1)

Cleans raw datasets, aggregates daily transactions to weekly SKU-level demand, merges calendar and catalog attributes, and extracts latest inventory positions:

```bash
python src/pipeline.py
```

**Outputs Created:**
- `data/processed/weekly_sales_master.csv`
- `data/processed/latest_inventory.csv`

### 3. Train Model, Benchmark WAPE, & Generate Risk Scores (Phase 2)

Engineers 1w/2w/4w lags and 4w rolling stats, benchmarks seasonal-naive baseline against the Random Forest ML model, produces 6-week out-of-sample forecasts, and classifies stockout/overstock financial risks:

```bash
python src/model.py
```

**Backtest Benchmark Results:**
- Baseline Seasonal-Naive (4W Lag) WAPE: **27.70%**
- FORESIGHT Random Forest ML WAPE: **24.49%** (*+11.58% relative accuracy gain*)
- Output saved to: `data/processed/sku_forecast_risk_summary.csv`

### 4. Launch Streamlit Operations Dashboard (Phase 3)

Launches the interactive planning dashboard with KPI cards, searchable risk matrix, and historical vs. 6-week forecast charts:

```bash
streamlit run app/dashboard.py
```
Open your browser at `http://localhost:8501`.

### 5. Launch FastAPI Scoring Microservice (Phase 3)

Launches the production scoring API service on port 8000:

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

#### Test the API Endpoints:
In a separate terminal or browser:
- **Health Check:**
  ```bash
  curl http://127.0.0.1:8000/health
  ```
- **List Monitored SKUs:**
  ```bash
  curl http://127.0.0.1:8000/skus
  ```
- **Query SKU Risk & 6-Week Forecast:**
  ```bash
  curl http://127.0.0.1:8000/predict/SKU_REORDER
  curl http://127.0.0.1:8000/predict/SKU_CLEAR
  ```

---

## Business Impact & Stakeholder Reports

- **[Data Quality & EDA Insight Memo](file:///c:/Project_FORESIGHT/docs/insight_memo.md):** Detailed breakdown of top sales movers, dead stock, and promotional elasticity.
- **[Executive Readout & Rupee Impact Report](file:///c:/Project_FORESIGHT/docs/executive_readout/README.md):** Quantified financial exposure detailing ₹3,568.35 in protected sales and ₹1,599.60 in trapped capital liquidation.
