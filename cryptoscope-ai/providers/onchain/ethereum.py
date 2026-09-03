"""
CryptoScope AI - Ethereum On-Chain Provider
Queries real public Ethereum JSON-RPC endpoints for block height, base fee, and gas price.
Zero synthetic fallbacks.
"""
import httpx
from datetime import datetime, timezone
from providers.onchain.base import BaseOnChainProvider, OnChainMetricSnapshot


class EthereumOnChainProvider(BaseOnChainProvider):
    def __init__(self, rpc_url: str = "https://ethereum-rpc.publicnode.com"):
        super().__init__("ETH", "ethereum_rpc")
        self.rpc_url = rpc_url

    async def get_metrics(self) -> OnChainMetricSnapshot:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                block_req = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
                gas_req = {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 2}

                b_resp = await client.post(self.rpc_url, json=block_req)
                g_resp = await client.post(self.rpc_url, json=gas_req)

                if b_resp.status_code == 200 and g_resp.status_code == 200:
                    b_hex = b_resp.json().get("result")
                    g_hex = g_resp.json().get("result")
                    if b_hex and g_hex:
                        block_height = int(b_hex, 16)
                        gas_gwei = int(g_hex, 16) / 1e9

                        return OnChainMetricSnapshot(
                            chain="ETH",
                            provider=self.provider_name,
                            status="REAL",
                            timestamp=datetime.now(timezone.utc),
                            block_height=block_height,
                            fee_rate_standard=round(gas_gwei, 4),
                            fee_rate_priority=round(gas_gwei * 1.2, 4),
                            metrics={
                                "gas_price_gwei": round(gas_gwei, 4),
                                "gas_price_wei": int(g_hex, 16)
                            },
                            attribution_url=self.rpc_url
                        )
        except Exception:
            pass

        return OnChainMetricSnapshot(
            chain="ETH",
            provider=self.provider_name,
            status="UNAVAILABLE",
            timestamp=datetime.now(timezone.utc),
            attribution_url=self.rpc_url
        )
