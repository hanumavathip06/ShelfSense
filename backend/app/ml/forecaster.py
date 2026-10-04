"""
Demand Forecasting Models for ShelfSense ML Pipeline.

Implements multiple forecasting algorithms for comparative analysis:
- ARIMA/SARIMA: Statistical time-series baseline
- Prophet: Additive model with trend + seasonality (Facebook)
- LSTM: Deep learning with temporal dependencies
- XGBoost: Gradient boosting with engineered features
- Hybrid Ensemble: Weighted combination of best models

Each model follows a consistent interface with train() and predict() methods.
"""

import warnings
import numpy as np
import pandas as pd
from datetime import timedelta

warnings.filterwarnings('ignore')


class ARIMAForecaster:
    """
    ARIMA (AutoRegressive Integrated Moving Average) forecaster.
    Statistical baseline model for time-series prediction.
    """
    
    def __init__(self, order=(5, 1, 0)):
        self.order = order
        self.model_fit = None
        self.name = "ARIMA"
    
    def train(self, demand_series):
        """
        Train ARIMA model on historical demand data.
        
        Args:
            demand_series: pd.Series of daily demand values
        """
        from statsmodels.tsa.arima.model import ARIMA
        
        try:
            model = ARIMA(demand_series.values, order=self.order)
            self.model_fit = model.fit()
        except Exception:
            # Fallback to simpler model if convergence fails
            model = ARIMA(demand_series.values, order=(1, 1, 0))
            self.model_fit = model.fit()
    
    def predict(self, horizon_days=30):
        """
        Generate demand forecast for the specified horizon.
        
        Args:
            horizon_days: Number of days to forecast ahead
            
        Returns:
            dict with keys: predictions, confidence_lower, confidence_upper
        """
        if self.model_fit is None:
            raise ValueError("Model not trained. Call train() first.")
        
        forecast_result = self.model_fit.get_forecast(steps=horizon_days)
        predictions = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)
        
        return {
            'predictions': np.maximum(predictions, 0).tolist(),
            'confidence_lower': np.maximum(conf_int[:, 0], 0).tolist(),
            'confidence_upper': np.maximum(conf_int[:, 1], 0).tolist()
        }


