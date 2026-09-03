"""
CryptoScope AI - Enrichment Provider Adapters
Modular adapters for CoinGecko, DefiLlama, FRED, OnChain, and Sentiment.
"""
from providers.enrichment.base import BaseEnrichmentProvider
from providers.enrichment.coingecko import CoinGeckoProvider
from providers.enrichment.defillama import DefiLlamaProvider
from providers.enrichment.fred import FREDProvider
from providers.enrichment.onchain import OnChainProvider
from providers.enrichment.sentiment import SentimentProvider

__all__ = [
    "BaseEnrichmentProvider",
    "CoinGeckoProvider",
    "DefiLlamaProvider",
    "FREDProvider",
    "OnChainProvider",
    "SentimentProvider"
]
