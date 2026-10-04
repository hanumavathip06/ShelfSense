"""
Dynamic Reorder Point Optimizer for ShelfSense ML Pipeline.

Replaces static reorder thresholds with data-driven dynamic calculations
using Economic Order Quantity (EOQ) principles:

    Reorder Point = (Average Daily Demand × Lead Time) + Safety Stock
    Safety Stock  = Z × σ_demand × √Lead Time

Where Z is the service level Z-score (e.g., 1.65 for 95% service level).
"""

import math
import numpy as np
from scipy import stats


# Z-scores for common service levels
SERVICE_LEVEL_Z = {
    0.80: 0.842,
    0.85: 1.036,
    0.90: 1.282,
    0.95: 1.645,
    0.97: 1.881,
    0.99: 2.326
}


def get_z_score(service_level):
    """
    Get the Z-score for a given service level.
    Uses lookup table for common values, falls back to ppf calculation.
    
    Args:
        service_level: Float between 0 and 1 (e.g., 0.95)
        
    Returns:
        Z-score value
    """
    if service_level in SERVICE_LEVEL_Z:
        return SERVICE_LEVEL_Z[service_level]
    return stats.norm.ppf(service_level)


def calculate_demand_statistics(daily_demands):
    """
    Calculate demand statistics from historical daily demand data.
    
    Args:
        daily_demands: Array-like of daily demand values
        
    Returns:
        dict with avg_daily_demand, std_daily_demand, total_days
    """
    demands = np.array(daily_demands, dtype=np.float64)
    demands = demands[demands >= 0]  # Remove any negative values
    
    if len(demands) == 0:
        return {
            'avg_daily_demand': 0,
            'std_daily_demand': 0,
            'total_days': 0
        }
    
    return {
        'avg_daily_demand': round(float(np.mean(demands)), 4),
        'std_daily_demand': round(float(np.std(demands)), 4),
        'total_days': len(demands)
    }


def calculate_safety_stock(std_daily_demand, lead_time_days, service_level=0.95):
    """
    Calculate safety stock using the statistical method.
    
    Formula: Safety Stock = Z × σ_demand × √Lead Time
    
    Args:
        std_daily_demand: Standard deviation of daily demand
        lead_time_days: Supplier lead time in days
        service_level: Target service level (0-1)
        
    Returns:
        Safety stock quantity (integer, rounded up)
    """
    z_score = get_z_score(service_level)
    safety_stock = z_score * std_daily_demand * math.sqrt(lead_time_days)
    return math.ceil(safety_stock)


def calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock):
    """
    Calculate the dynamic reorder point.
    
    Formula: ROP = (Average Daily Demand × Lead Time) + Safety Stock
    
    Args:
        avg_daily_demand: Average daily demand
        lead_time_days: Supplier lead time in days
        safety_stock: Calculated safety stock
        
    Returns:
        Reorder point quantity (integer, rounded up)
    """
    rop = (avg_daily_demand * lead_time_days) + safety_stock
    return math.ceil(rop)


def calculate_eoq(annual_demand, ordering_cost=50, holding_cost_rate=0.25, unit_price=1.0):
    """
    Calculate Economic Order Quantity (EOQ).
    
    Formula: EOQ = √(2 × D × S / H)
    Where:
        D = Annual demand
        S = Ordering cost per order
        H = Holding cost per unit per year = holding_cost_rate × unit_price
        
    Args:
        annual_demand: Total annual demand
        ordering_cost: Cost per order placement
        holding_cost_rate: Holding cost as fraction of unit price
        unit_price: Price per unit
        
    Returns:
        Optimal order quantity (integer, rounded up)
    """
    if annual_demand <= 0 or unit_price <= 0:
        return 0
    
    holding_cost = holding_cost_rate * unit_price
    if holding_cost <= 0:
        return 0
    
    eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
    return math.ceil(eoq)


def get_reorder_recommendation(product_data, daily_demands, forecasted_demand=None):
    """
    Generate a complete reorder recommendation for a product.
    
    Args:
        product_data: dict with quantity, lead_time_days, service_level, unit_price, reorder_threshold
        daily_demands: Array of historical daily demand values
        forecasted_demand: Optional array of forecasted daily demand values
        
    Returns:
        dict with full recommendation including static vs dynamic comparison
    """
    demand_stats = calculate_demand_statistics(daily_demands)
    
    # Use forecasted demand if available, otherwise use historical average
    if forecasted_demand is not None and len(forecasted_demand) > 0:
        forecast_avg = float(np.mean(forecasted_demand))
        effective_demand = forecast_avg
    else:
        effective_demand = demand_stats['avg_daily_demand']
    
    lead_time = product_data.get('lead_time_days', 7)
    service_level = product_data.get('service_level', 0.95)
    unit_price = float(product_data.get('unit_price', 1.0))
    current_qty = product_data.get('quantity', 0)
    static_threshold = product_data.get('reorder_threshold', 0)
    
    # Calculate dynamic reorder metrics
    safety_stock = calculate_safety_stock(
        demand_stats['std_daily_demand'], lead_time, service_level
    )
    
    dynamic_reorder_point = calculate_reorder_point(
        effective_demand, lead_time, safety_stock
    )
    
    annual_demand = effective_demand * 365
    eoq = calculate_eoq(annual_demand, unit_price=unit_price)
    
    # Days until stockout estimate
    if effective_demand > 0:
        days_until_stockout = current_qty / effective_demand
    else:
        days_until_stockout = float('inf')
    
    # Determine urgency
    if current_qty <= dynamic_reorder_point:
        urgency = 'CRITICAL' if current_qty <= safety_stock else 'HIGH'
    elif current_qty <= dynamic_reorder_point * 1.5:
        urgency = 'MEDIUM'
    else:
        urgency = 'LOW'
    
    return {
        'demand_statistics': demand_stats,
        'safety_stock': safety_stock,
        'dynamic_reorder_point': dynamic_reorder_point,
        'static_reorder_threshold': static_threshold,
        'eoq': eoq,
        'current_quantity': current_qty,
        'days_until_stockout': round(days_until_stockout, 1),
        'urgency': urgency,
        'service_level': service_level,
        'lead_time_days': lead_time,
        'needs_reorder': current_qty <= dynamic_reorder_point,
        'recommended_order_qty': eoq if current_qty <= dynamic_reorder_point else 0,
        'comparison': {
            'static_would_trigger': current_qty <= static_threshold,
            'dynamic_triggers': current_qty <= dynamic_reorder_point,
            'difference': dynamic_reorder_point - static_threshold,
            'improvement': 'Dynamic threshold is more accurate based on actual demand patterns'
        }
    }
