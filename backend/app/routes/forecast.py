"""
Forecast API Routes for ShelfSense.

Provides endpoints for demand forecasting:
- GET /forecast/<product_id> — Get demand forecast for a product
- GET /forecast/<product_id>/compare — Compare model performance metrics
- POST /forecast/<product_id>/train — Trigger model training
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Product, StockMovement, ForecastResult
from app.extensions import db
from app.utils.auth import requires_permission, Permission
from app.utils.errors import api_error

forecast_bp = Blueprint('forecast', __name__)


@forecast_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_forecast(product_id):
    """
    Get demand forecast for a specific product.
    Uses the most recent trained forecast, or generates a quick one if none exists.
    
    Query params:
        horizon: Number of days to forecast (default: 30)
        model: Model to use — arima, prophet, xgboost, ensemble (default: ensemble)
    """
    product = Product.query.get(product_id)
    if not product:
        return api_error("Product not found", 404)
    
    horizon = request.args.get('horizon', 30, type=int)
    model_name = request.args.get('model', 'ensemble')
    
    # Check for existing forecast
    existing = ForecastResult.query.filter_by(
        product_id=product_id
    ).order_by(ForecastResult.created_at.desc()).first()
    
    if existing:
        return jsonify({
            'product_id': product_id,
            'product_name': product.name,
            'model_name': existing.model_name,
            'horizon_days': existing.horizon_days,
            'predictions': json.loads(existing.predictions),
            'confidence_lower': json.loads(existing.confidence_lower) if existing.confidence_lower else [],
            'confidence_upper': json.loads(existing.confidence_upper) if existing.confidence_upper else [],
            'metrics': {
                'rmse': existing.rmse,
                'mae': existing.mae,
                'mape': existing.mape,
                'r2_score': existing.r2_score
            },
            'created_at': existing.created_at.isoformat() if existing.created_at else None
        })
    
    # No existing forecast — generate one on the fly
    return _train_and_forecast(product, horizon, model_name)


@forecast_bp.route('/<int:product_id>/compare', methods=['GET'])
@jwt_required()
@requires_permission(Permission.INVENTORY_EDIT)
def compare_models(product_id):
    """
    Compare performance metrics across all trained models for a product.
    Returns RMSE, MAE, MAPE, R² for each model.
    """
    product = Product.query.get(product_id)
    if not product:
        return api_error("Product not found", 404)
    
    # Get all forecast results for this product
    forecasts = ForecastResult.query.filter_by(
        product_id=product_id
    ).order_by(ForecastResult.created_at.desc()).all()
    
    if not forecasts:
        return jsonify({
            'product_id': product_id,
            'product_name': product.name,
            'models': [],
            'message': 'No trained models found. Train models first using POST /forecast/<id>/train'
        })
    
    # Get latest result per model
    seen_models = set()
    model_results = []
    for f in forecasts:
        if f.model_name not in seen_models:
            seen_models.add(f.model_name)
            model_results.append({
                'model_name': f.model_name,
                'rmse': f.rmse,
                'mae': f.mae,
                'mape': f.mape,
                'r2_score': f.r2_score,
                'horizon_days': f.horizon_days,
                'trained_at': f.created_at.isoformat() if f.created_at else None
            })
    
    # Sort by RMSE (best first)
    model_results.sort(key=lambda x: x['rmse'] if x['rmse'] is not None else float('inf'))
    
    return jsonify({
        'product_id': product_id,
        'product_name': product.name,
        'models': model_results,
        'best_model': model_results[0]['model_name'] if model_results else None
    })


@forecast_bp.route('/<int:product_id>/train', methods=['POST'])
@jwt_required()
@requires_permission(Permission.INVENTORY_EDIT)
def train_models(product_id):
    """
    Train all forecasting models for a product and store results.
    This may take some time depending on data volume.
    
    Body params (optional):
        horizon: Number of days to forecast (default: 30)
    """
    product = Product.query.get(product_id)
    if not product:
        return api_error("Product not found", 404)
    
    data = request.get_json(silent=True) or {}
    horizon = data.get('horizon', 30)
    
    result = _train_and_forecast(product, horizon, 'all')
    return result


def _train_and_forecast(product, horizon, model_name):
    """
    Internal function to train models and generate forecasts.
    """
    from app.ml.data_preprocessor import get_daily_demand, engineer_features, prepare_train_test_split
    from app.ml.model_evaluator import evaluate_model
    
    # Fetch stock movement history
    movements = StockMovement.query.filter_by(product_id=product.id).all()
    
    if len(movements) < 10:
        return jsonify({
            'product_id': product.id,
            'product_name': product.name,
            'message': 'Insufficient data for forecasting. Need at least 10 stock movements.',
            'movements_count': len(movements)
        }), 200
    
    # Prepare data
    movements_data = [{
        'created_at': m.created_at,
        'change_qty': m.change_qty,
        'reason': m.reason
    } for m in movements]
    
    daily_demand = get_daily_demand(movements_data)
    featured_df = engineer_features(daily_demand)
    train_df, test_df = prepare_train_test_split(featured_df)
    
    results = {}
    
    # Train individual models
    models_to_train = []
    if model_name in ('arima', 'all'):
        models_to_train.append('arima')
    if model_name in ('prophet', 'all'):
        models_to_train.append('prophet')
    if model_name in ('xgboost', 'all'):
        models_to_train.append('xgboost')
    if model_name in ('lstm', 'all'):
        models_to_train.append('lstm')
    if model_name in ('ensemble', 'all'):
        models_to_train.append('ensemble')
    
    if not models_to_train:
        models_to_train = ['ensemble']
    
    for m_name in models_to_train:
        try:
            if m_name == 'arima':
                from app.ml.forecaster import ARIMAForecaster
                model = ARIMAForecaster()
                model.train(train_df['demand'])
                pred = model.predict(horizon)
                
            elif m_name == 'prophet':
                from app.ml.forecaster import ProphetForecaster
                model = ProphetForecaster()
                model.train(train_df[['date', 'demand']])
                pred = model.predict(horizon)
                
            elif m_name == 'xgboost':
                from app.ml.forecaster import XGBoostForecaster
                model = XGBoostForecaster()
                model.train(train_df)
                pred = model.predict(horizon)
                
            elif m_name == 'lstm':
                from app.ml.forecaster import LSTMForecaster
                model = LSTMForecaster(epochs=30)
                model.train(train_df['demand'])
                pred = model.predict(horizon)
                
            elif m_name == 'ensemble':
                from app.ml.forecaster import HybridEnsembleForecaster
                model = HybridEnsembleForecaster()
                model.train_all(daily_demand, featured_df)
                pred = model.predict(horizon)
            else:
                continue
            
            # Evaluate against test data if possible
            test_horizon = len(test_df)
            if test_horizon > 0 and m_name != 'ensemble':
                test_pred = model.predict(test_horizon)
                metrics = evaluate_model(
                    test_df['demand'].values,
                    test_pred['predictions'][:test_horizon]
                )
            else:
                metrics = {'rmse': None, 'mae': None, 'mape': None, 'r2_score': None}
            
            # Store forecast result
            display_name = m_name.upper() if m_name != 'ensemble' else 'Hybrid Ensemble'
            forecast_result = ForecastResult(
                product_id=product.id,
                model_name=display_name,
                horizon_days=horizon,
                predictions=json.dumps(pred['predictions']),
                confidence_lower=json.dumps(pred.get('confidence_lower', [])),
                confidence_upper=json.dumps(pred.get('confidence_upper', [])),
                rmse=metrics.get('rmse'),
                mae=metrics.get('mae'),
                mape=metrics.get('mape'),
                r2_score=metrics.get('r2_score')
            )
            db.session.add(forecast_result)
            
            results[display_name] = {
                'predictions': pred['predictions'],
                'confidence_lower': pred.get('confidence_lower', []),
                'confidence_upper': pred.get('confidence_upper', []),
                'metrics': metrics
            }
            
        except Exception as e:
            results[m_name.upper()] = {'error': str(e)}
    
    db.session.commit()
    
    return jsonify({
        'product_id': product.id,
        'product_name': product.name,
        'horizon_days': horizon,
        'models': results,
        'data_points_used': len(daily_demand)
    })
