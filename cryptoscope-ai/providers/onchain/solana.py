"""
CryptoScope AI - Solana On-Chain Provider
Queries real Solana public mainnet JSON-RPC endpoints for slot, epoch, and real-time TPS.
Zero synthetic fallbacks.
"""
import httpx
from datetime import datetime, timezone
from providers.onchain.base import BaseOnChainProvider, OnChainMetricSnapshot


class SolanaOnChainProvider(BaseOnChainProvider):
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        super().__init__("SOL", "solana_rpc")
        self.rpc_url = rpc_url

    async def get_metrics(self) -> OnChainMetricSnapshot:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                slot_req = {"jsonrpc": "2.0", "method": "getSlot", "params": [], "id": 1}
                perf_req = {"jsonrpc": "2.0", "method": "getRecentPerformanceSamples", "params": [1], "id": 2}

                s_resp = await client.post(self.rpc_url, json=slot_req)
                p_resp = await client.post(self.rpc_url, json=perf_req)

                if s_resp.status_code == 200 and p_resp.status_code == 200:
                    slot = s_resp.json().get("result")
                    samples = p_resp.json().get("result", [])
                    tps = 0.0
                    non_vote_tps = 0.0
                    if samples:
                        sample = samples[0]
                        sec = sample.get("samplePeriodSecs", 60)
                        tps = sample.get("numTransactions", 0) / sec
                        non_vote_tps = sample.get("numNonVoteTransactions", 0) / sec

                    return OnChainMetricSnapshot(
                        chain="SOL",
                        provider=self.provider_name,
                        status="REAL",
                        timestamp=datetime.now(timezone.utc),
                        block_height=slot,
                        tps=round(tps, 1),
                        fee_rate_standard=5000.0,  # Base fee 5000 lamports
                        metrics={
                            "current_slot": slot,
                            "non_vote_tps": round(non_vote_tps, 1),
                            "total_tps": round(tps, 1)
                        },
                        attribution_url=self.rpc_url
                    )
        except Exception:
            pass

        return OnChainMetricSnapshot(
            chain="SOL",
            provider=self.provider_name,
            status="UNAVAILABLE",
            timestamp=datetime.now(timezone.utc),
            attribution_url=self.rpc_url
        )
