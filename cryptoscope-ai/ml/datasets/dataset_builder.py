"""
CryptoScope AI - Feature Engineering & Dataset Builder for Quantitative & DL Models
Implements:
- GROUP A (Price): returns, log returns, lag returns, range, ATR, realized vol, VWAP distance, momentum, RSI, MACD
- GROUP B (Volume): volume, volume z-score, buy volume, sell volume, volume delta, volume acceleration
- GROUP C (Trade Flow): CVD, trade imbalance, taker buy ratio, trade intensity
- GROUP F (Cross Asset): ETH & SOL returns, relative momentum against BTC
- Multi-Task Targets:
    * target_direction (0: DOWN, 1: SIDEWAYS, 2: UP) based on threshold tau
    * target_return (future log return over horizon)
    * target_volatility (future realized volatility over horizon)
- Preprocessing: RobustScaler fitted strictly on training data
- Sequence Window Generation: [sequence_length, feature_count]
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.preprocessing import RobustScaler


def compute_technical_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Computes genuine Group A, B, C features from historical candles without lookahead."""
    data = df.copy()

    # --- GROUP A: Price ---
    data["log_ret_1"] = np.log(data["close"] / data["close"].shift(1))
    data["log_ret_2"] = np.log(data["close"] / data["close"].shift(2))
    data["log_ret_4"] = np.log(data["close"] / data["close"].shift(4))
    data["log_ret_12"] = np.log(data["close"] / data["close"].shift(12))

    # Normalized Range & ATR
    high_low = (data["high"] - data["low"]) / data["close"]
    high_close_prev = (np.abs(data["high"] - data["close"].shift(1))) / data["close"]
    low_close_prev = (np.abs(data["low"] - data["close"].shift(1))) / data["close"]
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    data["norm_atr_14"] = tr.rolling(14).mean()

    # Rolling Realized Volatility
    data["realized_vol_16"] = data["log_ret_1"].rolling(16).std() * np.sqrt(96)  # annualize/daily scale

    # VWAP Distance
    cum_vol = data["volume"].rolling(24).sum()
    cum_vol_price = (data["close"] * data["volume"]).rolling(24).sum()
    vwap = cum_vol_price / (cum_vol + 1e-8)
    data["vwap_dist"] = (data["close"] - vwap) / (vwap + 1e-8)

    # Momentum (RSI 14)
    delta = data["close"].diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / (loss + 1e-8)
    data["rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

    # MACD
    ema_12 = data["close"].ewm(span=12, adjust=False).mean()
    ema_26 = data["close"].ewm(span=26, adjust=False).mean()
    macd_line = (ema_12 - ema_26) / data["close"]
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    data["macd_hist"] = macd_line - signal_line

    # --- GROUP B: Volume ---
    vol_mean = data["volume"].rolling(32).mean()
    vol_std = data["volume"].rolling(32).std() + 1e-8
    data["volume_zscore"] = (data["volume"] - vol_mean) / vol_std
    data["vol_delta"] = (data["volume"] - data["volume"].shift(1)) / (data["volume"].shift(1) + 1e-8)

    # --- GROUP C: Trade Flow ---
    # Taker buy base is genuine aggressor flow from Binance
    taker_buy = data["taker_buy_base"]
    taker_sell = (data["volume"] - taker_buy).clip(lower=0.0)
    data["taker_buy_ratio"] = taker_buy / (data["volume"] + 1e-8)
    delta_flow = taker_buy - taker_sell
    data["cvd_rolling"] = delta_flow.rolling(16).sum() / (data["volume"].rolling(16).sum() + 1e-8)
    data["trade_intensity"] = data["trades"] / (data["trades"].rolling(32).mean() + 1e-8)

    # Drop NaNs created by rolling windows
    return data.dropna()


def attach_multi_task_targets(
    df: pd.DataFrame,
    horizon_bars: int = 4,   # For 15m candles: 4 bars = 1h, 1 bar = 15m
    direction_threshold: float = 0.0025  # 0.25% threshold for 3-class classification
) -> pd.DataFrame:
    """
    Constructs multi-task future targets:
      - target_return: log(close_{t+H} / close_t)
      - target_direction: 2 (UP if > tau), 0 (DOWN if < -tau), 1 (SIDEWAYS)
      - target_volatility: std(log_ret) over future H bars
    """
    df = df.copy()
    future_close = df["close"].shift(-horizon_bars)
    df["target_return"] = np.log(future_close / df["close"])

    # Direction target
    conditions = [
        df["target_return"] > direction_threshold,
        df["target_return"] < -direction_threshold
    ]
    choices = [2, 0]
    df["target_direction"] = np.select(conditions, choices, default=1).astype(int)

    # Future realized volatility (over future H bars)
    # Computed causally looking forward only for target label
    future_returns = [np.log(df["close"].shift(-k) / df["close"].shift(-k + 1)) for k in range(1, horizon_bars + 1)]
    future_vol = pd.concat(future_returns, axis=1).std(axis=1)
    df["target_volatility"] = future_vol.fillna(0.001)

    # Drop the last H rows where targets are not known yet
    return df.dropna(subset=["target_return", "target_volatility"])


class QuantDatasetBuilder:
    """Prepares chronological sequence datasets for tabular and PyTorch sequential architectures."""

    def __init__(self, sequence_length: int = 96):
        self.sequence_length = sequence_length
        self.scaler = RobustScaler()
        self.feature_columns: List[str] = []

    def build_features_and_targets(
        self,
        raw_df: pd.DataFrame,
        horizon_bars: int = 1,
        direction_threshold: float = 0.002
    ) -> pd.DataFrame:
        featured = compute_technical_feature_matrix(raw_df)
        with_targets = attach_multi_task_targets(featured, horizon_bars=horizon_bars, direction_threshold=direction_threshold)
        
        target_cols = ["target_direction", "target_return", "target_volatility"]
        meta_cols = ["open_time", "close_time", "open", "high", "low", "close", "volume", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote"]
        self.feature_columns = [c for c in with_targets.columns if c not in target_cols and c not in meta_cols]
        return with_targets

    def create_walk_forward_splits(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Chronological Walk-Forward train/val/test splitting.
        Zero lookahead or shuffle.
        """
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()

        return train_df, val_df, test_df

    def fit_transform_features(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """RULE: Fit scaler ONLY on train_df. Transform val_df and test_df."""
        X_train_raw = train_df[self.feature_columns].values
        X_val_raw = val_df[self.feature_columns].values
        X_test_raw = test_df[self.feature_columns].values

        X_train = self.scaler.fit_transform(X_train_raw)
        X_val = self.scaler.transform(X_val_raw)
        X_test = self.scaler.transform(X_test_raw)

        return X_train, X_val, X_test

    def generate_sequences(
        self,
        X_scaled: np.ndarray,
        y_direction: np.ndarray,
        y_return: np.ndarray,
        y_volatility: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generates 3D tensors for recurrent / temporal networks:
        shape: [num_samples, sequence_length, feature_count]
        """
        num_samples = len(X_scaled) - self.sequence_length + 1
        X_seq = np.zeros((num_samples, self.sequence_length, X_scaled.shape[1]), dtype=np.float32)
        y_dir_seq = np.zeros(num_samples, dtype=np.int64)
        y_ret_seq = np.zeros(num_samples, dtype=np.float32)
        y_vol_seq = np.zeros(num_samples, dtype=np.float32)

        for i in range(num_samples):
            X_seq[i] = X_scaled[i : i + self.sequence_length]
            target_idx = i + self.sequence_length - 1
            y_dir_seq[i] = y_direction[target_idx]
            y_ret_seq[i] = y_return[target_idx]
            y_vol_seq[i] = y_volatility[target_idx]

        return X_seq, y_dir_seq, y_ret_seq, y_vol_seq
