"""Calculadores específicos por indicador IFB."""

import uuid
from datetime import date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legislative import (
    LegislativeProposition,
    LegislativeVoteEvent,
    LegislatorVote,
    ParliamentaryExpense,
    PoliticianLegislativeProfile,
    PropositionAuthor,
    SessionAttendance,
)
from app.models.promise import CampaignPromise
from app.services.indicators.engine import CalculationResult, IndicatorCalculator


class AttendanceCalculator(IndicatorCalculator):
    """Calcula índice de presença em sessões legislativas."""

    indicator_code = "attendance"
    methodology_version = "1.0"

    async def collect_inputs(
        self, db: AsyncSession, politician_id: uuid.UUID, period_start, period_end
    ) -> dict:
        # Get legislator IDs
        profiles = await db.execute(
            select(PoliticianLegislativeProfile.legislator_id).where(
                PoliticianLegislativeProfile.politician_id == politician_id,
                PoliticianLegislativeProfile.status.in_(["confirmed", "probable"]),
            )
        )
        leg_ids = list(profiles.scalars().all())
        if not leg_ids:
            return {"legislator_ids": [], "eligible": 0, "present": 0}

        query = select(SessionAttendance).where(
            SessionAttendance.legislator_id.in_(leg_ids)
        )
        if period_start:
            query = query.where(SessionAttendance.session_date >= period_start)
        if period_end:
            query = query.where(SessionAttendance.session_date <= period_end)

        result = await db.execute(query)
        records = result.scalars().all()

        present = sum(1 for r in records if r.attendance_status == "present")
        absent_just = sum(1 for r in records if r.attendance_status in ("justified_absence", "official_mission", "licensed"))
        absent = sum(1 for r in records if r.attendance_status == "absent")
        total = len(records)
        eligible = total - absent_just  # Don't count justified absences

        return {
            "legislator_ids": [str(i) for i in leg_ids],
            "total_sessions": total,
            "eligible_sessions": eligible,
            "present": present,
            "absent_justified": absent_just,
            "absent": absent,
        }

    def validate_inputs(self, inputs: dict) -> bool:
        return inputs.get("eligible_sessions", 0) >= 10

    def calculate(self, inputs: dict) -> CalculationResult:
        eligible = inputs["eligible_sessions"]
        present = inputs["present"]

        if eligible == 0:
            return CalculationResult(None, "insufficient_data", inputs, "Nenhuma sessão elegível.")

        value = round((present / eligible) * 100, 1)

        return CalculationResult(
            value=value,
            status="calculated",
            inputs=inputs,
            explanation=(
                f"Presença em {present} de {eligible} sessões elegíveis "
                f"(excluindo licenças e missões oficiais)."
            ),
            sources=[{"name": "Câmara dos Deputados / Senado Federal", "type": "api"}],
        )


class PromiseFulfillmentCalculator(IndicatorCalculator):
    """Calcula índice de cumprimento de promessas."""

    indicator_code = "promise_fulfillment"
    methodology_version = "1.0"

    async def collect_inputs(
        self, db: AsyncSession, politician_id: uuid.UUID, period_start, period_end
    ) -> dict:
        query = select(CampaignPromise).where(
            CampaignPromise.politician_id == politician_id,
            CampaignPromise.editorial_status == "published",
        )
        result = await db.execute(query)
        promises = result.scalars().all()

        counts = {"total": 0, "evaluable": 0, "fulfilled": 0, "partially": 0,
                  "in_progress": 0, "not_fulfilled": 0, "not_verifiable": 0,
                  "outside_competence": 0}

        for p in promises:
            counts["total"] += 1
            if p.status in ("not_verifiable", "outside_competence"):
                counts[p.status.replace("outside_", "outside_")] = counts.get(p.status, 0) + 1
                continue
            counts["evaluable"] += 1
            if p.status == "fulfilled":
                counts["fulfilled"] += 1
            elif p.status == "partially_fulfilled":
                counts["partially"] += 1
            elif p.status == "in_progress":
                counts["in_progress"] += 1
            elif p.status == "not_fulfilled":
                counts["not_fulfilled"] += 1

        return counts

    def validate_inputs(self, inputs: dict) -> bool:
        return inputs.get("evaluable", 0) >= 5

    def calculate(self, inputs: dict) -> CalculationResult:
        evaluable = inputs["evaluable"]
        if evaluable == 0:
            return CalculationResult(None, "insufficient_data", inputs, "Promessas insuficientes.")

        fulfilled = inputs["fulfilled"]
        partially = inputs["partially"]

        # Weighted: fulfilled=100%, partially=50%
        weighted = (fulfilled * 100 + partially * 50) / evaluable
        value = round(weighted, 1)

        return CalculationResult(
            value=value,
            status="calculated",
            inputs=inputs,
            explanation=(
                f"Cumprimento ponderado: {fulfilled} cumpridas + {partially} parciais "
                f"de {evaluable} avaliáveis (fórmula: cumpridas×100% + parciais×50%)."
            ),
            limitations=[
                "Promessas não verificáveis e fora da competência não são contabilizadas",
                "Promessas em andamento não afetam o percentual até avaliação",
            ],
            sources=[{"name": "IFB — Análise de promessas", "type": "internal"}],
        )


class VotingParticipationCalculator(IndicatorCalculator):
    """Calcula participação em votações nominais."""

    indicator_code = "voting_participation"
    methodology_version = "1.0"

    async def collect_inputs(
        self, db: AsyncSession, politician_id: uuid.UUID, period_start, period_end
    ) -> dict:
        profiles = await db.execute(
            select(PoliticianLegislativeProfile.legislator_id).where(
                PoliticianLegislativeProfile.politician_id == politician_id,
                PoliticianLegislativeProfile.status.in_(["confirmed", "probable"]),
            )
        )
        leg_ids = list(profiles.scalars().all())
        if not leg_ids:
            return {"total_votes": 0, "participated": 0}

        query = select(LegislatorVote).where(LegislatorVote.legislator_id.in_(leg_ids))
        result = await db.execute(query)
        votes = result.scalars().all()

        total = len(votes)
        participated = sum(1 for v in votes if v.normalized_vote in ("yes", "no", "abstention"))

        return {"total_votes": total, "participated": participated, "absent": total - participated}

    def validate_inputs(self, inputs: dict) -> bool:
        return inputs.get("total_votes", 0) >= 10

    def calculate(self, inputs: dict) -> CalculationResult:
        total = inputs["total_votes"]
        participated = inputs["participated"]
        if total == 0:
            return CalculationResult(None, "insufficient_data", inputs, "Sem votações registradas.")

        value = round((participated / total) * 100, 1)
        return CalculationResult(
            value=value,
            status="calculated",
            inputs=inputs,
            explanation=f"Participou em {participated} de {total} votações nominais.",
            sources=[{"name": "Câmara dos Deputados / Senado Federal", "type": "api"}],
        )


# Registry of all calculators
ALL_CALCULATORS: list[type[IndicatorCalculator]] = [
    AttendanceCalculator,
    PromiseFulfillmentCalculator,
    VotingParticipationCalculator,
]
