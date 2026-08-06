"""Serviço de importação TSE — orquestra parsers, mappers e persistência."""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.tse.mappers import candidate_to_dict, hash_cpf
from app.integrations.tse.parsers.candidates import parse_candidates_csv
from app.integrations.tse.schemas import TseCandidateRow
from app.models.election import Candidacy, Election, ExternalDataset
from app.models.politician import Politician, PoliticalParty, PoliticalPosition

logger = logging.getLogger(__name__)


class TseImportService:
    """Orquestra importação de dados do TSE."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_election(self, year: int, election_type: str) -> Election:
        """Obtém ou cria registro de eleição."""
        scope = "general" if year % 4 == 2 else "municipal"
        name = f"Eleições {scope.title()} {year}"

        result = await self.db.execute(
            select(Election).where(
                and_(Election.year == year, Election.election_type == scope)
            )
        )
        election = result.scalar_one_or_none()
        if election:
            return election

        election = Election(
            year=year,
            name=name,
            election_type=scope,
            scope=scope,
            status="concluded" if year < 2026 else "upcoming",
            source_id="tse",
        )
        self.db.add(election)
        await self.db.flush()
        return election


    async def resolve_party(self, acronym: str | None) -> uuid.UUID | None:
        """Resolve sigla de partido para ID."""
        if not acronym:
            return None
        result = await self.db.execute(
            select(PoliticalParty.id).where(PoliticalParty.acronym == acronym.upper())
        )
        row = result.scalar_one_or_none()
        return row

    async def resolve_position(self, position_name: str | None) -> uuid.UUID | None:
        """Resolve nome de cargo para ID."""
        if not position_name:
            return None
        normalized = position_name.strip().title()
        result = await self.db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == normalized)
        )
        return result.scalar_one_or_none()

    async def import_candidates_from_file(
        self,
        file_path: str,
        year: int,
        dataset_id: uuid.UUID | None = None,
    ) -> dict:
        """
        Importa candidatos de um arquivo CSV do TSE.
        Idempotente: usa sequence_number + election para deduplicação.
        Retorna estatísticas.
        """
        election = await self.get_or_create_election(year, "general")

        stats = {
            "total": 0, "created": 0, "updated": 0,
            "skipped": 0, "errors": 0, "duplicates": 0,
        }

        for row in parse_candidates_csv(file_path, year):
            stats["total"] += 1
            try:
                await self._import_single_candidate(row, election)
                stats["created"] += 1
            except DuplicateCandidate:
                stats["duplicates"] += 1
            except Exception as e:
                stats["errors"] += 1
                logger.warning("Import error row %d: %s", stats["total"], str(e))

            # Flush every 100 rows to avoid memory issues
            if stats["total"] % 100 == 0:
                await self.db.flush()

        await self.db.flush()
        logger.info("Import completed: %s", stats)
        return stats

    async def _import_single_candidate(
        self, row: TseCandidateRow, election: Election
    ) -> Candidacy:
        """Importa ou atualiza um único candidato."""
        # Check for existing by sequence_number
        if row.sequence_number:
            existing = await self.db.execute(
                select(Candidacy).where(
                    and_(
                        Candidacy.tse_candidate_id == row.sequence_number,
                        Candidacy.election_id == election.id,
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise DuplicateCandidate(row.sequence_number)

        # Resolve foreign keys
        party_id = await self.resolve_party(row.party_acronym)
        position_id = await self.resolve_position(row.position_name)
        cpf_h = hash_cpf(row.cpf) if row.cpf else None

        # Try to reconcile with existing politician
        politician_id = await self._reconcile(row, cpf_h)

        data = candidate_to_dict(row)

        candidacy = Candidacy(
            politician_id=politician_id,
            election_id=election.id,
            tse_candidate_id=row.sequence_number,
            sequence_number=row.sequence_number,
            ballot_number=row.ballot_number,
            ballot_name=row.ballot_name,
            full_name=row.full_name,
            cpf_hash=cpf_h,
            party_id=party_id,
            position_id=position_id,
            state_code=row.state_code,
            city_name=row.city_name,
            status=data["status"],
            status_detail=data["status_detail"],
            reelection=row.reelection,
            occupation=row.occupation,
            education=row.education,
            gender=row.gender,
            race_color=row.race_color,
            marital_status=row.marital_status,
            nationality=row.nationality,
            birth_date=data["birth_date"],
            birth_place=data["birth_place"],
            coalition_name=row.coalition_name,
            coalition_parties=row.coalition_parties,
            reconciliation_status="matched" if politician_id else "pending",
            source_id="tse",
            source_url=f"dadosabertos.tse.jus.br/candidatos-{row.election_year}",
            collected_at=datetime.now(UTC),
        )
        self.db.add(candidacy)
        return candidacy

    async def _reconcile(self, row: TseCandidateRow, cpf_hash: str | None) -> uuid.UUID | None:
        """
        Tenta conciliar candidato com político existente.
        Prioridade: CPF hash > nome + nascimento + UF.
        """
        if cpf_hash:
            result = await self.db.execute(
                select(Politician.id).where(Politician.cpf_hash == cpf_hash)
            )
            politician_id = result.scalar_one_or_none()
            if politician_id:
                return politician_id

        # Try name + state (weaker match - mark as pending review)
        # For now, return None and mark for manual review
        return None


class DuplicateCandidate(Exception):
    """Candidato já importado para esta eleição."""
    pass
