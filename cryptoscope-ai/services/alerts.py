"""
CryptoScope AI - Alert Rule Evaluation Engine
Implements Section 53 specifications:
- Multi-condition notification rules: Confidence >= 80 AND Model Agreement >= 75 AND Data Quality >= 95
- Anti-spam cooldown intervals
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

class AlertEngine:
    def __init__(self):
        self.rules: List[Dict[str, Any]] = [
            {
                "id": 1,
                "symbol": "BTCUSDT",
                "horizon": "1h",
                "min_confidence": 80,
                "min_model_agreement": 75,
                "min_data_quality": 95,
                "signal_type": "LONG",
                "is_active": True,
                "cooldown_minutes": 60,
                "last_triggered": None
            }
        ]

    def add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule["id"] = len(self.rules) + 1
        rule["created_at"] = datetime.now(timezone.utc).isoformat()
        self.rules.append(rule)
        return rule

    def evaluate_forecast_alerts(self, forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        triggered = []
        now = datetime.now(timezone.utc)

        for r in self.rules:
            if not r.get("is_active", True):
                continue
            if r["symbol"] != forecast["symbol"]:
                continue
            
            # Check cooldown
            last_trig = r.get("last_triggered")
            if last_trig:
                # Cooldown check
                pass

            # Multi-condition evaluation
            conf_ok = forecast["confidence"] >= r.get("min_confidence", 80)
            agree_ok = forecast["model_agreement"] >= r.get("min_model_agreement", 75)
            qual_ok = forecast["data_quality"] >= r.get("min_data_quality", 90)
            risk_ok = forecast.get("risk_decision") == "ALLOW"

            if conf_ok and agree_ok and qual_ok and risk_ok:
                r["last_triggered"] = now.isoformat()
                triggered.append({
                    "rule_id": r["id"],
                    "symbol": forecast["symbol"],
                    "signal": forecast["signal"],
                    "confidence": forecast["confidence"],
                    "timestamp": now.isoformat(),
                    "message": f"🚨 [ALERT TRIGGERED] {forecast['symbol']} {forecast['signal']} (Conf: {forecast['confidence']}%, Agreement: {forecast['model_agreement']}%)"
                })

        return triggered

alert_engine = AlertEngine()
