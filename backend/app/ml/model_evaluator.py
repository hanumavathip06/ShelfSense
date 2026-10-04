"""
Model Evaluator for ShelfSense ML Pipeline.

Provides evaluation metrics for comparing forecasting model performance:
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- MAPE (Mean Absolute Percentage Error)
- R² Score (Coefficient of Determination)

These metrics are critical for the IEEE paper's results section.
"""

import numpy as np


def evaluate_model(actual, predicted):
    """
    Calculate comprehensive evaluation metrics for a forecasting model.
    
    Args:
        actual: Array-like of actual demand values
        predicted: Array-like of predicted demand values
        
    Returns:
        dict with rmse, mae, mape, r2_score
    """
    actual = np.array(actual, dtype=np.float64)
    predicted = np.array(predicted, dtype=np.float64)
    
    # Ensure same length
    min_len = min(len(actual), len(predicted))
    actual = actual[:min_len]
    predicted = predicted[:min_len]
    
    if len(actual) == 0:
        return {'rmse': 0, 'mae': 0, 'mape': 0, 'r2_score': 0}
    
    # RMSE - Root Mean Squared Error
    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    
    # MAE - Mean Absolute Error
    mae = float(np.mean(np.abs(actual - predicted)))
    
    # MAPE - Mean Absolute Percentage Error
    # Avoid division by zero: only compute on non-zero actuals
    non_zero_mask = actual != 0
    if np.any(non_zero_mask):
        mape = float(np.mean(np.abs((actual[non_zero_mask] - predicted[non_zero_mask]) / actual[non_zero_mask])) * 100)
    else:
        mape = 0.0
    
    # R² Score - Coefficient of Determination
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2_score = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
    
    return {
        'rmse': round(rmse, 4),
        'mae': round(mae, 4),
        'mape': round(mape, 4),
        'r2_score': round(r2_score, 4)
    }


def compare_models(actual, model_predictions):
    """
    Compare multiple models using evaluation metrics.
    
    Args:
        actual: Array-like of actual demand values
        model_predictions: Dict of {model_name: predicted_values}
        
    Returns:
        Dict of {model_name: metrics_dict}, sorted by RMSE (best first)
    """
    results = {}
    
    for model_name, predicted in model_predictions.items():
        metrics = evaluate_model(actual, predicted)
        results[model_name] = metrics
    
    # Sort by RMSE (lower is better)
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['rmse']))
    
    return sorted_results


def get_best_model(comparison_results):
    """
    Identify the best performing model from comparison results.
    
    Args:
        comparison_results: Output from compare_models()
        
    Returns:
        Tuple of (best_model_name, metrics)
    """
    if not comparison_results:
        return None, {}
    
    best_name = next(iter(comparison_results))
    return best_name, comparison_results[best_name]
