"""Streamlit Planning Dashboard for Operations & Merchandise Planners (D5).

Project FORESIGHT:
- KPI cards: Total Sales at Risk (₹), Total Locked Capital (₹), Stockout SKUs, Overstock SKUs.
- Filterable & searchable SKU risk table.
- Interactive historical sales vs 6-week forecast chart per SKU.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Project FORESIGHT | Inventory & Demand Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for premium look
st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        color: white;
    }
    .status-badge-stockout {
        background-color: #ef4444;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    .status-badge-overstock {
        background-color: #f59e0b;
        color: black;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    .status-badge-healthy {
        background-color: #10b981;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load data with caching
@st.cache_data
def load_dashboard_data():
    base_dir = Path(__file__).resolve().parent.parent
    summary_path = base_dir / "data" / "processed" / "sku_forecast_risk_summary.csv"
    weekly_path = base_dir / "data" / "processed" / "weekly_sales_master.csv"

    if not summary_path.exists() or not weekly_path.exists():
        return None, None

    summary_df = pd.read_csv(summary_path)
    weekly_df = pd.read_csv(weekly_path)
    return summary_df, weekly_df


summary_df, weekly_df = load_dashboard_data()

# Header
st.title("📦 Project FORESIGHT: Inventory & Demand Risk Dashboard")
st.caption(
    "Automated Demand Forecasting, Stockout Prevention & Working Capital Optimization"
)

if summary_df is None or weekly_df is None:
    st.error(
        "Processed data not found. Please execute `python src/pipeline.py` and `python src/model.py` first."
    )
    st.stop()

# Top KPI Summary Cards
total_sales_at_risk = summary_df["sales_at_risk_inr"].sum()
total_locked_capital = summary_df["locked_capital_inr"].sum()
stockout_count = (summary_df["risk_status"] == "Stockout Risk").sum()
overstock_count = (summary_df["risk_status"] == "Overstock Risk").sum()
healthy_count = (summary_df["risk_status"] == "Healthy").sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="🚨 Total Sales at Risk (₹)",
        value=f"₹{total_sales_at_risk:,.2f}",
        delta=f"{stockout_count} SKU(s) Critical",
        delta_color="inverse",
    )
with col2:
    st.metric(
        label="🔒 Trapped Working Capital (₹)",
        value=f"₹{total_locked_capital:,.2f}",
        delta=f"{overstock_count} SKU(s) Excess",
        delta_color="inverse",
    )
with col3:
    st.metric(
        label="📦 Stockout Risk SKUs",
        value=f"{stockout_count} / {len(summary_df)}",
        help="SKUs where available stock is insufficient to cover lead time demand",
    )
with col4:
    st.metric(
        label="✅ Healthy / Balanced SKUs",
        value=f"{healthy_count} / {len(summary_df)}",
        help="SKUs operating within standard inventory boundaries",
    )

st.divider()

# Sidebar Filters
st.sidebar.header("🔍 Filters & Search")
search_query = st.sidebar.text_input("Search SKU ID or Category", "").strip()

risk_options = ["All"] + list(summary_df["risk_status"].unique())
selected_risk = st.sidebar.selectbox("Filter by Risk Status", risk_options)

category_options = ["All"] + list(summary_df["category"].unique())
selected_category = st.sidebar.selectbox("Filter by Category", category_options)

# Filter dataframe
filtered_df = summary_df.copy()
if search_query:
    filtered_df = filtered_df[
        filtered_df["sku_id"].str.contains(search_query, case=False, na=False)
        | filtered_df["category"].str.contains(search_query, case=False, na=False)
    ]
if selected_risk != "All":
    filtered_df = filtered_df[filtered_df["risk_status"] == selected_risk]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

# Main Section: Actionable SKU Table
st.subheader("📋 Prioritized Inventory Action Matrix")
st.markdown(
    "Live inventory positions, 6-week demand projections, risk classification, and financial stakes."
)

display_cols = [
    "sku_id",
    "category",
    "risk_status",
    "recommended_action",
    "sales_at_risk_inr",
    "locked_capital_inr",
    "stock_on_hand",
    "stock_on_order",
    "weeks_of_supply",
    "forecast_lead_time_demand",
    "forecast_avg_weekly",
    "forecast_total_6w",
]

# Rename columns for presentation
rename_dict = {
    "sku_id": "SKU ID",
    "category": "Category",
    "risk_status": "Risk Status",
    "recommended_action": "Action",
    "sales_at_risk_inr": "Sales at Risk (₹)",
    "locked_capital_inr": "Locked Capital (₹)",
    "stock_on_hand": "On Hand",
    "stock_on_order": "On Order",
    "weeks_of_supply": "Weeks of Supply",
    "forecast_lead_time_demand": "Lead Time Demand",
    "forecast_avg_weekly": "Avg Weekly Forecast",
    "forecast_total_6w": "Total 6W Forecast",
}

formatted_table = filtered_df[display_cols].rename(columns=rename_dict)
st.dataframe(
    formatted_table.style.format(
        {
            "Sales at Risk (₹)": "₹{:,.2f}",
            "Locked Capital (₹)": "₹{:,.2f}",
            "Weeks of Supply": "{:.2f}",
            "Lead Time Demand": "{:.1f}",
            "Avg Weekly Forecast": "{:.1f}",
            "Total 6W Forecast": "{:.1f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# Section 2: SKU Deep Dive & Historical vs Forecast Chart
st.subheader("📈 SKU Deep Dive: Historical Sales vs 6-Week Forecast")

col_sel, col_info = st.columns([1, 2])
available_skus = summary_df["sku_id"].tolist()
with col_sel:
    active_sku = st.selectbox("Select SKU for Deep Dive", available_skus)

sku_meta = summary_df[summary_df["sku_id"] == active_sku].iloc[0]

with col_info:
    badge_color = (
        "🔴"
        if sku_meta["risk_status"] == "Stockout Risk"
        else ("🟠" if sku_meta["risk_status"] == "Overstock Risk" else "🟢")
    )
    st.markdown(
        f"**{badge_color} {sku_meta['risk_status']}** | Action: **{sku_meta['recommended_action']}** | "
        f"Category: `{sku_meta['category']}` | Lead Time: `{sku_meta['lead_time_days']} days` | "
        f"Selling Price: `₹{sku_meta['selling_price']:.2f}` | Unit Cost: `₹{sku_meta['unit_cost']:.2f}`"
    )

# Prepare timeline data (18 historical weeks + 6 forecast weeks)
hist_sku = weekly_df[weekly_df["sku_id"] == active_sku].sort_values("week_start")
timeline_dates = list(hist_sku["week_start"])
hist_values = list(hist_sku["weekly_sales_units"])

last_hist_date = pd.to_datetime(timeline_dates[-1])
future_dates = [
    (last_hist_date + pd.Timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(1, 7)
]
forecast_values = [
    sku_meta[f"forecast_w{i}"] for i in range(1, 7)
]

# Combined series for Streamlit charting
all_dates = timeline_dates + future_dates
chart_df = pd.DataFrame(
    {
        "Week": all_dates,
        "Actual Sales (Historical)": hist_values + [np.nan] * len(forecast_values),
        "Demand Forecast (6-Week)": [np.nan] * (len(hist_values) - 1)
        + [hist_values[-1]]
        + forecast_values,
    }
).set_index("Week")

st.line_chart(chart_df, color=["#3b82f6", "#f97316"])

# Download Report
st.download_button(
    label="📥 Download Complete Forecast & Risk Summary (CSV)",
    data=summary_df.to_csv(index=False),
    file_name="project_foresight_sku_risk_summary.csv",
    mime="text/csv",
)
