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
        self.accounts: Dict[str, PaperAccount] = {}

    def get_account(self, user_id: str = "default") -> PaperAccount:
        if user_id not in self.accounts:
            self.accounts[user_id] = PaperAccount(account_id=user_id)
        return self.accounts[user_id]

    @property
    def account(self) -> PaperAccount:
        """Default account for backward compatibility."""
        return self.get_account("default")

    def execute_market_order(
        self,
        symbol: str,
        side: str,  # "BUY" (open long / close short) or "SELL" (open short / close long)
        size_usd: float,
        current_mid: float,
        spread_bps: float = 1.0,
        leverage: float = 2.0,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        acct = self.get_account(user_id)
        margin_required = size_usd / leverage
        fee = size_usd * (self.taker_fee / 100.0)

        if acct.available_balance_usd < (margin_required + fee):
            raise ValueError(
                f"Insufficient available margin: {acct.available_balance_usd:.2f} USD available, "
                f"{margin_required + fee:.2f} USD required."
            )

        # Taker execution price crossing half spread (1 bp = 0.0001)
        half_spread_fraction = (spread_bps / 2.0) / 10000.0
        if side == "BUY":
            fill_px = current_mid * (1.0 + half_spread_fraction)
        else:
            fill_px = current_mid * (1.0 - half_spread_fraction)

        acct.total_fees_paid_usd += fee
        acct.available_balance_usd -= (margin_required + fee)

        # Leverage-aware liquidation calculation
        liq_buffer = (1.0 / leverage) * 0.95
        if side == "BUY":
            liq_px = fill_px * max(0.0, 1.0 - liq_buffer)
        else:
            liq_px = fill_px * (1.0 + liq_buffer)

        pos_id = f"pos_{len(acct.trade_history) + 1}"
        pos = PaperPosition(
            position_id=pos_id,
            symbol=symbol,
            side="LONG" if side == "BUY" else "SHORT",
            entry_price=round(fill_px, 2),
            size_usd=round(size_usd, 2),
            leverage=leverage,
            liquidation_price=round(liq_px, 2)
        )
        acct.positions[pos_id] = pos

        order_record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "position_id": pos_id,
            "symbol": symbol,
            "side": side,
            "fill_price": round(fill_px, 2),
            "size_usd": size_usd,
            "fee_usd": round(fee, 2),
            "leverage": leverage
        }
        acct.trade_history.append(order_record)
        return order_record

    def close_position(
        self,
        pos_id: str,
        current_mid: float,
        user_id: str = "default"
    ) -> Optional[Dict[str, Any]]:
        acct = self.get_account(user_id)
        pos = acct.positions.pop(pos_id, None)
        if not pos:
            # Check if searched by symbol or symbol_side
            for k, p in list(acct.positions.items()):
                if p.symbol == pos_id or k == pos_id:
                    pos = acct.positions.pop(k)
                    break
        if not pos:
            return None

        fee = pos.size_usd * (self.taker_fee / 100.0)
        acct.total_fees_paid_usd += fee

        if pos.side == "LONG":
            ret_pct = (current_mid - pos.entry_price) / pos.entry_price
        else:
            ret_pct = (pos.entry_price - current_mid) / pos.entry_price

        gross_pnl = pos.size_usd * ret_pct
        net_pnl = gross_pnl - fee
        acct.realized_pnl_usd += net_pnl
        margin_released = pos.size_usd / pos.leverage
        acct.available_balance_usd += (margin_released + net_pnl)
        acct.equity_usd = acct.available_balance_usd + sum(
            p.size_usd / p.leverage for p in acct.positions.values()
        )

        close_record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "position_id": pos.position_id,
            "entry_price": pos.entry_price,
            "exit_price": round(current_mid, 2),
            "gross_pnl_usd": round(gross_pnl, 2),
            "net_pnl_usd": round(net_pnl, 2),
            "return_pct": round(ret_pct * 100.0, 3)
        }
        acct.trade_history.append(close_record)
        return close_record
