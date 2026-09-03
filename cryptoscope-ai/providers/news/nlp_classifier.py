"""
CryptoScope AI - News NLP Classifier
Categorizes crypto news headlines with asset relevance, multi-class sentiment probabilities,
uncertainty, novelty, and market urgency.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re
import numpy as np


class ClassifiedNewsItem(BaseModel):
    article_id: str
    title: str
    source: str
    published_time: str
    
    asset_relevance: Dict[str, float]  # "BTC": 0.9, "ETH": 0.1, ...
    primary_asset: str
    
    bullish_probability: float
    bearish_probability: float
    neutral_probability: float
    net_sentiment: float  # bullish - bearish (-1.0 to +1.0)
    
    uncertainty_score: float  # 0.0 to 1.0
    urgency_level: str  # "HIGH", "MEDIUM", "LOW"


class NewsNLPClassifier:
    def __init__(self):
        # Lexicons
        self.bull_words = {"surge", "rally", "gain", "high", "breakout", "all-time", "bull", "inflow", "approval", "adoption", "soar", "record", "jump", "climb", "expansion"}
        self.bear_words = {"drop", "fall", "crash", "plunge", "down", "bear", "outflow", "lawsuit", "hack", "exploit", "sec", "ban", "dump", "decline", "liquidation", "theft"}
        self.uncertainty_words = {"might", "could", "rumor", "speculation", "alleged", "potential", "uncertain", "unclear", "doubt", "claims"}
        self.urgent_words = {"emergency", "hack", "exploit", "sec", "approved", "banned", "fed", "cpi", "rate", "arrest", "insolvent"}

    def classify(self, article_id: str, title: str, source: str, published_time: str) -> ClassifiedNewsItem:
        text = title.lower()
        words = set(re.findall(r"\b\w+\b", text))

        # Asset relevance
        rel = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0}
        if "btc" in words or "bitcoin" in words or "satoshi" in words:
            rel["BTC"] = 1.0
        if "eth" in words or "ethereum" in words or "vitalik" in words:
            rel["ETH"] = 1.0
        if "sol" in words or "solana" in words:
            rel["SOL"] = 1.0

        if sum(rel.values()) == 0:
            rel["BTC"] = 0.5  # default market proxy
            primary = "BTC"
        else:
            primary = max(rel, key=rel.get)

        # Word counts
        b_count = sum(1 for w in words if w in self.bull_words)
        br_count = sum(1 for w in words if w in self.bear_words)
        u_count = sum(1 for w in words if w in self.uncertainty_words)
        urg_count = sum(1 for w in words if w in self.urgent_words)

        # Softmax logits
        logits = np.array([b_count * 1.2, br_count * 1.2, 0.8])  # baseline neutral 0.8
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        bull_prob = float(probs[0])
        bear_prob = float(probs[1])
        neu_prob = float(probs[2])
        net_sent = bull_prob - bear_prob

        # Uncertainty score
        uncert = min(u_count * 0.35 + (0.5 if abs(net_sent) < 0.1 else 0.1), 1.0)

        # Urgency
        if urg_count >= 1 or "sec" in words or "hack" in words:
            urgency = "HIGH"
        elif b_count >= 2 or br_count >= 2:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        return ClassifiedNewsItem(
            article_id=article_id,
            title=title,
            source=source,
            published_time=published_time,
            asset_relevance=rel,
            primary_asset=primary,
            bullish_probability=round(bull_prob, 3),
            bearish_probability=round(bear_prob, 3),
            neutral_probability=round(neu_prob, 3),
            net_sentiment=round(net_sent, 3),
            uncertainty_score=round(uncert, 2),
            urgency_level=urgency
        )
