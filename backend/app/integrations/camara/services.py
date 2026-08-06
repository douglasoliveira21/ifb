"""Serviços de sincronização da Câmara dos Deputados."""

import hashlib
import logging
from datetime import UTC, datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.camara.client import CamaraClient
from app.integrations.camara.constants import VOTE_MAP
from app.models.legislative import (
    Legislator,
    LegislativeCommittee,
    LegislativeHouse,
    LegislativeProposition,
    LegislativeVoteEvent,
    LegislatorVote,
    ParliamentaryExpense,
    PropositionAuthor,
    SessionAttendance,
)
from app.services.legislative_sync import LegislativeSyncService

logger = logging.getLogger(__name__)


class CamaraExpensesSync(LegislativeSyncService):
    """Sincroniza despesas parlamentares (CEAP) da Câmara."""

    provider = "camara"
    resource = "expenses"

    def __init__(self, db: AsyncSession, client: CamaraClient | None = None):
        super().__init__(db)
        self.client = client or CamaraClient()

    async def fetch(self, deputy_id: int = None, year: int = None, **params) -> list[dict]:
        """Busca despesas de um deputado."""
        if not deputy_id:
            return []
        return await self.client.get_deputy_expenses(deputy_id, year=year)

    async def persist(self, items: list[dict]) -> dict:
        """Persiste despesas no banco."""
        stats = {"total": len(items), "created": 0, "updated": 0, "duplicates": 0, "errors": 0}

        # Get house
        house_result = await self.db.execute(
            select(LegislativeHouse).where(LegislativeHouse.acronym == "CD")
        )
        house = house_result.scalar_one_or_none()
        if not house:
            return stats

        for item in items:
            try:
                await self._persist_expense(item, house.id)
                stats["created"] += 1
            except DuplicateExpense:
                stats["duplicates"] += 1
            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] <= 5:
                    logger.warning("Expense persist error: %s", e)

        stats["processed"] = stats["total"]
        await self.db.flush()
        return stats

    async def _persist_expense(self, item: dict, house_id) -> None:
        """Persiste uma despesa individual."""
        # Build unique key
        doc_num = item.get("numDocumento", "")
        year = item.get("ano", 0)
        month = item.get("mes", 0)
        dep_id = item.get("idDeputado") or item.get("codDocumento")
        ext_id = f"{dep_id}-{year}-{month}-{doc_num}" if doc_num else None

        if ext_id:
            existing = await self.db.execute(
                select(ParliamentaryExpense).where(
                    ParliamentaryExpense.external_id == ext_id,
                    ParliamentaryExpense.house_id == house_id,
                )
            )
            if existing.scalar_one_or_none():
                raise DuplicateExpense()

        # Resolve legislator
        legislator_ext_id = str(item.get("idDeputado", ""))
        leg_result = await self.db.execute(
            select(Legislator.id).where(
                Legislator.external_id == legislator_ext_id,
                Legislator.house_id == house_id,
            )
        )
        legislator_id = leg_result.scalar_one_or_none()
        if not legislator_id:
            raise ValueError(f"Legislator not found: {legislator_ext_id}")

        # Hash supplier document
        supplier_doc = item.get("cnpjCpfFornecedor", "")
        supplier_hash = None
        if supplier_doc:
            cleaned = supplier_doc.replace(".", "").replace("-", "").replace("/", "")
            supplier_hash = hashlib.sha256(cleaned.encode()).hexdigest() if cleaned else None

        net_amount = float(item.get("valorLiquido", 0) or 0)
        gross_amount = float(item.get("valorDocumento", 0) or 0)
        gloss = float(item.get("valorGlosa", 0) or 0)

        expense = ParliamentaryExpense(
            house_id=house_id,
            legislator_id=legislator_id,
            external_id=ext_id,
            year=int(year),
            month=int(month),
            category=item.get("tipoDespesa", "Não categorizado"),
            supplier_name=item.get("nomeFornecedor"),
            supplier_document_hash=supplier_hash,
            document_number=str(doc_num) if doc_num else None,
            document_date=None,
            gross_amount=gross_amount,
            net_amount=net_amount,
            reimbursement_amount=net_amount,
            document_url=item.get("urlDocumento"),
            source_url=f"https://dadosabertos.camara.leg.br/api/v2/deputados/{legislator_ext_id}/despesas",
        )
        self.db.add(expense)


