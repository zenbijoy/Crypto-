"""
CryptoScope AI - News Deduplication & Rolling Sentiment Feature Engine
Clustering of duplicate news alerts and rolling sentiment velocity/acceleration.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np
import re
from providers.news.nlp_classifier import ClassifiedNewsItem


class NewsSentimentFeatures(BaseModel):
    asset: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    current_sentiment_score: float  # -1.0 to +1.0
    sentiment_velocity: float = 0.0
    sentiment_acceleration: float = 0.0
    
    news_volume_1h: int
    news_volume_burst_score: float  # 0.0 to 100.0
    
    high_urgency_alerts_count: int
    recent_headlines: List[str]


class NewsDeduplicator:
    @staticmethod
    def deduplicate(items: List[ClassifiedNewsItem], threshold: float = 0.6) -> List[ClassifiedNewsItem]:
        unique_items: List[ClassifiedNewsItem] = []
        seen_word_sets: List[set] = []

        for item in items:
            words = set(re.findall(r"\b\w{4,}\b", item.title.lower()))
            if not words:
                unique_items.append(item)
                continue

            is_dup = False
            for seen in seen_word_sets:
                intersection = words.intersection(seen)
                union = words.union(seen)
                jaccard = len(intersection) / len(union) if union else 0.0
                if jaccard >= threshold:
                    is_dup = True
                    break

            if not is_dup:
                seen_word_sets.append(words)
                unique_items.append(item)

        return unique_items


class SentimentFeatureEngine:
    def __init__(self, baseline_hourly_volume: int = 8):
        self.baseline_vol = baseline_hourly_volume
        self._sent_history: Dict[str, List[float]] = {}

    def compute(self, asset: str, items: List[ClassifiedNewsItem]) -> NewsSentimentFeatures:
        relevant = [it for it in items if it.asset_relevance.get(asset, 0.0) > 0.3 or it.primary_asset == asset]
        now = datetime.now(timezone.utc)

        if not relevant:
            curr_sent = 0.0
            urg_count = 0
            titles = []
        else:
            weights = [it.asset_relevance.get(asset, 0.5) for it in relevant]
            curr_sent = float(np.average([it.net_sentiment for it in relevant], weights=weights))
            urg_count = sum(1 for it in relevant if it.urgency_level == "HIGH")
            titles = [it.title for it in relevant[:5]]

        if asset not in self._sent_history:
            self._sent_history[asset] = []
        self._sent_history[asset].append(curr_sent)
        if len(self._sent_history[asset]) > 20:
            self._sent_history[asset].pop(0)

        hist = self._sent_history[asset]
        vel = 0.0
        acc = 0.0
        if len(hist) >= 2:
            vel = hist[-1] - hist[-2]
        if len(hist) >= 3:
            prev_vel = hist[-2] - hist[-3]
            acc = vel - prev_vel

        # Burst score
        vol = len(relevant)
        burst = min((vol / self.baseline_vol) * 50.0, 100.0)

        return NewsSentimentFeatures(
            asset=asset,
            timestamp=now,
            current_sentiment_score=round(curr_sent, 3),
            sentiment_velocity=round(vel, 4),
            sentiment_acceleration=round(acc, 4),
            news_volume_1h=vol,
            news_volume_burst_score=round(burst, 1),
            high_urgency_alerts_count=urg_count,
            recent_headlines=titles
        )
