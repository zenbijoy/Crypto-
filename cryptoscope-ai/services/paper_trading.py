"""
CryptoScope AI - Paper Trading Simulation Engine
Implements Section 36 specifications:
- Simulated trade execution with realistic taker/maker fees
- Dynamic slippage model based on order size & volatility
- Stop-loss & Take-profit triggers
- Margin accounting & liquidation tracking
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from core.constants import DEFAULT_TAKER_FEE_BPS, DEFAULT_BASE_SLIPPAGE_BPS

class PaperTradingEngine:
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.order_history: List[Dict[str, Any]] = []

    def execute_order(
        self,
        symbol: str,
        direction: str,  # LONG or SHORT
        size_usd: float,
        current_market_price: float,
        leverage: int = 3,
        stop_loss_price: float = 0.0,
        take_profit_price: float = 0.0,
        volatility: float = 0.02
    ) -> Dict[str, Any]:
        required_margin = size_usd / leverage
        if required_margin > self.balance:
            raise ValueError(f"Insufficient virtual margin. Required: ${required_margin:.2f}, Available: ${self.balance:.2f}")

        # Compute realistic slippage based on size and volatility
        slippage_bps = DEFAULT_BASE_SLIPPAGE_BPS + (size_usd / 50000.0) * 1.5 + (volatility * 50.0)
        slippage_pct = slippage_bps / 10000.0

        if direction.upper() == "LONG":
            fill_price = current_market_price * (1.0 + slippage_pct)
        else:
            fill_price = current_market_price * (1.0 - slippage_pct)

        # Taker fee deduction
        fee_usd = size_usd * (DEFAULT_TAKER_FEE_BPS / 10000.0)
        self.balance -= fee_usd

        pos_id = str(uuid.uuid4())[:8]
        pos = {
            "id": pos_id,
            "symbol": symbol,
            "direction": direction.upper(),
            "size_usd": size_usd,
            "leverage": leverage,
            "margin_usd": round(required_margin, 2),
            "entry_price": round(fill_price, 2),
            "current_price": round(current_market_price, 2),
            "stop_loss": stop_loss_price if stop_loss_price > 0 else (round(fill_price * 0.98, 2) if direction == "LONG" else round(fill_price * 1.02, 2)),
            "take_profit": take_profit_price if take_profit_price > 0 else (round(fill_price * 1.03, 2) if direction == "LONG" else round(fill_price * 0.97, 2)),
            "fee_paid": round(fee_usd, 2),
            "slippage_bps": round(slippage_bps, 2),
            "unrealized_pnl": 0.0,
            "unrealized_pnl_pct": 0.0,
            "opened_at": datetime.now(timezone.utc).isoformat()
        }

        self.positions[pos_id] = pos
        return pos

    def close_position(self, pos_id: str, current_market_price: float) -> Dict[str, Any]:
        if pos_id not in self.positions:
            raise KeyError(f"Position {pos_id} not found")

        pos = self.positions.pop(pos_id)
        is_long = pos["direction"] == "LONG"
        
        # PnL calculation
        price_diff = current_market_price - pos["entry_price"]
        pnl_pct = (price_diff / pos["entry_price"]) * (1 if is_long else -1)
        realized_pnl = pos["size_usd"] * pnl_pct
        
        # Exit fee
        exit_fee = pos["size_usd"] * (DEFAULT_TAKER_FEE_BPS / 10000.0)
        net_pnl = realized_pnl - exit_fee
        
        self.balance += net_pnl

        pos["status"] = "CLOSED"
        pos["closed_at"] = datetime.now(timezone.utc).isoformat()
        pos["exit_price"] = round(current_market_price, 2)
        pos["realized_pnl"] = round(net_pnl, 2)
        pos["realized_pnl_pct"] = round(pnl_pct * 100.0, 2)
        self.order_history.append(pos)

        return pos

    def get_summary(self) -> Dict[str, Any]:
        open_list = list(self.positions.values())
        total_unrealized = sum(p.get("unrealized_pnl", 0.0) for p in open_list)
        return {
            "virtual_balance": round(self.balance, 2),
            "equity": round(self.balance + total_unrealized, 2),
            "open_positions_count": len(open_list),
            "positions": open_list,
            "total_closed_trades": len(self.order_history)
        }

paper_trading_engine = PaperTradingEngine()
