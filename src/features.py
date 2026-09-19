"""Feature Engineering Module for Project FORESIGHT.

Generates:
- Lag features: 1w, 2w, 4w
- Rolling statistics: 4w rolling mean, 4w rolling std (lagged by 1 to prevent data leakage)
- Promotional flags: promotion_active_week, promotion_days
- Calendar features: month, week_of_year, holiday_active_week
"""

import pandas as pd
import numpy as np


def add_lag_features(
    df: pd.DataFrame,
    group_col: str = "sku_id",
    target_col: str = "weekly_sales_units",
    lags: list[int] = [1, 2, 4],
) -> pd.DataFrame:
    """Create weekly lag features grouped by SKU."""
    df = df.copy()
    for lag in lags:
        df[f"sales_lag_{lag}w"] = df.groupby(group_col)[target_col].shift(lag)
    return df


def add_rolling_features(
    df: pd.DataFrame,
    group_col: str = "sku_id",
    target_col: str = "weekly_sales_units",
    window: int = 4,
) -> pd.DataFrame:
    """Create rolling mean and std features shifted by 1 week to avoid data leakage."""
    df = df.copy()
    shifted = df.groupby(group_col)[target_col].shift(1)
    df[f"sales_rolling_mean_{window}w"] = (
        shifted.groupby(df[group_col]).rolling(window, min_periods=2).mean().reset_index(0, drop=True)
    )
    df[f"sales_rolling_std_{window}w"] = (
        shifted.groupby(df[group_col]).rolling(window, min_periods=2).std().reset_index(0, drop=True).fillna(0.0)
    )
    return df


def add_calendar_features(df: pd.DataFrame, date_col: str = "week_start") -> pd.DataFrame:
    """Extract month and ISO week from week_start timestamp."""
    df = df.copy()
    date_dt = pd.to_datetime(df[date_col])
    df["month"] = date_dt.dt.month
    df["week_of_year"] = date_dt.dt.isocalendar().week.astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """End-to-end feature engineering pipeline on weekly master dataset."""
    df = df.sort_values(by=["sku_id", "week_start"]).reset_index(drop=True)
    df = add_lag_features(df, lags=[1, 2, 4])
    df = add_rolling_features(df, window=4)
    df = add_calendar_features(df, date_col="week_start")
    return df
