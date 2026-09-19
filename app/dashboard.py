"""Project FORESIGHT - Executive Demand Forecasting & Inventory Risk Intelligence Hub.

Phase 3 UI/UX Upgrade:
- Premium Glassmorphism & Modern Typography (Inter / Plus Jakarta Sans)
- Real-time KPI Metric Deck with financial risk indicators
- 4 Focused Interactive Tabs:
    1. Executive Command Center & Prioritized Risk Matrix
    2. SKU Deep Dive & Altair Multi-Layer Forecast Timeline
    3. Interactive What-If Scenario & Sensitivity Simulator
    4. Action Dispatcher & Automated Purchase Order Generator
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Project FORESIGHT | Inventory Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# DESIGN SYSTEM & CUSTOM CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Gradient Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.98rem;
        font-weight: 400;
        margin-bottom: 12px;
    }
    .engine-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* KPI Deck Cards */
    .kpi-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        margin-bottom: 6px;
        color: #f8fafc;
    }
    .kpi-value-danger {
        color: #f87171;
    }
    .kpi-value-warning {
        color: #fbbf24;
    }
    .kpi-value-success {
        color: #34d399;
    }
    .kpi-subtext {
        font-size: 0.82rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Status Pills */
    .pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        text-align: center;
    }
    .pill-stockout {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .pill-overstock {
        background: rgba(245, 158, 11, 0.15);
        color: #fde68a;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .pill-healthy {
        background: rgba(16, 185, 129, 0.15);
        color: #a7f3d0;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    /* Section Headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 12px;
        margin-bottom: 4px;
    }
    .section-desc {
        font-size: 0.88rem;
        color: #94a3b8;
        margin-bottom: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# DATA INGESTION & CACHING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent
    summary_path = base_dir / "data" / "processed" / "sku_forecast_risk_summary.csv"
    weekly_path = base_dir / "data" / "processed" / "weekly_sales_master.csv"
    inv_path = base_dir / "data" / "processed" / "latest_inventory.csv"

    if not summary_path.exists() or not weekly_path.exists():
        return None, None, None

    summary_df = pd.read_csv(summary_path)
    weekly_df = pd.read_csv(weekly_path)
    inv_df = pd.read_csv(inv_path) if inv_path.exists() else None
    return summary_df, weekly_df, inv_df


summary_df, weekly_df, inv_df = load_data()

if summary_df is None or weekly_df is None:
    st.error("Processed data missing. Please run `python src/pipeline.py` and `python src/model.py` first.")
    st.stop()

# -----------------------------------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">⚡ Project FORESIGHT: Inventory & Demand Intelligence</div>
        <div class="hero-subtitle">
            Autonomous Machine Learning Demand Forecasting, Lead-Time Runout Detection & Working Capital Optimization
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
            <div class="engine-badge">● Engine Online: Random Forest ML (WAPE: 24.49% | +11.58% vs Baseline)</div>
            <div style="color: #64748b; font-size: 0.8rem;">• Data Horizon: 119 Historical Days • 6-Week Out-of-Sample Forecast Horizon</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# EXECUTIVE KPI DECK
# -----------------------------------------------------------------------------
total_sales_at_risk = summary_df["sales_at_risk_inr"].sum()
total_locked_capital = summary_df["locked_capital_inr"].sum()
stockout_skus = summary_df[summary_df["risk_status"] == "Stockout Risk"]
overstock_skus = summary_df[summary_df["risk_status"] == "Overstock Risk"]
healthy_skus = summary_df[summary_df["risk_status"] == "Healthy"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">🚨 Sales Revenue at Risk</div>
            <div class="kpi-value kpi-value-danger">₹{total_sales_at_risk:,.2f}</div>
            <div class="kpi-subtext">
                <span style="color:#ef4444; font-weight:700;">{len(stockout_skus)} SKU(s)</span> facing stockout during lead time
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">🔒 Trapped Working Capital</div>
            <div class="kpi-value kpi-value-warning">₹{total_locked_capital:,.2f}</div>
            <div class="kpi-subtext">
                <span style="color:#f59e0b; font-weight:700;">{len(overstock_skus)} SKU(s)</span> exceeding 12-week holding ceiling
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    imminent_sku_name = stockout_skus.sort_values(by="sales_at_risk_inr", ascending=False).iloc[0]["sku_id"] if len(stockout_skus) > 0 else "None"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">⚡ Most Critical SKU</div>
            <div class="kpi-value" style="font-size:1.6rem; color:#38bdf8;">{imminent_sku_name}</div>
            <div class="kpi-subtext">
                Requires immediate replenishment PO
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    health_pct = (len(healthy_skus) / len(summary_df)) * 100
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">🛡️ Portfolio Balance Score</div>
            <div class="kpi-value kpi-value-success">{health_pct:.0f}%</div>
            <div class="kpi-subtext">
                {len(healthy_skus)} of {len(summary_df)} SKUs within target 1–12 WoS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# -----------------------------------------------------------------------------
# TABBED INTERFACE
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Command Center & Risk Matrix",
    "📈 Demand Forecast & SKU Deep Dive",
    "🧪 What-If Scenario Simulator",
    "📝 Purchase Order & Action Dispatcher"
])

# =============================================================================
# TAB 1: COMMAND CENTER & PRIORITIZED RISK MATRIX
# =============================================================================
with tab1:
    st.markdown('<div class="section-title">Operational Risk Prioritization Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Real-time inventory levels evaluated against machine learning 6-week demand projections and supplier lead times.</div>', unsafe_allow_html=True)

    # Filter Controls
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search = st.text_input("🔍 Search by SKU or Category", placeholder="e.g. SKU_REORDER or Furniture").strip()
    with f_col2:
        risk_filter = st.selectbox("Filter Risk Status", ["All"] + list(summary_df["risk_status"].unique()))
    with f_col3:
        cat_filter = st.selectbox("Filter Category", ["All"] + list(summary_df["category"].unique()))

    # Apply filters
    view_df = summary_df.copy()
    if search:
        view_df = view_df[
            view_df["sku_id"].str.contains(search, case=False, na=False) |
            view_df["category"].str.contains(search, case=False, na=False)
        ]
    if risk_filter != "All":
        view_df = view_df[view_df["risk_status"] == risk_filter]
    if cat_filter != "All":
        view_df = view_df[view_df["category"] == cat_filter]

    # Visual Financial Exposure Breakdown
    ch_col1, ch_col2 = st.columns(2)
    with ch_col1:
        st.markdown("**Sales Revenue at Risk by SKU (₹)**")
        risk_bar = (
            alt.Chart(view_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("sku_id:N", title="SKU ID", sort="-y"),
                y=alt.Y("sales_at_risk_inr:Q", title="Sales at Risk (₹)"),
                color=alt.Color(
                    "risk_status:N",
                    scale=alt.Scale(
                        domain=["Stockout Risk", "Overstock Risk", "Healthy"],
                        range=["#ef4444", "#f59e0b", "#10b981"],
                    ),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("sku_id:N", title="SKU"),
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("sales_at_risk_inr:Q", title="Sales at Risk (₹)", format=",.2f"),
                    alt.Tooltip("recommended_action:N", title="Action"),
                ],
            )
            .properties(height=220)
        )
        st.altair_chart(risk_bar, use_container_width=True)

    with ch_col2:
        st.markdown("**Weeks of Supply (WoS) vs 12-Week Policy Ceiling**")
        wos_bar = (
            alt.Chart(view_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("sku_id:N", title="SKU ID", sort="-y"),
                y=alt.Y("weeks_of_supply:Q", title="Weeks of Supply (WoS)"),
                color=alt.condition(
                    alt.datum.weeks_of_supply > 12,
                    alt.value("#f59e0b"),
                    alt.condition(alt.datum.weeks_of_supply < 1.0, alt.value("#ef4444"), alt.value("#10b981")),
                ),
                tooltip=[
                    alt.Tooltip("sku_id:N", title="SKU"),
                    alt.Tooltip("weeks_of_supply:Q", title="Weeks of Supply", format=".2f"),
                    alt.Tooltip("stock_on_hand:Q", title="Stock On Hand"),
                    alt.Tooltip("forecast_avg_weekly:Q", title="Avg Weekly Demand", format=".1f"),
                ],
            )
            .properties(height=220)
        )
        rule = alt.Chart(pd.DataFrame({"y": [12.0]})).mark_rule(color="#ef4444", strokeDash=[4, 4]).encode(y="y:Q")
        st.altair_chart(wos_bar + rule, use_container_width=True)

    # Detailed Interactive Table
    table_cols = [
        "sku_id", "category", "risk_status", "recommended_action",
        "sales_at_risk_inr", "locked_capital_inr", "stock_on_hand", "stock_on_order",
        "weeks_of_supply", "lead_time_days", "forecast_lead_time_demand", "forecast_avg_weekly", "forecast_total_6w"
    ]
    rename_map = {
        "sku_id": "SKU ID",
        "category": "Category",
        "risk_status": "Risk Status",
        "recommended_action": "Action Required",
        "sales_at_risk_inr": "Sales at Risk (₹)",
        "locked_capital_inr": "Locked Capital (₹)",
        "stock_on_hand": "Stock On Hand",
        "stock_on_order": "Inbound Order",
        "weeks_of_supply": "Weeks of Supply",
        "lead_time_days": "Lead Time (Days)",
        "forecast_lead_time_demand": "Lead Time Demand",
        "forecast_avg_weekly": "Avg Weekly Forecast",
        "forecast_total_6w": "6-Week Forecast Total",
    }
    styled_df = view_df[table_cols].rename(columns=rename_map)

    st.dataframe(
        styled_df.style.format({
            "Sales at Risk (₹)": "₹{:,.2f}",
            "Locked Capital (₹)": "₹{:,.2f}",
            "Weeks of Supply": "{:.2f} wks",
            "Lead Time Demand": "{:.1f} units",
            "Avg Weekly Forecast": "{:.1f} units",
            "6-Week Forecast Total": "{:.1f} units",
        }),
        use_container_width=True,
        hide_index=True,
    )

# =============================================================================
# TAB 2: DEMAND FORECAST & SKU DEEP DIVE
# =============================================================================
with tab2:
    st.markdown('<div class="section-title">SKU Demand Trajectory & 6-Week Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Interactive timeline contrasting 18 weeks of historical actuals against machine learning forecasts with lead-time demand markers.</div>', unsafe_allow_html=True)

    sku_select_col, sku_card_col = st.columns([1, 3])
    with sku_select_col:
        selected_sku = st.selectbox("Select Target SKU", summary_df["sku_id"].tolist())

    sku_data = summary_df[summary_df["sku_id"] == selected_sku].iloc[0]

    with sku_card_col:
        badge_style = (
            "pill-stockout" if sku_data["risk_status"] == "Stockout Risk"
            else ("pill-overstock" if sku_data["risk_status"] == "Overstock Risk" else "pill-healthy")
        )
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <span class="pill {badge_style}">{sku_data['risk_status']}</span>
                    <span style="font-weight:700; font-size:1.1rem; margin-left:10px; color:#f8fafc;">{sku_data['sku_id']} ({sku_data['category']})</span>
                    <span style="color:#94a3b8; font-size:0.85rem; margin-left:12px;">Action: <strong>{sku_data['recommended_action']}</strong></span>
                </div>
                <div style="display:flex; gap:18px; font-size:0.85rem; color:#cbd5e1;">
                    <div>Lead Time: <strong>{sku_data['lead_time_days']}d</strong></div>
                    <div>Price: <strong>₹{sku_data['selling_price']:.2f}</strong></div>
                    <div>Cost: <strong>₹{sku_data['unit_cost']:.2f}</strong></div>
                    <div>Stock: <strong>{sku_data['stock_on_hand']} units</strong></div>
                    <div>WoS: <strong>{sku_data['weeks_of_supply']:.2f} wks</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Prepare timeline dataframe
    hist_sku = weekly_df[weekly_df["sku_id"] == selected_sku].sort_values("week_start").copy()
    hist_sku["type"] = "Historical Actual"
    hist_sku["revenue"] = hist_sku["weekly_sales_units"] * sku_data["selling_price"]
    hist_sku["date"] = pd.to_datetime(hist_sku["week_start"])

    # Future dates
    last_date = hist_sku["date"].max()
    future_rows = []
    for step in range(1, 7):
        f_date = last_date + pd.Timedelta(weeks=step)
        f_units = float(sku_data[f"forecast_w{step}"])
        future_rows.append({
            "week_start": f_date.strftime("%Y-%m-%d"),
            "weekly_sales_units": f_units,
            "type": "ML Forecast",
            "revenue": f_units * sku_data["selling_price"],
            "date": f_date,
        })
    future_df = pd.DataFrame(future_rows)

    combined_timeline = pd.concat([
        hist_sku[["week_start", "weekly_sales_units", "type", "revenue", "date"]],
        future_df
    ], ignore_index=True)

    # Multi-Layer Altair Chart
    base = alt.Chart(combined_timeline).encode(
        x=alt.X("week_start:N", title="Week Starting (Monday)", axis=alt.Axis(labelAngle=-45)),
    )

    # Historical Area
    hist_chart = (
        alt.Chart(combined_timeline[combined_timeline["type"] == "Historical Actual"])
        .mark_area(
            line={"color": "#38bdf8", "width": 2.5},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="rgba(56, 189, 248, 0.35)", offset=0),
                    alt.GradientStop(color="rgba(56, 189, 248, 0.02)", offset=1),
                ],
                x1=1, x2=1, y1=1, y2=0,
            ),
            point=alt.OverlayMarkDef(color="#38bdf8", size=45),
        )
        .encode(
            x=alt.X("week_start:N", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("weekly_sales_units:Q", title="Demand (Units)"),
            tooltip=[
                alt.Tooltip("week_start:N", title="Week"),
                alt.Tooltip("weekly_sales_units:Q", title="Actual Units", format=".0f"),
                alt.Tooltip("revenue:Q", title="Revenue (₹)", format=",.2f"),
                alt.Tooltip("type:N", title="Series"),
            ],
        )
    )

    # Forecast Line with dashes
    fc_chart = (
        alt.Chart(combined_timeline[combined_timeline["type"] == "ML Forecast"])
        .mark_line(
            strokeDash=[5, 5],
            color="#f97316",
            strokeWidth=3,
            point=alt.OverlayMarkDef(color="#f97316", size=55, filled=True),
        )
        .encode(
            x=alt.X("week_start:N"),
            y=alt.Y("weekly_sales_units:Q"),
            tooltip=[
                alt.Tooltip("week_start:N", title="Forecast Week"),
                alt.Tooltip("weekly_sales_units:Q", title="Projected Units", format=".1f"),
                alt.Tooltip("revenue:Q", title="Projected Revenue (₹)", format=",.2f"),
                alt.Tooltip("type:N", title="Series"),
            ],
        )
    )

    # Vertical Forecast Horizon Divider
    split_date = last_date.strftime("%Y-%m-%d")
    split_rule = (
        alt.Chart(pd.DataFrame({"split": [split_date]}))
        .mark_rule(color="#94a3b8", strokeDash=[3, 3], strokeWidth=1.5)
        .encode(x="split:N")
    )

    full_chart = (hist_chart + fc_chart + split_rule).properties(height=380)
    st.altair_chart(full_chart, use_container_width=True)

    # Weekly Forecast Breakdown & Runout Metric
    brk_col1, brk_col2 = st.columns([2, 1])
    with brk_col1:
        st.markdown("**6-Week Detailed Weekly Demand Projections**")
        w_bars = (
            alt.Chart(future_df)
            .mark_bar(color="#f97316", cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("week_start:N", title="Forecast Week"),
                y=alt.Y("weekly_sales_units:Q", title="Demand (Units)"),
                tooltip=[
                    alt.Tooltip("week_start:N", title="Week"),
                    alt.Tooltip("weekly_sales_units:Q", title="Forecast Demand", format=".1f"),
                    alt.Tooltip("revenue:Q", title="Forecast Revenue (₹)", format=",.2f"),
                ],
            )
            .properties(height=180)
        )
        st.altair_chart(w_bars, use_container_width=True)

    with brk_col2:
        st.markdown("**Inventory Runout Timeline**")
        daily_rate = sku_data["forecast_avg_weekly"] / 7.0
        days_left = sku_data["stock_on_hand"] / max(daily_rate, 0.001)
        lt_days = sku_data["lead_time_days"]

        st.metric("Days of Stock Remaining", f"{days_left:.1f} days", delta=f"{days_left - lt_days:.1f}d buffer vs lead time", delta_color="normal" if days_left >= lt_days else "inverse")
        if days_left < lt_days:
            st.error(f"⚠️ Stockout projected in {days_left:.1f} days! Replenishment takes {lt_days} days. Order immediately.")
        elif days_left > 84:
            st.warning(f"📦 Stagnant stock: Holds {days_left:.0f} days of cover (>84-day ceiling). Activate markdown.")
        else:
            st.success("✅ Stock levels comfortably cover vendor replenishment window.")

# =============================================================================
# TAB 3: WHAT-IF SCENARIO & SENSITIVITY SIMULATOR
# =============================================================================
with tab3:
    st.markdown('<div class="section-title">🧪 Interactive Replenishment & What-If Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Simulate how supplier delays, promotional surges, or expedited POs alter lead-time coverage and rupee financial risk in real time.</div>', unsafe_allow_html=True)

    sim_sku_select = st.selectbox("Select SKU to Simulate", summary_df["sku_id"].tolist(), key="sim_sku")
    sim_base = summary_df[summary_df["sku_id"] == sim_sku_select].iloc[0]

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        lead_time_delta = st.slider("Supplier Lead Time Delta (Days)", -3, 14, 0, help="Adjust for supplier delay or expedited shipping")
    with sim_col2:
        promo_multiplier = st.slider("Promotional Demand Multiplier", 0.5, 2.5, 1.0, step=0.1, help="Simulate marketing campaign or flash sale surge")
    with sim_col3:
        sim_po_units = st.number_input("Simulated New Inbound Order (Units)", min_value=0, max_value=500, value=0, step=10)

    # Dynamic Simulation Calculations
    effective_lead_time = max(1, sim_base["lead_time_days"] + lead_time_delta)
    effective_weekly_demand = sim_base["forecast_avg_weekly"] * promo_multiplier
    effective_daily_rate = effective_weekly_demand / 7.0
    effective_lead_time_demand = effective_daily_rate * effective_lead_time
    effective_total_stock = sim_base["stock_on_hand"] + sim_base["stock_on_order"] + sim_po_units
    effective_wos = sim_base["stock_on_hand"] / max(effective_weekly_demand, 0.001)

    # Recalculate Risk
    if effective_total_stock < effective_lead_time_demand:
        sim_risk = "Stockout Risk"
        sim_action = "Expedite Reorder Immediately"
        sim_deficit = max(0.0, effective_lead_time_demand - effective_total_stock)
        sim_sales_at_risk = sim_deficit * sim_base["selling_price"]
        sim_locked_cap = 0.0
    elif effective_wos > 12.0:
        sim_risk = "Overstock Risk"
        sim_action = "Apply Clearance Markdown"
        sim_sales_at_risk = 0.0
        sim_locked_cap = max(0.0, sim_base["stock_on_hand"] - (effective_weekly_demand * 4.0)) * sim_base["unit_cost"]
    else:
        sim_risk = "Healthy"
        sim_action = "Maintain Normal Cadence"
        sim_sales_at_risk = 0.0
        sim_locked_cap = 0.0

    st.write("")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    with res_col1:
        st.metric("Simulated Risk Status", sim_risk, delta="Resolved" if sim_risk == "Healthy" and sim_base["risk_status"] != "Healthy" else None)
    with res_col2:
        st.metric("Lead Time Demand", f"{effective_lead_time_demand:.1f} units", delta=f"{effective_lead_time_demand - sim_base['forecast_lead_time_demand']:+.1f} units")
    with res_col3:
        st.metric("Available Stock (with PO)", f"{effective_total_stock} units", delta=f"+{sim_po_units} PO units" if sim_po_units > 0 else None)
    with res_col4:
        st.metric("Sales at Risk (₹)", f"₹{sim_sales_at_risk:,.2f}", delta=f"{sim_sales_at_risk - sim_base['sales_at_risk_inr']:+,.2f}", delta_color="inverse")

    if sim_risk == "Healthy":
        st.success(f"🎉 **Simulation Success**: Adding **{sim_po_units} units** under **{effective_lead_time} days lead time** resolves stockout risk completely!")
    elif sim_risk == "Stockout Risk":
        st.error(f"⚠️ **Still at Risk**: Deficit of **{effective_lead_time_demand - effective_total_stock:.1f} units** persists. Recommend increasing inbound order to at least **{int(np.ceil(effective_lead_time_demand - (sim_base['stock_on_hand'] + sim_base['stock_on_order'])))} units**.")

# =============================================================================
# TAB 4: ACTION DISPATCHER & PO GENERATOR
# =============================================================================
with tab4:
    st.markdown('<div class="section-title">📝 Operational Action Dispatcher & Purchase Order Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Automatically formatted purchase orders and markdown clearance plans ready for procurement and merchandising execution.</div>', unsafe_allow_html=True)

    po_records = []
    for _, r in stockout_skus.iterrows():
        # Suggested PO = Deficit during lead time + 4 weeks operating safety stock
        safety_stock = r["forecast_avg_weekly"] * 4.0
        recommended_order_qty = int(np.ceil((r["forecast_lead_time_demand"] - r["total_available_stock"]) + safety_stock))
        estimated_cost = recommended_order_qty * r["unit_cost"]

        po_records.append({
            "PO Number": f"PO-2026-{r['sku_id'][:6]}",
            "SKU ID": r["sku_id"],
            "Category": r["category"],
            "Urgency": "CRITICAL (High Stockout Risk)",
            "Recommended Order Qty": recommended_order_qty,
            "Supplier Lead Time": f"{r['lead_time_days']} Days",
            "Unit Cost (₹)": f"₹{r['unit_cost']:.2f}",
            "Estimated Total Cost (₹)": f"₹{estimated_cost:,.2f}",
        })

    if po_records:
        st.markdown("### 🛒 Recommended Replenishment Purchase Orders")
        po_df = pd.DataFrame(po_records)
        st.dataframe(po_df, use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 Export Replenishment Purchase Orders (CSV)",
            data=po_df.to_csv(index=False),
            file_name="project_foresight_purchase_orders.csv",
            mime="text/csv",
        )
    else:
        st.info("No active replenishment purchase orders required. All SKUs have sufficient stock.")

    st.divider()

    # Markdown Clearance Dispatch
    if len(overstock_skus) > 0:
        st.markdown("### 🏷️ Recommended Clearance Markdown Plan")
        clear_records = []
        for _, r in overstock_skus.iterrows():
            excess_units = max(0, r["stock_on_hand"] - int(r["forecast_avg_weekly"] * 4))
            clear_records.append({
                "SKU ID": r["sku_id"],
                "Category": r["category"],
                "Current Stock": r["stock_on_hand"],
                "Weeks of Supply": f"{r['weeks_of_supply']:.1f} wks",
                "Excess Units (>4W Buffer)": excess_units,
                "Current Price": f"₹{r['selling_price']:.2f}",
                "Recommended Promo Price (25% Off)": f"₹{r['selling_price'] * 0.75:.2f}",
                "Projected Working Capital Liberated": f"₹{excess_units * r['unit_cost']:,.2f}",
            })
        clear_df = pd.DataFrame(clear_records)
        st.dataframe(clear_df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 📥 Full System Export")
    st.download_button(
        label="📥 Download Complete FORESIGHT Risk & Forecast Summary (CSV)",
        data=summary_df.to_csv(index=False),
        file_name="project_foresight_sku_risk_summary.csv",
        mime="text/csv",
    )
