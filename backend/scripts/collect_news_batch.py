"""
Coleta de notícias em lotes para expansão nacional.
Execute: python scripts/collect_news_batch.py [batch_size] [offset] [--classify]

Exemplos:
  python scripts/collect_news_batch.py 50 0
  python scripts/collect_news_batch.py 50 50 --classify
  python scripts/collect_news_batch.py 200 0
"""

import asyncio
import hashlib
import os
import sys
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician
from app.models.news import NewsArticle, NewsMention

settings = get_settings()

BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 50
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 else 0
CLASSIFY = "--classify" in sys.argv


async def fetch_google_news(client: httpx.AsyncClient, query: str) -> list[dict]:
    """Fetch from Google News RSS."""
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.text)
        articles = []
        for item in root.findall(".//item")[:10]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            parsed_date = None
            if pub_date:
                try:
                    parsed_date = parsedate_to_datetime(pub_date)
                except Exception:
                    pass
            articles.append({"title": title, "url": link, "published_at": parsed_date})
        return articles
    except Exception:
        return []


async def main():
    print(f"\n{'='*60}")
    print(f"  COLETA DE NOTÍCIAS EM LOTE (batch={BATCH_SIZE}, offset={OFFSET})")
    print(f"{'='*60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=2)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as db:
        pols_r = await db.execute(
            select(Politician).where(Politician.is_public == True, Politician.deleted_at == None)
            .order_by(Politician.full_name).offset(OFFSET).limit(BATCH_SIZE)
        )
        politicians = pols_r.scalars().all()

        print(f"  Políticos no lote: {len(politicians)}")
        stats = {"total_collected": 0, "total_saved": 0, "total_duplicates": 0, "errors": 0}

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for i, pol in enumerate(politicians):
                query = f'"{pol.full_name}"'
                articles = await fetch_google_news(client, query)

                saved = 0
                for art in articles:
                    url = art.get("url", "")
                    if not url:
                        continue
                    content_hash = hashlib.sha256(url.encode()).hexdigest()

                    existing = await db.execute(
                        select(NewsArticle.id).where(NewsArticle.content_hash == content_hash)
                    )
                    if existing.scalar_one_or_none():
                        stats["total_duplicates"] += 1
                        continue

                    pub_at = art.get("published_at")
                    article = NewsArticle(
                        provider="google_news",
                        external_id=hashlib.md5(url.encode()).hexdigest(),
                        title=(art.get("title") or "")[:1000],
                        canonical_url=url, original_url=url,
                        language="pt", published_at=pub_at,
                        collected_at=datetime.now(UTC),
                        content_hash=content_hash, status="collected",
                    )
                    db.add(article)
                    await db.flush()
                    db.add(NewsMention(
                        article_id=article.id, politician_id=pol.id,
                        is_primary_subject=True, identity_confidence=0.7,
                        resolution_status="pending",
                    ))
                    saved += 1
                    stats["total_saved"] += 1

                stats["total_collected"] += len(articles)

                if (i + 1) % 10 == 0:
                    await db.flush()
                    print(f"  ... {i+1}/{len(politicians)} | saved={stats['total_saved']} dupes={stats['total_duplicates']}")

                await asyncio.sleep(2)  # Rate limit Google News

        await db.commit()

    await engine.dispose()

    print(f"\n{'='*60}")
    print(f"  RESULTADO")
    print(f"{'='*60}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\n  Próximo: python scripts/collect_news_batch.py {BATCH_SIZE} {OFFSET + BATCH_SIZE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
