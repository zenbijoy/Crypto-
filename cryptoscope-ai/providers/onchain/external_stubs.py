"""
CryptoScope AI - External Analytics On-Chain Stubs (Glassnode, CryptoQuant, Dune)
Strictly adheres to Zero-Fake-Data Invariant:
Returns status='NOT_CONFIGURED' when API keys are not provided.
Never produces synthetic or hallucinated metrics.
"""
import os
from datetime import datetime, timezone
from providers.onchain.base import BaseOnChainProvider, OnChainMetricSnapshot


class GlassnodeOnChainProvider(BaseOnChainProvider):
    def __init__(self, api_key: str = None):
        super().__init__("BTC", "glassnode")
        self.api_key = api_key or os.environ.get("GLASSNODE_API_KEY")

    async def get_metrics(self) -> OnChainMetricSnapshot:
        if not self.api_key:
            return OnChainMetricSnapshot(
                chain="BTC",
                provider=self.provider_name,
                status="NOT_CONFIGURED",
                timestamp=datetime.now(timezone.utc),
                metrics={"reason": "GLASSNODE_API_KEY environment variable not set"}
            )
        # Real call when configured
        return OnChainMetricSnapshot(
            chain="BTC",
            provider=self.provider_name,
            status="UNAVAILABLE",
            timestamp=datetime.now(timezone.utc),
            metrics={"reason": "Provider connection pending verification"}
        )


class CryptoQuantOnChainProvider(BaseOnChainProvider):
    def __init__(self, api_key: str = None):
        super().__init__("BTC", "cryptoquant")
        self.api_key = api_key or os.environ.get("CRYPTOQUANT_API_KEY")

    async def get_metrics(self) -> OnChainMetricSnapshot:
        if not self.api_key:
            return OnChainMetricSnapshot(
                chain="BTC",
                provider=self.provider_name,
                status="NOT_CONFIGURED",
                timestamp=datetime.now(timezone.utc),
                metrics={"reason": "CRYPTOQUANT_API_KEY environment variable not set"}
            )
        return OnChainMetricSnapshot(
            chain="BTC",
            provider=self.provider_name,
            status="UNAVAILABLE",
            timestamp=datetime.now(timezone.utc),
            metrics={"reason": "Provider connection pending verification"}
        )


class DuneOnChainProvider(BaseOnChainProvider):
    def __init__(self, api_key: str = None):
        super().__init__("ETH", "dune")
        self.api_key = api_key or os.environ.get("DUNE_API_KEY")

    async def get_metrics(self) -> OnChainMetricSnapshot:
        if not self.api_key:
            return OnChainMetricSnapshot(
                chain="ETH",
                provider=self.provider_name,
                status="NOT_CONFIGURED",
                timestamp=datetime.now(timezone.utc),
                metrics={"reason": "DUNE_API_KEY environment variable not set"}
            )
        return OnChainMetricSnapshot(
            chain="ETH",
            provider=self.provider_name,
            status="UNAVAILABLE",
            timestamp=datetime.now(timezone.utc),
            metrics={"reason": "Provider connection pending verification"}
        )
