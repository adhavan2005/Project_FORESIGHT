"""Data Ingestion, Cleaning, and Aggregation Pipeline (D1).

Project FORESIGHT:
1. Ingests raw data: sales_daily, sku_master, calendar, inventory_snapshots.
2. Cleans data (missing values, types, date standardization).
3. Aggregates daily sales to weekly SKU-level demand.
4. Enriches with calendar attributes (promotions, holidays) and SKU master details.
5. Extracts latest inventory snapshot per SKU.
6. Outputs:
   - data/processed/weekly_sales_master.csv
   - data/processed/latest_inventory.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np


def load_raw_data(raw_data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all 4 raw CSV files."""
    sales_file = raw_data_dir / "sales_daily.csv"
    sku_file = raw_data_dir / "sku_master.csv"
    calendar_file = raw_data_dir / "calendar.csv"
    inventory_file = raw_data_dir / "inventory_snapshots.csv"

    for f in [sales_file, sku_file, calendar_file, inventory_file]:
        if not f.exists():
            raise FileNotFoundError(f"Missing required raw input file: {f}")

    sales_df = pd.read_csv(sales_file)
    sku_df = pd.read_csv(sku_file)
    calendar_df = pd.read_csv(calendar_file)
    inventory_df = pd.read_csv(inventory_file)

    return sales_df, sku_df, calendar_df, inventory_df


def clean_data(
    sales_df: pd.DataFrame,
    sku_df: pd.DataFrame,
    calendar_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Clean and validate raw datasets."""
    # Ensure datetime conversions
    sales_df["date"] = pd.to_datetime(sales_df["date"])
    calendar_df["date"] = pd.to_datetime(calendar_df["date"])
    inventory_df["date"] = pd.to_datetime(inventory_df["date"])

    # Clean missing values if any
    sales_df["sales_units"] = sales_df["sales_units"].fillna(0).astype(int)
    inventory_df["stock_on_hand"] = inventory_df["stock_on_hand"].fillna(0).astype(int)
    inventory_df["stock_on_order"] = inventory_df["stock_on_order"].fillna(0).astype(int)

    calendar_df["promotion_active"] = calendar_df["promotion_active"].fillna(0).astype(int)
    calendar_df["is_holiday"] = calendar_df["is_holiday"].fillna(0).astype(int)

    # Trim whitespace from string columns
    sales_df["sku_id"] = sales_df["sku_id"].astype(str).str.strip()
    sku_df["sku_id"] = sku_df["sku_id"].astype(str).str.strip()
    inventory_df["sku_id"] = inventory_df["sku_id"].astype(str).str.strip()

    return sales_df, sku_df, calendar_df, inventory_df


def build_weekly_sales_master(
    sales_df: pd.DataFrame,
    sku_df: pd.DataFrame,
    calendar_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate daily sales to weekly SKU-level demand and enrich with calendar & SKU metadata."""
    # Merge sales with calendar
    daily_merged = sales_df.merge(calendar_df, on="date", how="left")

    # Determine Monday of the week as standard week_start
    daily_merged["week_start"] = daily_merged["date"] - pd.to_timedelta(
        daily_merged["date"].dt.dayofweek, unit="D"
    )
    daily_merged["week_start"] = daily_merged["week_start"].dt.strftime("%Y-%m-%d")

    # Aggregate by SKU and week_start
    weekly = (
        daily_merged.groupby(["sku_id", "week_start"], as_index=False)
        .agg(
            weekly_sales_units=("sales_units", "sum"),
            promotion_days=("promotion_active", "sum"),
            holiday_days=("is_holiday", "sum"),
            days_recorded=("date", "nunique"),
        )
        .sort_values(by=["sku_id", "week_start"])
        .reset_index(drop=True)
    )

    # Calculate promo active flag (1 if promo was active at least 1 day in the week)
    weekly["promotion_active_week"] = (weekly["promotion_days"] > 0).astype(int)
    weekly["holiday_active_week"] = (weekly["holiday_days"] > 0).astype(int)

    # Merge SKU Master attributes
    weekly_master = weekly.merge(sku_df, on="sku_id", how="left")

    # Revenue calculations
    weekly_master["weekly_revenue"] = (
        weekly_master["weekly_sales_units"] * weekly_master["selling_price"]
    ).round(2)
    weekly_master["weekly_cogs"] = (
        weekly_master["weekly_sales_units"] * weekly_master["unit_cost"]
    ).round(2)

    return weekly_master


def extract_latest_inventory(
    inventory_df: pd.DataFrame,
    sku_df: pd.DataFrame,
) -> pd.DataFrame:
    """Extract the most recent inventory position per SKU and enrich with SKU metadata."""
    # Sort and take latest date per SKU
    latest_inv = (
        inventory_df.sort_values(by=["sku_id", "date"])
        .groupby("sku_id")
        .last()
        .reset_index()
    )

    latest_enriched = latest_inv.merge(sku_df, on="sku_id", how="left")
    latest_enriched["total_available_stock"] = (
        latest_enriched["stock_on_hand"] + latest_enriched["stock_on_order"]
    )
    latest_enriched["inventory_value_cost"] = (
        latest_enriched["stock_on_hand"] * latest_enriched["unit_cost"]
    ).round(2)
    latest_enriched["inventory_value_retail"] = (
        latest_enriched["stock_on_hand"] * latest_enriched["selling_price"]
    ).round(2)

    return latest_enriched


def run_pipeline(
    raw_dir: str = "data/raw",
    processed_dir: str = "data/processed",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute end-to-end data pipeline and write outputs."""
    raw_path = Path(raw_dir)
    proc_path = Path(processed_dir)
    proc_path.mkdir(parents=True, exist_ok=True)

    print(f"Loading raw datasets from {raw_path.resolve()}...")
    sales_df, sku_df, calendar_df, inventory_df = load_raw_data(raw_path)

    print("Cleaning and validating data...")
    sales_df, sku_df, calendar_df, inventory_df = clean_data(
        sales_df, sku_df, calendar_df, inventory_df
    )

    print("Aggregating to weekly SKU-level demand master...")
    weekly_sales_master = build_weekly_sales_master(sales_df, sku_df, calendar_df)

    print("Extracting latest inventory positions...")
    latest_inventory = extract_latest_inventory(inventory_df, sku_df)

    output_weekly = proc_path / "weekly_sales_master.csv"
    output_inv = proc_path / "latest_inventory.csv"

    weekly_sales_master.to_csv(output_weekly, index=False)
    latest_inventory.to_csv(output_inv, index=False)

    print(f"Saved: {output_weekly} ({len(weekly_sales_master)} rows)")
    print(f"Saved: {output_inv} ({len(latest_inventory)} rows)")

    return weekly_sales_master, latest_inventory


if __name__ == "__main__":
    run_pipeline()
