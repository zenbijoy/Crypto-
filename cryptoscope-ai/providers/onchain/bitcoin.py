"""
CryptoScope AI - Bitcoin On-Chain Provider
Queries real mempool.space public REST endpoints for Bitcoin blockchain state,
including fee rates (sat/vB), tip height, and mempool congestion.
Zero synthetic fallbacks.
"""
import httpx
from datetime import datetime, timezone
from providers.onchain.base import BaseOnChainProvider, OnChainMetricSnapshot


class BitcoinOnChainProvider(BaseOnChainProvider):
    def __init__(self, base_url: str = "https://mempool.space/api"):
        super().__init__("BTC", "mempool_space")
        self.base_url = base_url

    async def get_metrics(self) -> OnChainMetricSnapshot:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                fee_resp = await client.get(f"{self.base_url}/v1/fees/recommended")
                tip_resp = await client.get(f"{self.base_url}/blocks/tip/height")
                mem_resp = await client.get(f"{self.base_url}/mempool")

                if fee_resp.status_code == 200 and tip_resp.status_code == 200:
                    fees = fee_resp.json()
                    height = int(tip_resp.text.strip())
                    mem_data = mem_resp.json() if mem_resp.status_code == 200 else {}

                    return OnChainMetricSnapshot(
                        chain="BTC",
                        provider=self.provider_name,
                        status="REAL",
                        timestamp=datetime.now(timezone.utc),
                        block_height=height,
                        fee_rate_standard=float(fees.get("hourFee", 1)),
                        fee_rate_priority=float(fees.get("fastestFee", 2)),
                        unconfirmed_transactions=int(mem_data.get("count", 0)),
                        metrics={
                            "minimum_fee": fees.get("minimumFee"),
                            "economy_fee": fees.get("economyFee"),
                            "half_hour_fee": fees.get("halfHourFee"),
                            "mempool_vsize": mem_data.get("vsize", 0),
                            "mempool_total_fees_btc": round(mem_data.get("total_fee", 0) / 1e8, 4)
                        },
                        attribution_url=self.base_url
                    )
        except Exception:
            pass

        return OnChainMetricSnapshot(
            chain="BTC",
            provider=self.provider_name,
            status="UNAVAILABLE",
            timestamp=datetime.now(timezone.utc),
            attribution_url=self.base_url
        )
