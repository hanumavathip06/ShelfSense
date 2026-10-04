"""
ABC-XYZ Inventory Classification for ShelfSense ML Pipeline.

Classifies inventory items into a 3×3 matrix based on:

ABC Analysis (Revenue/Value Contribution):
- A: Top 80% of total inventory value (high-value items)
- B: Next 15% of total inventory value (medium-value items)
- C: Bottom 5% of total inventory value (low-value items)

XYZ Analysis (Demand Variability):
- X: Low demand variability (CV < 0.5) — stable, predictable demand
- Y: Moderate demand variability (0.5 ≤ CV < 1.0) — some fluctuation
- Z: High demand variability (CV ≥ 1.0) — erratic, unpredictable demand

Combined Matrix guides inventory strategy:
- AX: High value, stable → Continuous review, accurate forecasting
- AZ: High value, erratic → Safety stock focus, frequent monitoring
- CX: Low value, stable → Simple reorder point, minimal monitoring
- CZ: Low value, erratic → Consider eliminating from inventory
"""

import numpy as np


def classify_abc(products_data):
    """
    Perform ABC classification based on inventory value.
    
    Args:
        products_data: List of dicts with keys: id, name, quantity, unit_price
        
    Returns:
        Dict mapping product_id to ABC class ('A', 'B', or 'C')
    """
    if not products_data:
        return {}
    
    # Calculate total value for each product
    for p in products_data:
        p['total_value'] = float(p.get('quantity', 0)) * float(p.get('unit_price', 0))
    
    # Sort by total value (descending)
    sorted_products = sorted(products_data, key=lambda x: x['total_value'], reverse=True)
    
    total_inventory_value = sum(p['total_value'] for p in sorted_products)
    
    if total_inventory_value == 0:
        return {p['id']: 'C' for p in sorted_products}
    
    classification = {}
    cumulative_value = 0
    
    for product in sorted_products:
        cumulative_value += product['total_value']
        cumulative_percentage = (cumulative_value / total_inventory_value) * 100
        
        if cumulative_percentage <= 80:
            classification[product['id']] = 'A'
        elif cumulative_percentage <= 95:
            classification[product['id']] = 'B'
        else:
            classification[product['id']] = 'C'
    
    return classification


def classify_xyz(products_demand_data):
    """
    Perform XYZ classification based on demand variability.
    
    Uses Coefficient of Variation (CV = σ / μ) as the variability measure.
    
    Args:
        products_demand_data: Dict mapping product_id to list of daily demand values
        
    Returns:
        Dict mapping product_id to XYZ class ('X', 'Y', or 'Z') and CV value
    """
    if not products_demand_data:
        return {}
    
    classification = {}
    
    for product_id, demands in products_demand_data.items():
        demands = np.array(demands, dtype=np.float64)
        demands = demands[demands >= 0]  # Remove negatives
        
        if len(demands) == 0 or np.mean(demands) == 0:
            classification[product_id] = {'class': 'Z', 'cv': float('inf')}
            continue
        
        mean_demand = np.mean(demands)
        std_demand = np.std(demands)
        cv = std_demand / mean_demand  # Coefficient of Variation
        
        if cv < 0.5:
            xyz_class = 'X'
        elif cv < 1.0:
            xyz_class = 'Y'
        else:
            xyz_class = 'Z'
        
        classification[product_id] = {
            'class': xyz_class,
            'cv': round(float(cv), 4)
        }
    
    return classification


def get_combined_classification(products_data, products_demand_data):
    """
    Perform combined ABC-XYZ classification.
    
    Args:
        products_data: List of dicts with product details
        products_demand_data: Dict mapping product_id to demand history
        
    Returns:
        List of dicts with complete classification for each product
    """
    abc_classes = classify_abc(products_data)
    xyz_results = classify_xyz(products_demand_data)
    
    results = []
    
    for product in products_data:
        pid = product['id']
        abc = abc_classes.get(pid, 'C')
        xyz_data = xyz_results.get(pid, {'class': 'Z', 'cv': 0})
        xyz = xyz_data['class']
        cv = xyz_data['cv']
        
        combined_class = f"{abc}{xyz}"
        
        # Generate strategy recommendation
        strategy = get_strategy_recommendation(combined_class)
        
        results.append({
            'product_id': pid,
            'product_name': product.get('name', ''),
            'sku': product.get('sku', ''),
            'total_value': float(product.get('quantity', 0)) * float(product.get('unit_price', 0)),
            'abc_class': abc,
            'xyz_class': xyz,
            'combined_class': combined_class,
            'coefficient_of_variation': cv if cv != float('inf') else 999,
            'strategy': strategy
        })
    
    return results


