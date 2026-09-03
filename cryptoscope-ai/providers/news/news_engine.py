"""
CryptoScope AI - News Ingestion Engine
Fetches real-time crypto news from real verified RSS feeds (CoinTelegraph, etc.).
Extracts article metadata, publishing time, and content.
"""
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    article_id: str
    title: str
    link: str
    published_time: datetime
    source: str
    summary: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NewsEngine:
    def __init__(self, feed_urls: List[str] = None):
        self.feed_urls = feed_urls or [
            "https://cointelegraph.com/rss"
        ]

    async def fetch_latest_news(self, limit: int = 20) -> List[NewsArticle]:
        articles = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for url in self.feed_urls:
                try:
                    resp = await client.get(url, headers={"User-Agent": "CryptoScope/2.0 QuantResearch"})
                    if resp.status_code == 200:
                        root = ET.fromstring(resp.content)
                        channel = root.find("channel")
                        if channel is not None:
                            items = channel.findall("item")
                            for it in items[:limit]:
                                title = it.find("title").text if it.find("title") is not None else ""
                                link = it.find("link").text if it.find("link") is not None else ""
                                pub_str = it.find("pubDate").text if it.find("pubDate") is not None else ""
                                desc = it.find("description").text if it.find("description") is not None else ""

                                # Parse RFC 2822 date e.g. "Thu, 03 Sep 2026 06:10:27 +0000"
                                try:
                                    pub_dt = datetime.strptime(pub_str[:25].strip(), "%a, %d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
                                except Exception:
                                    pub_dt = datetime.now(timezone.utc)

                                aid = f"{hash(title + link)}"
                                articles.append(NewsArticle(
                                    article_id=aid,
                                    title=title,
                                    link=link,
                                    published_time=pub_dt,
                                    source="cointelegraph",
                                    summary=desc[:300] if desc else ""
                                ))
                except Exception:
                    pass
        return articles
