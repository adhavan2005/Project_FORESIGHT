# Project FORESIGHT: Data Quality & EDA Insight Memo (D2)

**Author:** Lead Data Scientist, Project FORESIGHT  
**Date:** September 19, 2026  
**Audience:** Supply Chain Leadership, Merchandise Planners, Operations Team  

---

## Executive Summary

This memorandum presents findings from the automated ingestion, audit, and exploratory analysis of 119 days of daily transaction records (`sales_daily.csv`), inventory snapshots (`inventory_snapshots.csv`), product catalog master (`sku_master.csv`), and calendar attributes (`calendar.csv`). 

The analysis reveals extreme polarization across SKU velocities and working capital allocation. While high-velocity lines face imminent stockouts that threaten revenue, slow-moving items are tying up capital in excessive inventory.

---

## Key Business Finding 1: Top Movers & Revenue Anchors

The portfolio shows strong concentration where two SKUs drive **85.4%** of total unit volume and **85.3%** of total gross revenue:

| SKU ID | Category | Total Units Sold | Total Revenue (₹) | Avg Weekly Units | Selling Price (₹) | Share of Revenue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SKU_REORDER`** | Furniture | 1,173 | ₹2,93,238.27 | 65.17 | ₹249.99 | **54.7%** |
| **`SKU_WATCH`** | Textiles | 1,817 | ₹1,63,511.83 | 100.94 | ₹89.99 | **30.5%** |
| **`SKU_HEALTHY`** | Lighting | 916 | ₹73,270.84 | 50.89 | ₹79.99 | **13.7%** |
| **`SKU_CLEAR`** | Decor | 183 | ₹5,488.17 | 10.17 | ₹29.99 | **1.0%** |
| **Total** | — | **4,089** | **₹5,35,509.11** | **227.17** | — | **100.0%** |

- **Value Leader (`SKU_REORDER`):** Generates more than half the business's total top-line revenue (₹2.93 Lakhs) at a high unit price (₹249.99). However, current stock on hand has collapsed to just **20 units**, representing only **2.1 days of supply (0.31 Weeks of Supply)** against a vendor lead time of **5 days**. This SKU is at critical stockout risk.
- **Volume Leader (`SKU_WATCH`):** The single highest-volume seller, averaging **100.94 units/week** with higher demand variance ($\sigma = 29.99$). Stock on hand is 60 units with 40 on order, which is precarious given its extended 10-day lead time.

---

## Key Business Finding 2: Dead Stock & Trapped Working Capital

`SKU_CLEAR` (Decor) exhibits classic dead-stock / overstock symptoms:
- **Velocity:** Sells only **10.17 units per week** (averaging ~1.45 units/day).
- **Inventory Position:** Current stock on hand is **150 units** with 0 on order.
- **Weeks of Supply (WoS):** **14.75 weeks** of supply (over 103 days of cover).
- **Working Capital Lockup:** Traps **₹2,250.00 at cost** and **₹4,498.50 in retail inventory value**.
- **Assessment:** Exceeds the standard 12-week operational ceiling. Without aggressive markdowns or bundling, this inventory will remain stagnant, incurring holding costs and shelf-space penalties.

---

## Key Business Finding 3: Seasonality & Promotional Sensitivity

Examining daily demand cadence and calendar metadata indicates marked seasonal patterns:
1. **Weekend Surges:**
   - `SKU_REORDER` (Furniture) increases by **+27.4%** on Sundays (10.94 units/day) compared to mid-week troughs (8.59 units on Wednesdays).
   - `SKU_HEALTHY` (Lighting) reaches peak velocity on Saturdays (8.24 units/day) and Sundays (8.06 units/day).
2. **Promotional Responsiveness:**
   - `SKU_HEALTHY` shows significant promotional elasticity with a **+10.8% sales lift** during promotion-active weeks (52.31 units/week vs 47.20 units in non-promo weeks).
   - `SKU_REORDER` gains a **+6.6% lift** (66.31 units/week vs 62.20 units).
   - Conversely, `SKU_CLEAR` shows negligible promo lift (+5.2% on a tiny base), reinforcing that price elasticity alone without deep clearance mechanics will not liquidate the surplus.

---

## Strategic Recommendations for Next Phases

1. **Immediate Reorder Protocol:** Immediately trigger replenishment for `SKU_REORDER` to avoid catastrophic lost sales on our highest-margin product.
2. **Automated Markdown Activation:** Institute an automated clearance cadence for `SKU_CLEAR` to recover at least 70–80% of unit cost into free cash flow.
3. **Model Architecture:** Demand forecasting must account for calendar promotional flags and weekly lags to capture the cyclical momentum identified above.
