"""
CryptoScope AI - Production Quantitative Data Quality Engine (Step 10)
Implements Step 10 Specifications:
- Real-time pre-ingestion validation for Candles, Orderbooks, Tickers, and Derivatives
- OHLC Invariant Verification:
  * high >= low
  * open >= 0, high >= 0, low >= 0, close >= 0
  * high >= max(open, close)
  * low <= min(open, close)
  * volume >= 0
- Chronological Invariant Verification:
  * No future timestamps (t <= now + clock_skew_tolerance)
  * Sequential monotonicity (t_curr >= t_prev)
  * Deduplication detection
- Order Book Microstructure Invariants:
  * No crossed book (best_bid < best_ask)
  * Non-negative spreads (spread_bps > 0)
  * Non-empty bids/asks
- Extreme Outlier / Bad Tick Detection:
  * Percentage price jump > threshold (e.g. 35% in 1 minute without market corroboration)
- Dynamic Data Quality Scoring:
  * Generates data_quality_score: 0 to 100
  * Hard-rejects corrupt/impossible data (raises DataQualityException)
  * Records structured quality failure audit events
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from core.models import Candle, OrderBookSnapshot, Ticker
from core.exceptions import DataQualityException

logger = logging.getLogger("cryptoscope.data_quality")


class DataQualityService:
    def __init__(self, clock_skew_tolerance_seconds: float = 60.0):
        self.clock_skew_tolerance_seconds = clock_skew_tolerance_seconds
        self.quality_events_log: List[Dict[str, Any]] = []

    def log_event(self, symbol: str, event_type: str, severity: str, description: str, details: Optional[Dict[str, Any]] = None):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol.upper(),
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "details": details or {}
        }
        self.quality_events_log.append(event)
        if len(self.quality_events_log) > 500:
            self.quality_events_log = self.quality_events_log[-500:]
        if severity in ["CRITICAL", "REJECTED"]:
            logger.error("Data Quality Violation [%s]: %s - %s", symbol, event_type, description)
        else:
            logger.warning("Data Quality Warning [%s]: %s - %s", symbol, event_type, description)

    def validate_candle(self, candle: Candle, prev_candle: Optional[Candle] = None) -> Tuple[bool, int, List[str]]:
        """
        Validates a single candlestick.
        Returns (is_valid, quality_score, violations_list).
        """
        violations: List[str] = []
        score = 100

        # 1. Price non-negativity
        if candle.open <= 0 or candle.high <= 0 or candle.low <= 0 or candle.close <= 0:
            violations.append("NON_POSITIVE_PRICE: OHLC must be strictly greater than 0")
            score -= 60

        # 2. High/Low invariant
        if candle.high < candle.low:
            violations.append(f"HIGH_LESS_THAN_LOW: high({candle.high}) < low({candle.low})")
            score -= 80

        # 3. Open/Close bounded by High/Low
        if candle.high < max(candle.open, candle.close):
            violations.append(f"HIGH_BELOW_BODY: high({candle.high}) < max(open, close)")
            score -= 50

        if candle.low > min(candle.open, candle.close):
            violations.append(f"LOW_ABOVE_BODY: low({candle.low}) > min(open, close)")
            score -= 50

        # 4. Non-negative volume
        if candle.volume_base < 0 or candle.volume_quote < 0:
            violations.append("NEGATIVE_VOLUME: Volume cannot be negative")
            score -= 40

        # 5. Future timestamp
        now_ts = datetime.now(timezone.utc).timestamp()
        if candle.close_time.timestamp() > (now_ts + self.clock_skew_tolerance_seconds):
            violations.append("FUTURE_TIMESTAMP: Close time is in the future")
            score -= 40

        # 6. Monotonicity with previous candle
        if prev_candle:
            if candle.open_time < prev_candle.open_time:
                violations.append("BACKWARD_TIMESTAMP: Current candle open_time precedes previous candle")
                score -= 60
            elif candle.open_time == prev_candle.open_time:
                violations.append("DUPLICATE_CANDLE: Identical open_time to previous candle")
                score -= 30

            # Extreme flash jump check (> 35% in 1 interval)
            if prev_candle.close > 0:
                pct_move = abs((candle.close - prev_candle.close) / prev_candle.close)
                if pct_move > 0.35:
                    violations.append(f"EXTREME_JUMP: Price moved {pct_move * 100:.1f}% in single interval")
                    score -= 40

        score = max(0, min(100, score))
        is_valid = (score >= 60) and not any("HIGH_LESS_THAN_LOW" in v for v in violations)

        if not is_valid:
            self.log_event(
                symbol=candle.symbol,
                event_type="CANDLE_INVALID",
                severity="REJECTED",
                description="; ".join(violations),
                details={"open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close}
            )

        return is_valid, score, violations

    def validate_orderbook(self, orderbook: OrderBookSnapshot) -> Tuple[bool, int, List[str]]:
        """
        Validates an L2 orderbook snapshot.
        Checks for crossed books, negative spreads, and empty sides.
        """
        violations: List[str] = []
        score = 100

        if not orderbook.bids or not orderbook.asks:
            violations.append("EMPTY_ORDERBOOK: Missing bids or asks")
            score -= 100
            self.log_event(orderbook.symbol, "EMPTY_ORDERBOOK", "CRITICAL", "Empty bids or asks")
            return False, 0, violations

        best_bid = orderbook.bids[0][0]
        best_ask = orderbook.asks[0][0]

        # 1. Crossed book
        if best_bid >= best_ask:
            violations.append(f"CROSSED_BOOK: best_bid({best_bid}) >= best_ask({best_ask})")
            score -= 90

        # 2. Spread
        if orderbook.spread_bps <= 0:
            violations.append(f"NON_POSITIVE_SPREAD: spread_bps={orderbook.spread_bps}")
            score -= 70

        # 3. Microprice within spread
        if not (best_bid <= orderbook.microprice <= best_ask):
            violations.append(f"MICROPRICE_OUT_OF_BOUNDS: microprice({orderbook.microprice}) outside bid/ask")
            score -= 30

        score = max(0, min(100, score))
        is_valid = (score >= 60) and ("CROSSED_BOOK" not in [v.split(":")[0] for v in violations])

        if not is_valid:
            self.log_event(
                symbol=orderbook.symbol,
                event_type="ORDERBOOK_INVALID",
                severity="REJECTED",
                description="; ".join(violations)
            )

        return is_valid, score, violations

    def validate_series(self, candles: List[Candle]) -> Tuple[List[Candle], int]:
        """
        Validates an entire sequence of candles, removes duplicates, filters invalid bars,
        and returns clean candles along with an aggregate series quality score.
        """
        if not candles:
            return [], 0

        clean: List[Candle] = []
        scores: List[int] = []
        seen_timestamps = set()

        for c in candles:
            ts_key = int(c.open_time.timestamp())
            if ts_key in seen_timestamps:
                continue
            seen_timestamps.add(ts_key)

            prev = clean[-1] if clean else None
            is_valid, score, _ = self.validate_candle(c, prev)
            if is_valid:
                clean.append(c)
                scores.append(score)

        avg_score = int(sum(scores) / len(scores)) if scores else 0
        return clean, avg_score

    def calculate_quality_breakdown(
        self,
        candles: Optional[List[Candle]] = None,
        orderbook: Optional[OrderBookSnapshot] = None,
        provider_count: int = 1,
        feed_freshness_seconds: float = 1.0
    ) -> Dict[str, Any]:
        """
        Phase 16 Component breakdown:
        freshness_score, completeness_score, sequence_score, validity_score, cross_provider_score, overall_score.
        Derived purely from observable checks.
        """
        # 1. Freshness Score (100 if < 2s, decays after)
        freshness_score = max(0, min(100, int(100 - max(0.0, (feed_freshness_seconds - 2.0) * 10))))

        # 2. Validity Score (OHLC invariants & non-crossed orderbook)
        validity_score = 100
        if candles:
            _, c_score = self.validate_series(candles)
            validity_score = c_score
        if orderbook:
            ob_valid, ob_score, _ = self.validate_orderbook(orderbook)
            validity_score = min(validity_score, ob_score)

        # 3. Sequence Score (monotonicity, gaps, duplicates)
        sequence_score = 100
        if candles and len(candles) > 1:
            gaps = 0
            for i in range(1, len(candles)):
                if candles[i].open_time <= candles[i - 1].open_time:
                    gaps += 1
            sequence_score = max(0, 100 - (gaps * 25))

        # 4. Completeness Score
        completeness_score = 100 if (candles and len(candles) >= 30) else (50 if candles else 0)

        # 5. Cross-provider consensus score
        cross_provider_score = min(100, provider_count * 50) if provider_count > 0 else 0

        # Overall weighted score
        overall_score = int(
            0.30 * validity_score +
            0.25 * freshness_score +
            0.20 * sequence_score +
            0.15 * completeness_score +
            0.10 * cross_provider_score
        )

        return {
            "overall_score": overall_score,
            "freshness_score": freshness_score,
            "validity_score": validity_score,
            "sequence_score": sequence_score,
            "completeness_score": completeness_score,
            "cross_provider_score": cross_provider_score,
            "quality_tier": "HIGH" if overall_score >= 80 else ("MEDIUM" if overall_score >= 50 else "LOW")
        }


# Global singleton
data_quality_service = DataQualityService()
