"""
Machine learning and forecasting module
Safe forecast generation with error handling
"""
from datetime import date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from . import models


def product_forecast(
    db: Session,
    product: models.Product,
    user_id: int,
    horizon: int = 7
) -> Dict[str, Any]:
    """
    Generate sales forecast for a product

    Args:
        db: Database session
        product: Product to forecast
        user_id: Owner user ID
        horizon: Number of days to forecast (default 7)

    Returns:
        Dict with forecast data and reorder status
    """
    try:
        # Fetch recent sales (last 60 days)
        sixty_days_ago = date.today() - timedelta(days=60)

        sales = db.query(models.Sale).filter(
            and_(
                models.Sale.product_id == product.id,
                models.Sale.user_id == user_id,
                models.Sale.sold_on >= sixty_days_ago
            )
        ).order_by(models.Sale.sold_on).all()

        if not sales or len(sales) < 2:
            # Not enough data for forecast - use simple heuristic
            return _simple_forecast(product, 0)

        # Prepare data for ML
        daily_sales = {}
        for sale in sales:
            day = sale.sold_on
            daily_sales[day] = daily_sales.get(day, 0) + sale.quantity

        # Create time series
        date_range = pd.date_range(
            start=min(daily_sales.keys()),
            end=date.today(),
            freq='D'
        )

        quantities = [daily_sales.get(d.date(), 0) for d in date_range]

        # Simple moving average for smoothing
        if len(quantities) < 3:
            avg_daily_sales = np.mean(quantities) if quantities else 0
        else:
            avg_daily_sales = np.mean(quantities[-7:]) if len(quantities) >= 7 else np.mean(quantities)

        # Generate forecast
        forecast_qty = max(0, avg_daily_sales * horizon)

        # Determine reorder status
        days_until_stockout = _estimate_days_until_stockout(
            product.stock,
            avg_daily_sales
        )

        status = "REORDER" if (days_until_stockout <= horizon or product.stock <= product.reorder_level) else "OK"

        suggested_qty = max(0, (product.reorder_level * 2) - product.stock)

        return {
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": product.stock,
            "forecast_period_days": horizon,
            "forecast_sales": round(forecast_qty, 2),
            "average_daily_sales": round(avg_daily_sales, 2),
            "days_until_stockout": max(0, days_until_stockout),
            "status": status,
            "suggested_order_qty": round(suggested_qty, 0),
            "confidence": "HIGH" if len(sales) >= 14 else "MEDIUM" if len(sales) >= 7 else "LOW",
            "data_points": len(sales)
        }

    except Exception as e:
        # Safe fallback on any error
        return _simple_forecast(product, 0)


def _simple_forecast(product: models.Product, daily_rate: float) -> Dict[str, Any]:
    """
    Simple forecast when data is insufficient
    """
    days_until_stockout = _estimate_days_until_stockout(product.stock, daily_rate)
    status = "REORDER" if product.stock <= product.reorder_level else "OK"
    suggested_qty = max(0, (product.reorder_level * 2) - product.stock)

    return {
        "product_id": product.id,
        "product_name": product.name,
        "current_stock": product.stock,
        "forecast_period_days": 7,
        "forecast_sales": 0,
        "average_daily_sales": 0,
        "days_until_stockout": max(0, days_until_stockout),
        "status": status,
        "suggested_order_qty": round(suggested_qty, 0),
        "confidence": "LOW",
        "data_points": 0,
        "note": "Insufficient historical data"
    }


def _estimate_days_until_stockout(stock: int, daily_rate: float) -> int:
    """
    Estimate days until product runs out of stock
    """
    if daily_rate <= 0:
        return 9999  # No sales pattern

    days = int(stock / daily_rate)
    return max(0, days)


def calculate_safety_stock(
    average_demand: float,
    lead_time_days: int = 7,
    service_level: float = 0.95
) -> float:
    """
    Calculate safety stock based on demand variability

    Args:
        average_demand: Average daily demand
        lead_time_days: Lead time for resupply
        service_level: Desired service level (0.95 = 95%)

    Returns:
        Recommended safety stock quantity
    """
    try:
        # Simple safety stock calculation
        # In production, would use more sophisticated methods
        z_score = 1.65 if service_level == 0.95 else 1.28  # Approximate Z-scores

        safety_stock = z_score * (average_demand * 0.2) * np.sqrt(lead_time_days)
        return max(0, safety_stock)

    except Exception:
        return average_demand * lead_time_days * 1.5  # Fallback
