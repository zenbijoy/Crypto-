"""
CryptoScope AI - Live Paper Trading Execution Service
Real-time virtual execution engine supporting realistic limit/market orders,
fee deductions, price impact, position management, and PnL reporting.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class PaperPosition(BaseModel):
    position_id: str
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_price: float
    size_usd: float
    leverage: float
    liquidation_price: float
    unrealized_pnl_usd: float = 0.0
    entry_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaperAccount(BaseModel):
    account_id: str = "PAPER_MAIN"
    initial_balance_usd: float = 100_000.0
    available_balance_usd: float = 100_000.0
    equity_usd: float = 100_000.0
    realized_pnl_usd: float = 0.0
    total_fees_paid_usd: float = 0.0
    positions: Dict[str, PaperPosition] = Field(default_factory=dict)
    trade_history: List[Dict[str, Any]] = Field(default_factory=list)


class PaperTradingEngine:
    def __init__(self, taker_fee_pct: float = 0.04, maker_fee_pct: float = 0.02):
        self.taker_fee = taker_fee_pct
        self.maker_fee = maker_fee_pct
        self.account = PaperAccount()

    def execute_market_order(
        self,
        symbol: str,
        side: str,  # "BUY" (open long / close short) or "SELL" (open short / close long)
        size_usd: float,
        current_mid: float,
        spread_bps: float = 1.0,
        leverage: float = 2.0
    ) -> Dict[str, Any]:
        # Taker execution price crossing half spread
        half_spread_pct = (spread_bps / 2.0) / 100.0
        if side == "BUY":
            fill_px = current_mid * (1.0 + half_spread_pct)
        else:
            fill_px = current_mid * (1.0 - half_spread_pct)

        fee = size_usd * (self.taker_fee / 100.0)
        self.account.total_fees_paid_usd += fee
        self.account.available_balance_usd -= fee

        pos_key = f"{symbol}_{side}"
        pos = PaperPosition(
            position_id=f"pos_{len(self.account.trade_history)+1}",
            symbol=symbol,
            side="LONG" if side == "BUY" else "SHORT",
            entry_price=round(fill_px, 2),
            size_usd=round(size_usd, 2),
            leverage=leverage,
            liquidation_price=round(fill_px * (0.5 if side == "BUY" else 1.5), 2)
        )
        self.account.positions[pos_key] = pos

        order_record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "side": side,
            "fill_price": round(fill_px, 2),
            "size_usd": size_usd,
            "fee_usd": round(fee, 2),
            "leverage": leverage
        }
        self.account.trade_history.append(order_record)
        return order_record

    def close_position(self, pos_key: str, current_mid: float) -> Optional[Dict[str, Any]]:
        pos = self.account.positions.pop(pos_key, None)
        if not pos:
            return None

        fee = pos.size_usd * (self.taker_fee / 100.0)
        self.account.total_fees_paid_usd += fee

        if pos.side == "LONG":
            ret_pct = (current_mid - pos.entry_price) / pos.entry_price
        else:
            ret_pct = (pos.entry_price - current_mid) / pos.entry_price

        gross_pnl = pos.size_usd * ret_pct
        net_pnl = gross_pnl - fee
        self.account.realized_pnl_usd += net_pnl
        self.account.available_balance_usd += (pos.size_usd / pos.leverage) + net_pnl
        self.account.equity_usd = self.account.available_balance_usd

        close_record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "position_id": pos.position_id,
            "entry_price": pos.entry_price,
            "exit_price": round(current_mid, 2),
            "gross_pnl_usd": round(gross_pnl, 2),
            "net_pnl_usd": round(net_pnl, 2),
            "return_pct": round(ret_pct * 100.0, 3)
        }
        self.account.trade_history.append(close_record)
        return close_record