class CamaraPropositionsSync(LegislativeSyncService):
    """Sincroniza proposições da Câmara."""

    provider = "camara"
    resource = "propositions"

    def __init__(self, db: AsyncSession, client: CamaraClient | None = None):
        super().__init__(db)
        self.client = client or CamaraClient()

    async def fetch(self, year: int = None, **params) -> list[dict]:
        filters = {}
        if year:
            filters["ano"] = year
        filters["ordenarPor"] = "id"
        filters["ordem"] = "DESC"
        return await self.client.list_propositions(**filters)

    async def persist(self, items: list[dict]) -> dict:
        stats = {"total": len(items), "created": 0, "updated": 0, "duplicates": 0, "errors": 0}
        house_result = await self.db.execute(
            select(LegislativeHouse).where(LegislativeHouse.acronym == "CD")
        )
        house = house_result.scalar_one_or_none()
        if not house:
            return stats

        for item in items:
            ext_id = str(item.get("id", ""))
            existing = await self.db.execute(
                select(LegislativeProposition).where(
                    LegislativeProposition.external_id == ext_id,
                    LegislativeProposition.house_id == house.id,
                )
            )
            if existing.scalar_one_or_none():
                stats["duplicates"] += 1
                continue

            prop = LegislativeProposition(
                house_id=house.id,
                external_id=ext_id,
                type_acronym=item.get("siglaTipo", ""),
                number=item.get("numero"),
                year=item.get("ano"),
                title=item.get("ementa", "")[:1000],
                summary=item.get("ementaDetalhada"),
                status=item.get("statusProposicao", {}).get("descricaoSituacao") if isinstance(item.get("statusProposicao"), dict) else None,
                presentation_date=item.get("dataApresentacao"),
                source_url=item.get("urlInteiroTeor"),
                last_synced_at=datetime.now(UTC),
            )
            self.db.add(prop)
            stats["created"] += 1

        stats["processed"] = stats["total"]
        await self.db.flush()
        return stats


class CamaraVotesSync(LegislativeSyncService):
    """Sincroniza votações e votos individuais da Câmara."""

    provider = "camara"
    resource = "votes"

    def __init__(self, db: AsyncSession, client: CamaraClient | None = None):
        super().__init__(db)
        self.client = client or CamaraClient()

    async def fetch(self, **params) -> list[dict]:
        return await self.client.get_paginated("/votacoes", params)

    async def persist(self, items: list[dict]) -> dict:
        stats = {"total": len(items), "created": 0, "duplicates": 0, "errors": 0}
        house_result = await self.db.execute(
            select(LegislativeHouse).where(LegislativeHouse.acronym == "CD")
        )
        house = house_result.scalar_one_or_none()
        if not house:
            return stats

        for item in items:
            ext_id = str(item.get("id", ""))
            existing = await self.db.execute(
                select(LegislativeVoteEvent).where(
                    LegislativeVoteEvent.external_id == ext_id,
                    LegislativeVoteEvent.house_id == house.id,
                )
            )
            if existing.scalar_one_or_none():
                stats["duplicates"] += 1
                continue

            vote_event = LegislativeVoteEvent(
                house_id=house.id,
                external_id=ext_id,
                date=item.get("data"),
                description=item.get("descricao"),
                result=item.get("aprovacao"),
                is_nominal=True,
                source_url=item.get("uri"),
            )
            self.db.add(vote_event)
            stats["created"] += 1

        stats["processed"] = stats["total"]
        await self.db.flush()
        return stats


class DuplicateExpense(Exception):
    pass
