# Project FORESIGHT: Executive Readout & Stakeholder Presentation (D7)

**Presenter:** Lead Data Scientist, Project FORESIGHT  
**Audience:** Chief Supply Chain Officer, VP of Merchandising, Head of Operations  
**Date:** September 19, 2026  

---

## 1. Executive Summary & Value Proposition

Project FORESIGHT delivers automated demand intelligence and inventory risk quantification. By shifting from static replenishment thresholds to machine learning-driven lead-time demand forecasting, the platform protects high-margin revenue and unlocks stagnant working capital:

- **Total Revenue Protected (Sales at Risk):** **₹3,568.35** across critical stockout exposures.
- **Trapped Working Capital Identified for Liquidation:** **₹1,599.60** (Cost basis) / **₹4,498.50** (Retail value).
- **Forecasting Benchmark:** Our Random Forest ML model achieved **24.49% WAPE** on backtesting, delivering an **+11.58% relative accuracy improvement** over the seasonal-naive industry baseline (27.70% WAPE).

---

## 2. Priority 1: Top SKUs to Reorder Immediately (Stockout Risk)

These SKUs have available inventory (`stock_on_hand + stock_on_order`) lower than projected demand across their respective supplier lead-time horizons. Stockout will occur within days without immediate purchase orders:

| Priority | SKU ID | Category | Lead Time | On-Hand Stock | Inbound Order | Lead Time Demand | Deficit (Units) | Selling Price (₹) | **Sales at Risk (₹)** | Immediate Action |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **`SKU_REORDER`** | Furniture | 5 Days | 20 | 0 | 33.8 | **13.8** | ₹249.99 | **₹3,442.36** | **Issue Expedited PO for 100 units** (0.42 Weeks of Supply remaining) |
| **#2** | **`SKU_WATCH`** | Textiles | 10 Days | 60 | 40 | 101.4 | **1.4** | ₹89.99 | **₹125.99** | **Confirm Inbound Delivery & Queue next batch PO** |
| *#3* | *Portfolio Ext.* | *Standard* | *—* | *—* | *—* | *—* | *—* | *—* | *—* | *System dynamically ranks up to Top 5 upon catalog expansion* |

### Business Takeaway for Reorders:
`SKU_REORDER` accounts for **96.5% of total revenue at risk**. With only 20 units in stock against a 5-day lead time demand of 33.8 units, stockout is imminent in ~3 business days. Expediting replenishment preserves high-margin furniture sales.

---

## 3. Priority 2: Top SKUs to Clear / Markdown (Overstock Risk)

These SKUs exhibit Weeks of Supply (WoS) significantly exceeding our 12-week operational holding policy, resulting in trapped working capital, warehouse carrying costs, and obsolescence risk:

| Priority | SKU ID | Category | On-Hand Stock | Weekly Forecast Demand | Weeks of Supply (WoS) | Healthy Buffer (4W) | Excess Units | Unit Cost (₹) | **Locked Capital (₹)** | Immediate Action |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **`SKU_CLEAR`** | Decor | 150 | 10.84 | **13.84 Wks** | 43.4 | **106.6** | ₹15.00 | **₹1,599.60** | **Trigger 25% Flash Sale / Clearance Markdown** |
| *#2* | *Portfolio Ext.* | *Standard* | *—* | *—* | *—* | *—* | *—* | *—* | *—* | *System dynamically ranks up to Top 5 upon catalog expansion* |

### Business Takeaway for Clearance:
`SKU_CLEAR` holds 150 units against a run rate of only 10.8 units/week. Over 106 units sit above an optimal 4-week operating buffer. Initiating a targeted promotional markdown unlocks ₹1,599.60 in cash flow and liberates warehouse footprint.

---

## 4. Balanced / Healthy Portfolio Status

| SKU ID | Category | Lead Time | On-Hand Stock | Avg Weekly Forecast | Weeks of Supply | Status | Guidance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`SKU_HEALTHY`** | Lighting | 5 Days | 50 | 39.72 | 1.26 Wks | **Healthy** | Normal replenishment cycle; supply covers lead-time demand (28.4 units). |

---

## 5. Model Performance & Validation Summary

```text
========================================================================================
MODEL EVALUATION BENCHMARK (Temporal Holdout Split: 4 Weeks)
========================================================================================
Benchmark 1: Seasonal-Naive (4-Week Lag) WAPE  : 27.70%
FORESIGHT ML Model (Random Forest Ensemble)     : 24.49%
----------------------------------------------------------------------------------------
Performance Delta                              : -3.21% absolute (-11.58% relative error)
Feature Attribution Drivers                    : Lag_1W, Rolling_Mean_4W, Promo_Flag, Month
========================================================================================
```

---

## 6. Operational Rollout & Next Steps

1. **Operations Dashboard (`app/dashboard.py`):** Planners can view live portfolio health, filter by risk category, and inspect SKU-level historical vs 6-week forecast demand curves.
2. **Scoring Microservice (`app/api.py`):** ERP/WMS systems can ingest live predictions via `/predict/{sku_id}` to trigger automated purchase orders or pricing adjustments.
3. **Weekly Automation:** Schedule `pipeline.py` and `model.py` to run weekly following Sunday night batch closes.
