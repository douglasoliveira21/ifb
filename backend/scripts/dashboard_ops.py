"""
Dashboard operacional — mostra estado das sincronizações.
Execute: python scripts/dashboard_ops.py
"""

import asyncio
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician
from app.models.legislative import (
    LegislativeProposition, LegislatorVote, LegislativeCommittee,
    CommitteeMembership, ParliamentaryExpense, LegislativeSpeech,
    PoliticianLegislativeProfile,
)
from app.models.news import NewsArticle, NewsClassification, NewsMention
from app.models.election import Candidacy, CandidateAsset, CampaignRevenue, CampaignExpense

settings = get_settings()


async def main():
    engine = create_async_engine(settings.database_url, pool_size=3)
    factory = async_sessionmaker(engine, class_=AsyncSession)

    print(f"\n{'='*60}")
    print(f"  DASHBOARD OPERACIONAL — IFB")
    print(f"  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    async with factory() as db:
        # Politicians
        pols = (await db.execute(select(func.count(Politician.id)).where(Politician.is_public == True))).scalar_one()
        print(f"  📊 POLÍTICOS: {pols}")

        # Legislative
        props = (await db.execute(select(func.count(LegislativeProposition.id)))).scalar_one()
        votes = (await db.execute(select(func.count(LegislatorVote.id)))).scalar_one()
        comms = (await db.execute(select(func.count(CommitteeMembership.id)))).scalar_one()
        expenses = (await db.execute(select(func.count(ParliamentaryExpense.id)))).scalar_one()
        profiles = (await db.execute(select(func.count(PoliticianLegislativeProfile.id)))).scalar_one()
        speeches = (await db.execute(select(func.count(LegislativeSpeech.id)))).scalar_one()

        print(f"\n  📋 LEGISLATIVO:")
        print(f"     Proposições/Matérias: {props}")
        print(f"     Votos individuais: {votes}")
        print(f"     Comissões (membros): {comms}")
        print(f"     Despesas CEAP: {expenses}")
        print(f"     Perfis vinculados: {profiles}")
        print(f"     Discursos: {speeches}")

        # Electoral
        cands = (await db.execute(select(func.count(Candidacy.id)))).scalar_one()
        assets = (await db.execute(select(func.count(CandidateAsset.id)))).scalar_one()
        revs = (await db.execute(select(func.count(CampaignRevenue.id)))).scalar_one()
        exps = (await db.execute(select(func.count(CampaignExpense.id)))).scalar_one()

        print(f"\n  🗳️ ELEITORAL (TSE):")
        print(f"     Candidaturas: {cands}")
        print(f"     Bens declarados: {assets}")
        print(f"     Receitas campanha: {revs}")
        print(f"     Despesas campanha: {exps}")

        # News
        articles = (await db.execute(select(func.count(NewsArticle.id)))).scalar_one()
        classified = (await db.execute(select(func.count(NewsClassification.id)))).scalar_one()
        approved = (await db.execute(select(func.count(NewsClassification.id)).where(NewsClassification.review_status == "approved"))).scalar_one()
        pending = (await db.execute(select(func.count(NewsClassification.id)).where(NewsClassification.review_status == "pending"))).scalar_one()
        mentions = (await db.execute(select(func.count(NewsMention.id)))).scalar_one()

        print(f"\n  📰 NOTÍCIAS:")
        print(f"     Artigos coletados: {articles}")
        print(f"     Menções: {mentions}")
        print(f"     Classificados: {classified}")
        print(f"     Aprovados: {approved}")
        print(f"     Pendentes revisão: {pending}")

        # Expense totals
        total_ceap = (await db.execute(select(func.sum(ParliamentaryExpense.net_amount)))).scalar_one() or 0

        print(f"\n  💰 FINANCEIRO:")
        print(f"     Total CEAP importado: R$ {total_ceap:,.2f}")

    await engine.dispose()

    print(f"\n  ⏰ SCHEDULER (Celery Beat):")
    print(f"     Notícias: a cada 2h")
    print(f"     Proposições Câmara: diário 3h")
    print(f"     Despesas Câmara: diário 4h")
    print(f"     Senado: diário 5h")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
