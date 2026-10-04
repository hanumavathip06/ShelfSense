"""
Anomaly Detection for ShelfSense ML Pipeline.

Detects unusual stock movement patterns that may indicate:
- Potential theft or shrinkage
- Data entry errors
- Sudden demand spikes or drops
- Supplier delivery anomalies

Implements two detection methods:
1. Isolation Forest: Unsupervised ML algorithm for outlier detection
2. Z-Score: Statistical method based on standard deviations from mean
"""

import numpy as np
from datetime import datetime, timezone


def detect_anomalies_zscore(movements_data, threshold=2.5):
    """
    Detect anomalous stock movements using Z-Score method.
    
    A movement is flagged as anomalous if its Z-score exceeds the threshold.
    Z-Score = (value - mean) / std_deviation
    
    Args:
        movements_data: List of dicts with keys: id, product_id, change_qty, reason, created_at
        threshold: Z-score threshold for flagging anomalies (default: 2.5)
        
    Returns:
        List of dicts with anomaly details
    """
    if not movements_data or len(movements_data) < 5:
        return []
    
    quantities = np.array([abs(m['change_qty']) for m in movements_data], dtype=np.float64)
    
    mean_qty = np.mean(quantities)
    std_qty = np.std(quantities)
    
    if std_qty == 0:
        return []
    
    anomalies = []
    
    for i, movement in enumerate(movements_data):
        qty = abs(movement['change_qty'])
        z_score = (qty - mean_qty) / std_qty
        
        if abs(z_score) > threshold:
            anomaly_type = _classify_anomaly(movement, z_score)
            
            anomalies.append({
                'movement_id': movement.get('id'),
                'product_id': movement.get('product_id'),
                'product_name': movement.get('product_name', ''),
                'change_qty': movement['change_qty'],
                'reason': movement.get('reason', ''),
                'z_score': round(float(z_score), 4),
                'anomaly_score': round(float(abs(z_score) / threshold), 4),
                'anomaly_type': anomaly_type,
                'severity': _get_severity(abs(z_score), threshold),
                'created_at': movement.get('created_at', ''),
                'method': 'Z-Score'
            })
    
    return sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)


def detect_anomalies_isolation_forest(movements_data, contamination=0.1):
    """
    Detect anomalous stock movements using Isolation Forest algorithm.
    
    Isolation Forest works by randomly selecting features and split values,
    then counting the number of splits needed to isolate a data point.
    Anomalies require fewer splits (shorter path length).
    
    Args:
        movements_data: List of dicts with movement data
        contamination: Expected proportion of anomalies (default: 10%)
        
    Returns:
        List of dicts with anomaly details
    """
    from sklearn.ensemble import IsolationForest
    
    if not movements_data or len(movements_data) < 10:
        return []
    
    # Feature engineering for each movement
    features = []
    for m in movements_data:
        created_at = m.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                created_at = datetime.now(timezone.utc)
        
        features.append([
            abs(m['change_qty']),
            created_at.hour if hasattr(created_at, 'hour') else 12,
            created_at.weekday() if hasattr(created_at, 'weekday') else 0,
        ])
    
    X = np.array(features, dtype=np.float64)
    
    # Fit Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )
    
    predictions = iso_forest.fit_predict(X)
    scores = iso_forest.decision_function(X)
    
    anomalies = []
    
    for i, (pred, score) in enumerate(zip(predictions, scores)):
        if pred == -1:  # -1 indicates anomaly
            movement = movements_data[i]
            anomaly_type = _classify_anomaly(movement, -score)
            
            anomalies.append({
                'movement_id': movement.get('id'),
                'product_id': movement.get('product_id'),
                'product_name': movement.get('product_name', ''),
                'change_qty': movement['change_qty'],
                'reason': movement.get('reason', ''),
                'anomaly_score': round(float(-score), 4),
                'anomaly_type': anomaly_type,
                'severity': _get_severity_from_score(-score),
                'created_at': movement.get('created_at', ''),
                'method': 'Isolation Forest'
            })
    
    return sorted(anomalies, key=lambda x: x['anomaly_score'], reverse=True)


def detect_anomalies_combined(movements_data, z_threshold=2.5, contamination=0.1):
    """
    Run both anomaly detection methods and combine results.
    Items flagged by both methods are given higher confidence.
    
    Args:
        movements_data: List of movement dicts
        z_threshold: Z-score threshold
        contamination: Isolation Forest contamination rate
        
    Returns:
        dict with combined anomalies, z_score_anomalies, isolation_forest_anomalies
    """
    z_anomalies = detect_anomalies_zscore(movements_data, z_threshold)
    
    try:
        if_anomalies = detect_anomalies_isolation_forest(movements_data, contamination)
    except Exception:
        if_anomalies = []
    
    # Find movements flagged by both methods
    z_ids = {a['movement_id'] for a in z_anomalies}
    if_ids = {a['movement_id'] for a in if_anomalies}
    both_ids = z_ids & if_ids
    
    combined = []
    seen_ids = set()
    
    # Add high-confidence anomalies (flagged by both)
    for a in z_anomalies + if_anomalies:
        mid = a['movement_id']
        if mid in both_ids and mid not in seen_ids:
            a['confidence'] = 'HIGH'
            a['detection_methods'] = ['Z-Score', 'Isolation Forest']
            combined.append(a)
            seen_ids.add(mid)
        elif mid not in seen_ids:
            a['confidence'] = 'MEDIUM'
            a['detection_methods'] = [a['method']]
            combined.append(a)
            seen_ids.add(mid)
    
    return {
        'anomalies': sorted(combined, key=lambda x: x.get('anomaly_score', 0), reverse=True),
        'total_movements_analyzed': len(movements_data),
        'total_anomalies_detected': len(combined),
        'high_confidence_count': len(both_ids),
        'z_score_count': len(z_anomalies),
        'isolation_forest_count': len(if_anomalies)
    }


def _classify_anomaly(movement, score):
    """Classify the type of anomaly based on movement characteristics."""
    change_qty = movement.get('change_qty', 0)
    reason = movement.get('reason', '')
    
    if change_qty < 0 and abs(change_qty) > 100:
        return 'Unusually large outflow — possible theft or bulk error'
    elif change_qty > 0 and change_qty > 100:
        return 'Unusually large inflow — verify supplier delivery'
    elif reason == 'manual_adjustment':
        return 'Suspicious manual adjustment — review required'
    elif reason == 'sale' and abs(change_qty) > 50:
        return 'Abnormal sales volume — demand spike detected'
    else:
        return 'Statistical outlier — further investigation recommended'


def _get_severity(z_score, threshold):
    """Determine severity level based on Z-score magnitude."""
    ratio = abs(z_score) / threshold
    if ratio >= 2.0:
        return 'CRITICAL'
    elif ratio >= 1.5:
        return 'HIGH'
    elif ratio >= 1.0:
        return 'MEDIUM'
    else:
        return 'LOW'


def _get_severity_from_score(anomaly_score):
    """Determine severity from Isolation Forest anomaly score."""
    if anomaly_score > 0.3:
        return 'CRITICAL'
    elif anomaly_score > 0.2:
        return 'HIGH'
    elif anomaly_score > 0.1:
        return 'MEDIUM'
    else:
        return 'LOW'