class ProphetForecaster:
    """
    Facebook Prophet forecaster.
    Additive model handling trend, seasonality, and holiday effects.
    """
    
    def __init__(self):
        self.model = None
        self.name = "Prophet"
    
    def train(self, demand_df):
        """
        Train Prophet model.
        
        Args:
            demand_df: DataFrame with columns 'date' and 'demand'
        """
        from prophet import Prophet
        
        # Prophet requires 'ds' and 'y' columns
        prophet_df = demand_df[['date', 'demand']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        self.model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True if len(prophet_df) > 365 else False,
            changepoint_prior_scale=0.05,
            seasonality_mode='multiplicative'
        )
        self.model.fit(prophet_df)
    
    def predict(self, horizon_days=30):
        """
        Generate demand forecast using Prophet.
        
        Returns:
            dict with predictions, confidence_lower, confidence_upper
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        future = self.model.make_future_dataframe(periods=horizon_days)
        forecast = self.model.predict(future)
        
        # Get only the forecast period
        forecast_period = forecast.tail(horizon_days)
        
        return {
            'predictions': np.maximum(forecast_period['yhat'].values, 0).tolist(),
            'confidence_lower': np.maximum(forecast_period['yhat_lower'].values, 0).tolist(),
            'confidence_upper': np.maximum(forecast_period['yhat_upper'].values, 0).tolist()
        }


class LSTMForecaster:
    """
    LSTM (Long Short-Term Memory) neural network forecaster.
    Deep learning model capturing complex temporal dependencies.
    """
    
    def __init__(self, sequence_length=30, epochs=50, batch_size=16):
        self.sequence_length = sequence_length
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.min_val = 0
        self.max_val = 1
        self.name = "LSTM"
    
    def train(self, demand_series):
        """
        Train LSTM model on demand time series.
        
        Args:
            demand_series: pd.Series or array of daily demand values
        """
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from app.ml.data_preprocessor import normalize_data, prepare_lstm_sequences
        
        data = np.array(demand_series, dtype=np.float32)
        
        if len(data) < self.sequence_length + 10:
            # Not enough data for LSTM, use a simpler approach
            self.model = None
            self.fallback_value = float(np.mean(data)) if len(data) > 0 else 0
            return
        
        # Normalize data
        normalized, self.min_val, self.max_val = normalize_data(data)
        
        # Prepare sequences
        X, y = prepare_lstm_sequences(normalized, self.sequence_length)
        
        if len(X) == 0:
            self.model = None
            self.fallback_value = float(np.mean(data))
            return
        
        # Build LSTM model
        self.model = Sequential([
            LSTM(64, input_shape=(self.sequence_length, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mse')
        
        # Train silently
        self.model.fit(
            X, y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=0,
            validation_split=0.1
        )
        
        # Store last sequence for prediction
        self.last_sequence = normalized[-self.sequence_length:]
    
    def predict(self, horizon_days=30):
        """
        Generate demand forecast using LSTM.
        
        Returns:
            dict with predictions, confidence_lower, confidence_upper
        """
        from app.ml.data_preprocessor import denormalize_data
        
        if self.model is None:
            # Fallback: return mean-based prediction
            predictions = [self.fallback_value] * horizon_days
            return {
                'predictions': predictions,
                'confidence_lower': [max(0, p * 0.7) for p in predictions],
                'confidence_upper': [p * 1.3 for p in predictions]
            }
        
        predictions = []
        current_seq = self.last_sequence.copy().reshape(1, self.sequence_length, 1)
        
        for _ in range(horizon_days):
            pred = self.model.predict(current_seq, verbose=0)[0, 0]
            predictions.append(pred)
            # Shift sequence and append prediction
            current_seq = np.roll(current_seq, -1, axis=1)
            current_seq[0, -1, 0] = pred
        
        # Denormalize
        predictions = denormalize_data(np.array(predictions), self.min_val, self.max_val)
        
        # Estimate confidence intervals (±20% for LSTM)
        predictions_list = np.maximum(predictions, 0).tolist()
        
        return {
            'predictions': predictions_list,
            'confidence_lower': [max(0, p * 0.8) for p in predictions_list],
            'confidence_upper': [p * 1.2 for p in predictions_list]
        }


class XGBoostForecaster:
    """
    XGBoost gradient boosting forecaster.
    Uses engineered time-series features for regression.
    """
    
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.last_row = None
        self.name = "XGBoost"
    
    def train(self, featured_df):
        """
        Train XGBoost model on feature-engineered data.
        
        Args:
            featured_df: DataFrame from engineer_features() with 'demand' as target
        """
        from xgboost import XGBRegressor
        
        df = featured_df.copy()
        
        self.feature_columns = [
            'day_of_week', 'month', 'day_of_month', 'is_weekend', 'week_of_year',
            'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_30',
            'rolling_std_7', 'rolling_std_14',
            'lag_1', 'lag_7', 'lag_14', 'lag_30',
            'ema_7', 'ema_14'
        ]
        
        # Filter available columns
        available_cols = [c for c in self.feature_columns if c in df.columns]
        self.feature_columns = available_cols
        
        X = df[self.feature_columns].values
        y = df['demand'].values
        
        self.model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        self.model.fit(X, y)
        
        # Store last row for iterative prediction
        self.last_row = df.iloc[-1].copy()
        self.training_data = df.copy()
    
    def predict(self, horizon_days=30):
        """
        Generate demand forecast using XGBoost with iterative feature construction.
        
        Returns:
            dict with predictions, confidence_lower, confidence_upper
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = []
        temp_df = self.training_data.copy()
        
        for i in range(horizon_days):
            # Create next day's features
            next_date = temp_df['date'].iloc[-1] + timedelta(days=1)
            next_row = {
                'date': next_date,
                'day_of_week': next_date.dayofweek,
                'month': next_date.month,
                'day_of_month': next_date.day,
                'is_weekend': int(next_date.dayofweek >= 5),
                'week_of_year': next_date.isocalendar()[1],
            }
            
            # Calculate rolling features from recent data
            recent_demands = temp_df['demand'].values
            next_row['rolling_mean_7'] = np.mean(recent_demands[-7:])
            next_row['rolling_mean_14'] = np.mean(recent_demands[-14:])
            next_row['rolling_mean_30'] = np.mean(recent_demands[-30:])
            next_row['rolling_std_7'] = np.std(recent_demands[-7:])
            next_row['rolling_std_14'] = np.std(recent_demands[-14:])
            
            # Lag features
            next_row['lag_1'] = recent_demands[-1] if len(recent_demands) >= 1 else 0
            next_row['lag_7'] = recent_demands[-7] if len(recent_demands) >= 7 else 0
            next_row['lag_14'] = recent_demands[-14] if len(recent_demands) >= 14 else 0
            next_row['lag_30'] = recent_demands[-30] if len(recent_demands) >= 30 else 0
            
            # EMA features (approximate)
            next_row['ema_7'] = temp_df['ema_7'].iloc[-1] if 'ema_7' in temp_df.columns else next_row['rolling_mean_7']
            next_row['ema_14'] = temp_df['ema_14'].iloc[-1] if 'ema_14' in temp_df.columns else next_row['rolling_mean_14']
            
            # Predict
            X_next = np.array([[next_row.get(c, 0) for c in self.feature_columns]])
            pred = max(0, float(self.model.predict(X_next)[0]))
            predictions.append(pred)
            
            # Add prediction to temp data for next iteration
            next_row['demand'] = pred
            temp_df = pd.concat([temp_df, pd.DataFrame([next_row])], ignore_index=True)
        
        return {
            'predictions': predictions,
            'confidence_lower': [max(0, p * 0.75) for p in predictions],
            'confidence_upper': [p * 1.25 for p in predictions]
        }


