"""FastAPI Deployed Scoring Microservice (D6).

Project FORESIGHT:
Provides real-time scoring endpoints for SKU demand forecasting,
inventory risk level, recommended replenishment/markdown actions,
and quantified Rupee financial impact.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd

app = FastAPI(
    title="Project FORESIGHT Scoring Service",
    description="Operational API for SKU-level demand forecasting and inventory risk mitigation.",
    version="1.0.0",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "sku_forecast_risk_summary.csv"


class RupeeImpact(BaseModel):
    sales_at_risk_inr: float = Field(..., description="Projected lost revenue if stockout occurs (₹)")
    locked_capital_inr: float = Field(..., description="Excess capital tied up beyond operating buffer (₹)")
    currency: str = "INR"


class SKUPredictionResponse(BaseModel):
    sku_id: str
    category: str
    risk_status: str
    recommended_action: str
    weeks_of_supply: float
    stock_on_hand: int
    stock_on_order: int
    total_available_stock: int
    lead_time_days: int
    forecast_lead_time_demand: float
    forecast_avg_weekly: float
    forecast_total_6w: float
    forecast_weekly_6w: List[float]
    rupee_impact: RupeeImpact


def load_risk_data() -> pd.DataFrame:
    """Load latest generated risk summary dataset."""
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Risk summary data not found. Please run the model pipeline first."
        )
    return pd.read_csv(DATA_PATH)


@app.get("/health")
def health_check():
    """Service health verification."""
    return {"status": "healthy", "service": "Project FORESIGHT Scoring API"}


@app.get("/skus")
def list_skus():
    """Retrieve all monitored SKUs and their primary risk status."""
    df = load_risk_data()
    return {
        "count": len(df),
        "skus": df[["sku_id", "category", "risk_status", "recommended_action"]].to_dict(orient="records"),
    }


@app.get("/predict/{sku_id}", response_model=SKUPredictionResponse)
def predict_sku_risk(sku_id: str):
    """Retrieve 6-week demand forecast, inventory risk classification, recommended action, and rupee impact."""
    df = load_risk_data()
    match = df[df["sku_id"].str.upper() == sku_id.strip().upper()]

    if match.empty:
        raise HTTPException(
            status_code=404,
            detail=f"SKU '{sku_id}' not found in FORESIGHT database. Available SKUs: {list(df['sku_id'])}",
        )

    row = match.iloc[0]

    weekly_forecast = [
        float(row["forecast_w1"]),
        float(row["forecast_w2"]),
        float(row["forecast_w3"]),
        float(row["forecast_w4"]),
        float(row["forecast_w5"]),
        float(row["forecast_w6"]),
    ]

    return SKUPredictionResponse(
        sku_id=str(row["sku_id"]),
        category=str(row["category"]),
        risk_status=str(row["risk_status"]),
        recommended_action=str(row["recommended_action"]),
        weeks_of_supply=float(row["weeks_of_supply"]),
        stock_on_hand=int(row["stock_on_hand"]),
        stock_on_order=int(row["stock_on_order"]),
        total_available_stock=int(row["total_available_stock"]),
        lead_time_days=int(row["lead_time_days"]),
        forecast_lead_time_demand=float(row["forecast_lead_time_demand"]),
        forecast_avg_weekly=float(row["forecast_avg_weekly"]),
        forecast_total_6w=float(row["forecast_total_6w"]),
        forecast_weekly_6w=weekly_forecast,
        rupee_impact=RupeeImpact(
            sales_at_risk_inr=float(row["sales_at_risk_inr"]),
            locked_capital_inr=float(row["locked_capital_inr"]),
            currency="INR",
        ),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
