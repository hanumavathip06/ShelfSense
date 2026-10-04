"""
Data Preprocessor for ShelfSense ML Pipeline.

Transforms raw stock movement data from the database into time-series
datasets suitable for demand forecasting models. Handles feature engineering,
missing date imputation, and train/test splitting.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone


def get_daily_demand(movements_data, days_back=180):
    """
    Aggregates stock movements into daily demand time series.
    
    Args:
        movements_data: List of dicts with keys: created_at, change_qty, reason
        days_back: Number of historical days to include
        
    Returns:
        pd.DataFrame with columns: date, demand
    """
    if not movements_data:
        return pd.DataFrame(columns=['date', 'demand'])
    
    df = pd.DataFrame(movements_data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    
    # Filter to sales and outgoing movements (negative change_qty indicates consumption)
    # Sales reduce stock, so we take absolute value of negative changes
    demand_df = df[df['reason'].isin(['sale', 'manual_adjustment'])]
    demand_df = demand_df.copy()
    demand_df['demand'] = demand_df['change_qty'].abs()
    
    # Aggregate daily demand
    daily = demand_df.groupby('date')['demand'].sum().reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    
    # Fill missing dates with 0 demand
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days_back)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    full_df = pd.DataFrame({'date': date_range})
    full_df = full_df.merge(daily, on='date', how='left')
    full_df['demand'] = full_df['demand'].fillna(0).astype(int)
    
    return full_df


def engineer_features(df):
    """
    Creates time-series features for ML models.
    
    Features include:
    - Day of week (0=Monday, 6=Sunday)
    - Month (1-12)
    - Day of month (1-31)
    - Is weekend (binary)
    - Rolling averages (7-day, 14-day, 30-day)
    - Lag features (1, 7, 14, 30 days)
    - Exponential moving average
    
    Args:
        df: DataFrame with columns: date, demand
        
    Returns:
        pd.DataFrame with engineered features
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Calendar features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    
    # Rolling statistics
    df['rolling_mean_7'] = df['demand'].rolling(window=7, min_periods=1).mean()
    df['rolling_mean_14'] = df['demand'].rolling(window=14, min_periods=1).mean()
    df['rolling_mean_30'] = df['demand'].rolling(window=30, min_periods=1).mean()
    df['rolling_std_7'] = df['demand'].rolling(window=7, min_periods=1).std().fillna(0)
    df['rolling_std_14'] = df['demand'].rolling(window=14, min_periods=1).std().fillna(0)
    
    # Lag features
    for lag in [1, 7, 14, 30]:
        df[f'lag_{lag}'] = df['demand'].shift(lag).fillna(0)
    
    # Exponential moving average
    df['ema_7'] = df['demand'].ewm(span=7, adjust=False).mean()
    df['ema_14'] = df['demand'].ewm(span=14, adjust=False).mean()
    
    return df


def prepare_train_test_split(df, test_days=30):
    """
    Splits time-series data into training and test sets.
    Uses chronological split (no random shuffling) to prevent data leakage.
    
    Args:
        df: DataFrame with date and features
        test_days: Number of days to use for testing
        
    Returns:
        Tuple of (train_df, test_df)
    """
    df = df.sort_values('date').reset_index(drop=True)
    
    if len(df) <= test_days:
        # Not enough data, use 80/20 split
        split_idx = max(1, int(len(df) * 0.8))
    else:
        split_idx = len(df) - test_days
    
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    
    return train_df, test_df


def prepare_lstm_sequences(data, sequence_length=30):
    """
    Prepares sequential data for LSTM model input.
    
    Args:
        data: 1D array of demand values
        sequence_length: Number of time steps per sequence
        
    Returns:
        Tuple of (X, y) where X has shape (samples, sequence_length, 1)
    """
    X, y = [], []
    data = np.array(data, dtype=np.float32)
    
    for i in range(len(data) - sequence_length):
        X.append(data[i:i + sequence_length])
        y.append(data[i + sequence_length])
    
    X = np.array(X).reshape(-1, sequence_length, 1)
    y = np.array(y)
    
    return X, y


def normalize_data(data):
    """
    Min-Max normalization for neural network input.
    
    Args:
        data: Array of values
        
    Returns:
        Tuple of (normalized_data, min_val, max_val)
    """
    data = np.array(data, dtype=np.float32)
    min_val = data.min()
    max_val = data.max()
    
    if max_val - min_val == 0:
        return np.zeros_like(data), min_val, max_val
    
    normalized = (data - min_val) / (max_val - min_val)
    return normalized, min_val, max_val


def denormalize_data(normalized_data, min_val, max_val):
    """
    Reverses Min-Max normalization.
    
    Args:
        normalized_data: Normalized values
        min_val: Original minimum value
        max_val: Original maximum value
        
    Returns:
        Denormalized values
    """
    if max_val - min_val == 0:
        return np.full_like(normalized_data, min_val)
    
    return normalized_data * (max_val - min_val) + min_val
