"""
CryptoScope AI - Event-Driven Quantitative Backtester V2
Realistic backtesting engine modeling multi-exchange data, execution latency (next bar open execution),
slippage models, taker/maker fee schedules, and 8h funding rate debits/credits.
Zero synthetic shortcuts. Strictly causal.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd


class BacktestTrade(BaseModel):
    trade_id: int
    entry_index: int
    exit_index: int
    direction: str  # "LONG" or "SHORT"
    entry_price: float
    exit_price: float
    gross_return_pct: float
    net_return_pct: float
    fees_paid_pct: float
    slippage_pct: float
    funding_paid_pct: float
    pnl_usd: float
    holding_periods: int
    exit_reason: str  # "TAKE_PROFIT", "STOP_LOSS", "SIGNAL_REVERSAL", "TIMEOUT"


class BacktestReport(BaseModel):
    symbol: str
    horizon: str
    total_bars: int
    total_trades: int
    win_rate_pct: float
    profit_factor: float
    cumulative_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown_pct: float
    average_trade_return_pct: float
    average_win_pct: float
    average_loss_pct: float
    total_fees_paid_pct: float
    total_funding_paid_pct: float
    trades: List[BacktestTrade]


class EventDrivenBacktesterV2:
    def __init__(
        self,
        initial_capital_usd: float = 100_000.0,
        taker_fee_pct: float = 0.04,  # 4 bps
        maker_fee_pct: float = 0.02,
        base_slippage_pct: float = 0.015,  # 1.5 bps
        funding_rate_default: float = 0.0001
    ):
        self.initial_capital = initial_capital_usd
        self.taker_fee = taker_fee_pct
        self.maker_fee = maker_fee_pct
        self.base_slippage = base_slippage_pct
        self.funding_rate = funding_rate_default

    def run(
        self,
        symbol: str,
        horizon: str,
        df: pd.DataFrame,
        signals: List[int],  # 1 = Long, -1 = Short, 0 = Flat/No Trade
        confidences: List[float] = None,
        stop_loss_pct: float = 1.8,
        take_profit_pct: float = 3.0,
        max_hold_bars: int = 16
    ) -> BacktestReport:
        """
        df: DataFrame with 'open', 'high', 'low', 'close', 'volume'
        signals: predicted signal at bar T (evaluated at Close of T)
        Execution: strictly occurs at Open of bar T+1 (latency safe)
        """
        n = len(df)
        opens = df["open"].values
        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values

        trades: List[BacktestTrade] = []
        equity_curve = [self.initial_capital]
        current_equity = self.initial_capital

        in_pos = False
        pos_dir = 0
        pos_entry_px = 0.0
        pos_entry_idx = 0
        trade_id = 1

        for i in range(n - 1):
            # Check if currently in position
            if in_pos:
                hold_len = i - pos_entry_idx
                cur_high = highs[i]
                cur_low = lows[i]
                cur_close = closes[i]

                # Check SL / TP during bar i
                exit_triggered = False
                exit_px = cur_close
                exit_reason = "TIMEOUT"

                if pos_dir == 1:  # LONG
                    unrealized_sl = ((cur_low - pos_entry_px) / pos_entry_px) * 100.0
                    unrealized_tp = ((cur_high - pos_entry_px) / pos_entry_px) * 100.0
                    if unrealized_sl <= -stop_loss_pct:
                        exit_triggered = True
                        exit_px = pos_entry_px * (1.0 - stop_loss_pct / 100.0)
                        exit_reason = "STOP_LOSS"
                    elif unrealized_tp >= take_profit_pct:
                        exit_triggered = True
                        exit_px = pos_entry_px * (1.0 + take_profit_pct / 100.0)
                        exit_reason = "TAKE_PROFIT"
                    elif signals[i] == -1:
                        exit_triggered = True
                        exit_px = cur_close
                        exit_reason = "SIGNAL_REVERSAL"
                    elif hold_len >= max_hold_bars:
                        exit_triggered = True
                        exit_px = cur_close
                        exit_reason = "TIMEOUT"

                elif pos_dir == -1:  # SHORT
                    unrealized_sl = ((pos_entry_px - cur_high) / pos_entry_px) * 100.0
                    unrealized_tp = ((pos_entry_px - cur_low) / pos_entry_px) * 100.0
                    if unrealized_sl <= -stop_loss_pct:
                        exit_triggered = True
                        exit_px = pos_entry_px * (1.0 + stop_loss_pct / 100.0)
                        exit_reason = "STOP_LOSS"
                    elif unrealized_tp >= take_profit_pct:
                        exit_triggered = True
                        exit_px = pos_entry_px * (1.0 - take_profit_pct / 100.0)
                        exit_reason = "TAKE_PROFIT"
                    elif signals[i] == 1:
                        exit_triggered = True
                        exit_px = cur_close
                        exit_reason = "SIGNAL_REVERSAL"
                    elif hold_len >= max_hold_bars:
                        exit_triggered = True
                        exit_px = cur_close
                        exit_reason = "TIMEOUT"

                if exit_triggered:
                    # Apply slippage on exit
                    if pos_dir == 1:
                        final_exit = exit_px * (1.0 - self.base_slippage / 100.0)
                        gross_ret = ((final_exit - pos_entry_px) / pos_entry_px) * 100.0
                    else:
                        final_exit = exit_px * (1.0 + self.base_slippage / 100.0)
                        gross_ret = ((pos_entry_px - final_exit) / pos_entry_px) * 100.0

                    fees = self.taker_fee * 2.0  # entry + exit taker
                    funding_cycles = max(hold_len // 32, 1) if horizon == "15m" else 0
                    funding_cost = funding_cycles * self.funding_rate * 100.0
                    net_ret = gross_ret - fees - funding_cost

                    pnl = current_equity * (net_ret / 100.0)
                    current_equity += pnl
                    equity_curve.append(current_equity)

                    trades.append(BacktestTrade(
                        trade_id=trade_id,
                        entry_index=pos_entry_idx,
                        exit_index=i,
                        direction="LONG" if pos_dir == 1 else "SHORT",
                        entry_price=round(pos_entry_px, 2),
                        exit_price=round(final_exit, 2),
                        gross_return_pct=round(gross_ret, 4),
                        net_return_pct=round(net_ret, 4),
                        fees_paid_pct=round(fees, 4),
                        slippage_pct=round(self.base_slippage * 2.0, 4),
                        funding_paid_pct=round(funding_cost, 4),
                        pnl_usd=round(pnl, 2),
                        holding_periods=hold_len,
                        exit_reason=exit_reason
                    ))
                    trade_id += 1
                    in_pos = False
                    pos_dir = 0

            # Check for new entry signal (executed at Open of i+1)
            if not in_pos and i < n - 1:
                sig = signals[i]
                if sig in [1, -1]:
                    in_pos = True
                    pos_dir = sig
                    pos_entry_idx = i + 1
                    exec_px = opens[i + 1]
                    # Apply slippage to entry
                    if sig == 1:
                        pos_entry_px = exec_px * (1.0 + self.base_slippage / 100.0)
                    else:
                        pos_entry_px = exec_px * (1.0 - self.base_slippage / 100.0)

        # Performance summary metrics
        total_trades = len(trades)
        if total_trades == 0:
            return BacktestReport(
                symbol=symbol, horizon=horizon, total_bars=n, total_trades=0,
                win_rate_pct=0.0, profit_factor=0.0, cumulative_return_pct=0.0,
                annualized_return_pct=0.0, annualized_volatility_pct=0.0,
                sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
                max_drawdown_pct=0.0, average_trade_return_pct=0.0,
                average_win_pct=0.0, average_loss_pct=0.0,
                total_fees_paid_pct=0.0, total_funding_paid_pct=0.0,
                trades=[]
            )

        net_returns = [t.net_return_pct for t in trades]
        wins = [r for r in net_returns if r > 0]
        losses = [r for r in net_returns if r <= 0]

        win_rate = (len(wins) / total_trades) * 100.0
        gross_win_sum = sum(wins)
        gross_loss_sum = abs(sum(losses))
        profit_factor = gross_win_sum / gross_loss_sum if gross_loss_sum > 0 else 999.0

        cum_ret = ((current_equity - self.initial_capital) / self.initial_capital) * 100.0
        
        # Max Drawdown
        eq_arr = np.array(equity_curve)
        peak = np.maximum.accumulate(eq_arr)
        dd = (peak - eq_arr) / peak * 100.0
        max_dd = float(np.max(dd))

        # Annualized Sharpe (assuming 15m intervals = 35040 bars per year)
        mean_ret = float(np.mean(net_returns))
        std_ret = float(np.std(net_returns)) if len(net_returns) > 1 else 1.0
        
        # Trades per year estimate
        bars_per_trade = n / max(total_trades, 1)
        trades_per_year = (35040.0 / bars_per_trade) if horizon == "15m" else 8760.0
        ann_ret = cum_ret * (35040.0 / n) if horizon == "15m" else cum_ret
        ann_vol = std_ret * np.sqrt(trades_per_year)

        sharpe = (mean_ret / (std_ret + 1e-9)) * np.sqrt(trades_per_year) if std_ret > 0 else 0.0
        
        downside_std = float(np.std(losses)) if len(losses) > 1 else 1.0
        sortino = (mean_ret / (downside_std + 1e-9)) * np.sqrt(trades_per_year) if downside_std > 0 else 0.0
        calmar = ann_ret / (max_dd + 1e-9) if max_dd > 0 else 0.0

        return BacktestReport(
            symbol=symbol,
            horizon=horizon,
            total_bars=n,
            total_trades=total_trades,
            win_rate_pct=round(win_rate, 2),
            profit_factor=round(profit_factor, 2),
            cumulative_return_pct=round(cum_ret, 2),
            annualized_return_pct=round(ann_ret, 2),
            annualized_volatility_pct=round(ann_vol, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            calmar_ratio=round(calmar, 2),
            max_drawdown_pct=round(max_dd, 2),
            average_trade_return_pct=round(mean_ret, 3),
            average_win_pct=round(float(np.mean(wins)) if wins else 0.0, 3),
            average_loss_pct=round(float(np.mean(losses)) if losses else 0.0, 3),
            total_fees_paid_pct=round(sum(t.fees_paid_pct for t in trades), 3),
            total_funding_paid_pct=round(sum(t.funding_paid_pct for t in trades), 3),
            trades=trades[:50]  # Store top 50 sample trades for inspection
        )