class HybridEnsembleForecaster:
    """
    Hybrid Ensemble forecaster that combines predictions from multiple models.
    Weights are determined by each model's historical performance (inverse MAPE).
    
    This is the PRIMARY novel contribution for the IEEE paper.
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.name = "Hybrid Ensemble"
    
    def train_all(self, demand_df, featured_df):
        """
        Train all component models and compute ensemble weights.
        
        Args:
            demand_df: DataFrame with 'date' and 'demand' columns
            featured_df: DataFrame with engineered features
        """
        from app.ml.model_evaluator import evaluate_model
        from app.ml.data_preprocessor import prepare_train_test_split
        
        train_df, test_df = prepare_train_test_split(featured_df, test_days=min(30, len(featured_df) // 5))
        
        # Train ARIMA
        try:
            arima = ARIMAForecaster()
            arima.train(train_df['demand'])
            arima_pred = arima.predict(len(test_df))
            arima_metrics = evaluate_model(test_df['demand'].values, arima_pred['predictions'])
            self.models['ARIMA'] = arima
            self.weights['ARIMA'] = 1.0 / max(arima_metrics['mape'], 1)
        except Exception:
            pass
        
        # Train Prophet
        try:
            prophet = ProphetForecaster()
            prophet.train(train_df[['date', 'demand']])
            prophet_pred = prophet.predict(len(test_df))
            prophet_metrics = evaluate_model(test_df['demand'].values, prophet_pred['predictions'])
            self.models['Prophet'] = prophet
            self.weights['Prophet'] = 1.0 / max(prophet_metrics['mape'], 1)
        except Exception:
            pass
        
        # Train XGBoost
        try:
            xgb = XGBoostForecaster()
            xgb.train(train_df)
            xgb_pred = xgb.predict(len(test_df))
            xgb_metrics = evaluate_model(test_df['demand'].values, xgb_pred['predictions'])
            self.models['XGBoost'] = xgb
            self.weights['XGBoost'] = 1.0 / max(xgb_metrics['mape'], 1)
        except Exception:
            pass
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    def predict(self, horizon_days=30):
        """
        Generate weighted ensemble forecast.
        
        Returns:
            dict with predictions, confidence_lower, confidence_upper, model_weights
        """
        if not self.models:
            raise ValueError("No models trained successfully.")
        
        all_predictions = {}
        for name, model in self.models.items():
            try:
                pred = model.predict(horizon_days)
                all_predictions[name] = pred
            except Exception:
                continue
        
        # Weighted average
        ensemble_predictions = np.zeros(horizon_days)
        ensemble_lower = np.zeros(horizon_days)
        ensemble_upper = np.zeros(horizon_days)
        
        active_weight_sum = 0
        for name, pred in all_predictions.items():
            weight = self.weights.get(name, 0)
            pred_arr = np.array(pred['predictions'][:horizon_days])
            lower_arr = np.array(pred['confidence_lower'][:horizon_days])
            upper_arr = np.array(pred['confidence_upper'][:horizon_days])
            
            # Pad if needed
            if len(pred_arr) < horizon_days:
                pred_arr = np.pad(pred_arr, (0, horizon_days - len(pred_arr)), constant_values=pred_arr[-1] if len(pred_arr) > 0 else 0)
                lower_arr = np.pad(lower_arr, (0, horizon_days - len(lower_arr)), constant_values=lower_arr[-1] if len(lower_arr) > 0 else 0)
                upper_arr = np.pad(upper_arr, (0, horizon_days - len(upper_arr)), constant_values=upper_arr[-1] if len(upper_arr) > 0 else 0)
            
            ensemble_predictions += weight * pred_arr
            ensemble_lower += weight * lower_arr
            ensemble_upper += weight * upper_arr
            active_weight_sum += weight
        
        if active_weight_sum > 0:
            ensemble_predictions /= active_weight_sum
            ensemble_lower /= active_weight_sum
            ensemble_upper /= active_weight_sum
        
        return {
            'predictions': np.maximum(ensemble_predictions, 0).tolist(),
            'confidence_lower': np.maximum(ensemble_lower, 0).tolist(),
            'confidence_upper': np.maximum(ensemble_upper, 0).tolist(),
            'model_weights': self.weights,
            'individual_predictions': {
                name: pred['predictions'] for name, pred in all_predictions.items()
            }
        }
