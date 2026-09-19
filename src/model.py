"""Demand Forecasting and Risk Scoring Engine (D3, D4).

Project FORESIGHT:
1. Implements Seasonal-Naive baseline and calculates backtest WAPE.
2. Trains a supervised ML model (RandomForestRegressor) with engineered features
   strictly beating the baseline WAPE on temporal backtest.
3. Generates 6-week out-of-sample weekly demand forecast for all active SKUs.
4. Compares forecast against latest inventory positions to classify:
   - 'Stockout Risk' (if total_available_stock < forecast_lead_time_demand) -> Action: 'Reorder Now'
   - 'Overstock Risk' (if weeks_of_supply > 12) -> Action: 'Markdown/Clear'
   - 'Healthy' -> Action: 'Maintain'
5. Quantifies Rupee Impact:
   - Sales at Risk (₹) = Deficit units during lead time * selling_price
   - Locked Capital (₹) = Excess units beyond 4-week buffer * unit_cost
6. Saves summary to data/processed/sku_forecast_risk_summary.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from src.features import engineer_features



def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Weighted Absolute Percentage Error (WAPE).

    WAPE = sum(|y - y_hat|) / sum(y)
    """
    total_actual = float(np.sum(y_true))
    if total_actual == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / total_actual)


class SeasonalNaiveBaseline:
    """Seasonal-Naive baseline forecasting model using 4-week seasonal lag."""

    def __init__(self, seasonal_lag: int = 4):
        self.seasonal_lag = seasonal_lag

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict demand using the sales_lag_4w feature (or lag_1w if missing)."""
        if "sales_lag_4w" in df.columns:
            preds = df["sales_lag_4w"].fillna(df["sales_lag_1w"]).fillna(0.0)
        else:
            preds = df["sales_lag_1w"].fillna(0.0)
        return preds.values


def evaluate_models_on_backtest(
    featured_df: pd.DataFrame, test_weeks_count: int = 4
) -> Tuple[float, float, list[str]]:
    """Temporal split backtest to compare Seasonal-Naive vs ML model."""
    all_weeks = sorted(featured_df["week_start"].unique())
    test_weeks = all_weeks[-test_weeks_count:]
    train_weeks = all_weeks[:-test_weeks_count]

    # One-hot encode SKU ID
    df_encoded = pd.get_dummies(featured_df, columns=["sku_id"], drop_first=False)
    feature_cols = [
        c
        for c in df_encoded.columns
        if "sales_lag_" in c
        or "sales_rolling_" in c
        or "sku_id_" in c
        or c in ["promotion_active_week", "holiday_active_week", "month", "week_of_year"]
    ]

    train_mask = df_encoded["week_start"].isin(train_weeks)
    test_mask = df_encoded["week_start"].isin(test_weeks)

    train_data = df_encoded[train_mask].dropna(subset=["sales_lag_4w", "sales_rolling_mean_4w"]).copy()
    test_data = df_encoded[test_mask].dropna(subset=["sales_lag_4w", "sales_rolling_mean_4w"]).copy()

    # 1. Baseline evaluation
    baseline = SeasonalNaiveBaseline(seasonal_lag=4)
    baseline_preds = baseline.predict(test_data)
    baseline_wape = calculate_wape(test_data["weekly_sales_units"].values, baseline_preds)

    # 2. ML model evaluation
    ml_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=4)
    ml_model.fit(train_data[feature_cols], train_data["weekly_sales_units"])
    ml_preds = ml_model.predict(test_data[feature_cols])
    ml_wape = calculate_wape(test_data["weekly_sales_units"].values, ml_preds)

    print(f"--- Temporal Backtest (Test Horizon: {test_weeks_count} weeks) ---")
    print(f"Baseline (Seasonal-Naive 4W) WAPE: {baseline_wape:.4f} ({baseline_wape * 100:.2f}%)")
    print(f"FORESIGHT ML Model WAPE:           {ml_wape:.4f} ({ml_wape * 100:.2f}%)")
    improvement = (baseline_wape - ml_wape) / baseline_wape * 100
    print(f"Relative WAPE Improvement:         +{improvement:.2f}%")

    assert ml_wape < baseline_wape, (
        f"ML WAPE ({ml_wape:.4f}) failed to beat Baseline WAPE ({baseline_wape:.4f})"
    )

    return baseline_wape, ml_wape, feature_cols


def generate_6w_forecast(
    featured_df: pd.DataFrame,
    feature_cols: list[str],
    horizon_weeks: int = 6,
) -> pd.DataFrame:
    """Train ML model on all data and generate iterative 6-week out-of-sample forecasts."""
    df_encoded = pd.get_dummies(featured_df, columns=["sku_id"], drop_first=False)
    for col in feature_cols:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    clean_train = df_encoded.dropna(subset=["sales_lag_4w", "sales_rolling_mean_4w"]).copy()

    model = RandomForestRegressor(n_estimators=120, random_state=42, max_depth=4)
    model.fit(clean_train[feature_cols], clean_train["weekly_sales_units"])

    skus = sorted(featured_df["sku_id"].unique())
    last_week_start = pd.to_datetime(featured_df["week_start"].max())

    # Build SKU history dict
    history_dict = {
        sku: list(featured_df[featured_df["sku_id"] == sku]["weekly_sales_units"].values)
        for sku in skus
    }

    forecast_records = {sku: [] for sku in skus}

    for step in range(1, horizon_weeks + 1):
        future_week = last_week_start + pd.Timedelta(weeks=step)
        for sku in skus:
            hist = history_dict[sku]
            lag_1 = hist[-1]
            lag_2 = hist[-2]
            lag_4 = hist[-4] if len(hist) >= 4 else hist[-1]
            roll_mean = np.mean(hist[-4:])
            roll_std = np.std(hist[-4:], ddof=1) if len(hist) >= 4 else 0.0

            row_features = {
                "sales_lag_1w": lag_1,
                "sales_lag_2w": lag_2,
                "sales_lag_4w": lag_4,
                "sales_rolling_mean_4w": roll_mean,
                "sales_rolling_std_4w": roll_std,
                "promotion_active_week": 0,
                "holiday_active_week": 0,
                "month": future_week.month,
                "week_of_year": int(future_week.isocalendar().week),
            }
            for s in skus:
                row_features[f"sku_id_{s}"] = 1 if s == sku else 0

            X_step = pd.DataFrame([row_features])[feature_cols]
            pred_units = max(0.0, float(model.predict(X_step)[0]))
            forecast_records[sku].append(round(pred_units, 2))
            # Append predicted value to history for subsequent lags
            history_dict[sku].append(pred_units)

    # Format into summary dataframe
    summary_rows = []
    for sku, preds in forecast_records.items():
        row = {
            "sku_id": sku,
            "forecast_w1": preds[0],
            "forecast_w2": preds[1],
            "forecast_w3": preds[2],
            "forecast_w4": preds[3],
            "forecast_w5": preds[4],
            "forecast_w6": preds[5],
            "forecast_total_6w": round(sum(preds), 2),
            "forecast_avg_weekly": round(np.mean(preds), 2),
        }
        summary_rows.append(row)

    return pd.DataFrame(summary_rows)


def apply_risk_scoring(
    forecast_df: pd.DataFrame, latest_inv_df: pd.DataFrame
) -> pd.DataFrame:
    """Classify SKU risks, recommended actions, and rupee financial impact."""
    merged = forecast_df.merge(latest_inv_df, on="sku_id", how="left")

    # Lead time demand & weeks of supply calculations
    # Daily forecast rate = avg_weekly / 7.0
    merged["lead_time_weeks"] = (merged["lead_time_days"] / 7.0).round(2)
    merged["forecast_lead_time_demand"] = (
        (merged["forecast_avg_weekly"] / 7.0) * merged["lead_time_days"]
    ).round(2)

    merged["total_available_stock"] = (
        merged["stock_on_hand"] + merged["stock_on_order"]
    )
    merged["weeks_of_supply"] = (
        merged["stock_on_hand"] / merged["forecast_avg_weekly"].replace(0, 0.001)
    ).round(2)

    risk_statuses = []
    actions = []
    sales_at_risk_list = []
    locked_capital_list = []

    for _, row in merged.iterrows():
        total_avail = row["total_available_stock"]
        lt_demand = row["forecast_lead_time_demand"]
        wos = row["weeks_of_supply"]
        selling_price = row["selling_price"]
        unit_cost = row["unit_cost"]
        on_hand = row["stock_on_hand"]
        weekly_demand = row["forecast_avg_weekly"]

        if total_avail < lt_demand:
            risk_status = "Stockout Risk"
            action = "Reorder Now"
            # Deficit units during lead time window
            deficit_units = max(0.0, lt_demand - total_avail)
            sales_at_risk = round(deficit_units * selling_price, 2)
            locked_capital = 0.0
        elif wos > 12.0:
            risk_status = "Overstock Risk"
            action = "Markdown/Clear"
            sales_at_risk = 0.0
            # Capital tied up in inventory exceeding a 4-week operating buffer
            excess_units = max(0.0, on_hand - (weekly_demand * 4.0))
            locked_capital = round(excess_units * unit_cost, 2)
        else:
            risk_status = "Healthy"
            action = "Maintain"
            sales_at_risk = 0.0
            locked_capital = 0.0

        risk_statuses.append(risk_status)
        actions.append(action)
        sales_at_risk_list.append(sales_at_risk)
        locked_capital_list.append(locked_capital)

    merged["risk_status"] = risk_statuses
    merged["recommended_action"] = actions
    merged["sales_at_risk_inr"] = sales_at_risk_list
    merged["locked_capital_inr"] = locked_capital_list

    # Reorder columns for clean presentation
    output_cols = [
        "sku_id",
        "category",
        "risk_status",
        "recommended_action",
        "sales_at_risk_inr",
        "locked_capital_inr",
        "stock_on_hand",
        "stock_on_order",
        "total_available_stock",
        "lead_time_days",
        "forecast_lead_time_demand",
        "weeks_of_supply",
        "forecast_avg_weekly",
        "forecast_total_6w",
        "forecast_w1",
        "forecast_w2",
        "forecast_w3",
        "forecast_w4",
        "forecast_w5",
        "forecast_w6",
        "unit_cost",
        "selling_price",
    ]

    return merged[output_cols].sort_values(
        by=["sales_at_risk_inr", "locked_capital_inr"], ascending=False
    ).reset_index(drop=True)


def run_modeling_pipeline(
    processed_dir: str = "data/processed",
) -> Tuple[float, float, pd.DataFrame]:
    """Execute end-to-end model training, backtesting, forecasting, and risk scoring."""
    proc_path = Path(processed_dir)
    weekly_file = proc_path / "weekly_sales_master.csv"
    inv_file = proc_path / "latest_inventory.csv"

    if not weekly_file.exists() or not inv_file.exists():
        raise FileNotFoundError("Prerequisite processed datasets missing. Run pipeline.py first.")

    print("Loading processed master data...")
    weekly_df = pd.read_csv(weekly_file)
    latest_inv_df = pd.read_csv(inv_file)

    print("Engineering features...")
    featured_df = engineer_features(weekly_df)

    print("Running backtest evaluation (Baseline vs FORESIGHT ML)...")
    baseline_wape, ml_wape, feature_cols = evaluate_models_on_backtest(featured_df)

    print("Generating 6-week recursive out-of-sample forecast...")
    forecast_df = generate_6w_forecast(featured_df, feature_cols, horizon_weeks=6)

    print("Applying inventory risk scoring and rupee financial impact...")
    risk_summary_df = apply_risk_scoring(forecast_df, latest_inv_df)

    output_file = proc_path / "sku_forecast_risk_summary.csv"
    risk_summary_df.to_csv(output_file, index=False)
    print(f"Risk summary successfully generated at: {output_file}")
    print("\n--- SKU Forecast & Risk Summary Table ---")
    print(
        risk_summary_df[
            [
                "sku_id",
                "risk_status",
                "recommended_action",
                "sales_at_risk_inr",
                "locked_capital_inr",
                "weeks_of_supply",
            ]
        ].to_string(index=False)
    )

    return baseline_wape, ml_wape, risk_summary_df


if __name__ == "__main__":
    run_modeling_pipeline()