def get_strategy_recommendation(combined_class):
    """
    Returns inventory management strategy based on ABC-XYZ class.
    
    Args:
        combined_class: Two-character string like 'AX', 'BY', 'CZ'
        
    Returns:
        dict with monitoring_level, forecasting_approach, reorder_strategy
    """
    strategies = {
        'AX': {
            'monitoring_level': 'Continuous',
            'forecasting_approach': 'ML-based (LSTM/Hybrid) with daily updates',
            'reorder_strategy': 'Just-In-Time (JIT) with dynamic reorder points',
            'priority': 'HIGHEST'
        },
        'AY': {
            'monitoring_level': 'Continuous',
            'forecasting_approach': 'ML-based with weekly recalibration',
            'reorder_strategy': 'Dynamic reorder point with safety stock buffer',
            'priority': 'HIGH'
        },
        'AZ': {
            'monitoring_level': 'Continuous',
            'forecasting_approach': 'Ensemble model with wide confidence intervals',
            'reorder_strategy': 'High safety stock, frequent review',
            'priority': 'HIGH'
        },
        'BX': {
            'monitoring_level': 'Periodic (Weekly)',
            'forecasting_approach': 'ARIMA/XGBoost with weekly updates',
            'reorder_strategy': 'Fixed reorder point with moderate safety stock',
            'priority': 'MEDIUM'
        },
        'BY': {
            'monitoring_level': 'Periodic (Weekly)',
            'forecasting_approach': 'Moving average with seasonal adjustment',
            'reorder_strategy': 'Periodic review system',
            'priority': 'MEDIUM'
        },
        'BZ': {
            'monitoring_level': 'Periodic (Bi-weekly)',
            'forecasting_approach': 'Simple moving average',
            'reorder_strategy': 'Safety stock focused, periodic review',
            'priority': 'MEDIUM-LOW'
        },
        'CX': {
            'monitoring_level': 'Periodic (Monthly)',
            'forecasting_approach': 'Simple average / min-max method',
            'reorder_strategy': 'Simple reorder point, minimal monitoring',
            'priority': 'LOW'
        },
        'CY': {
            'monitoring_level': 'Periodic (Monthly)',
            'forecasting_approach': 'Simple average',
            'reorder_strategy': 'Bulk ordering to reduce costs',
            'priority': 'LOW'
        },
        'CZ': {
            'monitoring_level': 'On-demand',
            'forecasting_approach': 'Not recommended — order on demand',
            'reorder_strategy': 'Consider eliminating; order only when needed',
            'priority': 'LOWEST'
        }
    }
    
    return strategies.get(combined_class, strategies['CZ'])


def get_classification_summary(classification_results):
    """
    Generate a summary of the classification distribution.
    
    Args:
        classification_results: Output from get_combined_classification()
        
    Returns:
        dict with distribution counts and value percentages
    """
    if not classification_results:
        return {'abc_distribution': {}, 'xyz_distribution': {}, 'matrix': {}}
    
    abc_dist = {'A': 0, 'B': 0, 'C': 0}
    xyz_dist = {'X': 0, 'Y': 0, 'Z': 0}
    matrix = {}
    abc_values = {'A': 0, 'B': 0, 'C': 0}
    total_value = 0
    
    for item in classification_results:
        abc = item['abc_class']
        xyz = item['xyz_class']
        combined = item['combined_class']
        value = item['total_value']
        
        abc_dist[abc] = abc_dist.get(abc, 0) + 1
        xyz_dist[xyz] = xyz_dist.get(xyz, 0) + 1
        matrix[combined] = matrix.get(combined, 0) + 1
        abc_values[abc] = abc_values.get(abc, 0) + value
        total_value += value
    
    # Calculate value percentages
    abc_value_pct = {}
    for cls, val in abc_values.items():
        abc_value_pct[cls] = round((val / total_value * 100), 2) if total_value > 0 else 0
    
    return {
        'abc_distribution': abc_dist,
        'xyz_distribution': xyz_dist,
        'matrix': matrix,
        'abc_value_percentages': abc_value_pct,
        'total_products': len(classification_results),
        'total_inventory_value': round(total_value, 2)
    }
