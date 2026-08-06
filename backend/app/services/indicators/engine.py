"""Motor de cálculo de indicadores — orquestra calculators e gera resultados."""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import (
    IndicatorDefinition,
    IndicatorMethodology,
    IndicatorResult,
)

logger = logging.getLogger(__name__)


class CalculationResult:
    """Resultado de um cálculo de indicador."""

    def __init__(
        self,
        value: float | None,
        status: str,
        inputs: dict,
        explanation: str,
        limitations: list[str] | None = None,
        sources: list[dict] | None = None,
    ):
        self.value = value
        self.status = status
        self.inputs = inputs
        self.explanation = explanation
        self.limitations = limitations or []
        self.sources = sources or []


class IndicatorCalculator(ABC):
    """Interface base para calculadores de indicadores."""

    indicator_code: str = ""
    methodology_version: str = "1.0"

    @abstractmethod
    async def collect_inputs(
        self, db: AsyncSession, politician_id: uuid.UUID, period_start, period_end
    ) -> dict:
        """Coleta dados de entrada para o cálculo."""
        ...

    @abstractmethod
    def validate_inputs(self, inputs: dict) -> bool:
        """Valida se há dados suficientes."""
        ...

    @abstractmethod
    def calculate(self, inputs: dict) -> CalculationResult:
        """Executa o cálculo. Retorna resultado com explicação."""
        ...


class IndicatorEngine:
    """Orquestra cálculo de indicadores com persistência."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._calculators: dict[str, IndicatorCalculator] = {}

    def register(self, calculator: IndicatorCalculator) -> None:
        """Registra um calculator."""
        self._calculators[calculator.indicator_code] = calculator

    async def calculate_for_politician(
        self,
        indicator_code: str,
        politician_id: uuid.UUID,
        period_start=None,
        period_end=None,
    ) -> IndicatorResult | None:
        """Calcula indicador para um político e persiste resultado."""
        calculator = self._calculators.get(indicator_code)
        if not calculator:
            logger.error("No calculator for indicator: %s", indicator_code)
            return None

        # Get indicator definition
        ind_result = await self.db.execute(
            select(IndicatorDefinition).where(IndicatorDefinition.code == indicator_code)
        )
        indicator = ind_result.scalar_one_or_none()
        if not indicator:
            logger.error("Indicator not found: %s", indicator_code)
            return None

        # Get methodology
        meth_result = await self.db.execute(
            select(IndicatorMethodology).where(
                IndicatorMethodology.indicator_id == indicator.id,
                IndicatorMethodology.status == "published",
            ).order_by(IndicatorMethodology.effective_from.desc()).limit(1)
        )
        methodology = meth_result.scalar_one_or_none()

        # Collect inputs
        try:
            inputs = await calculator.collect_inputs(
                self.db, politician_id, period_start, period_end
            )
        except Exception as e:
            logger.error("Input collection failed for %s: %s", indicator_code, e)
            return await self._save_result(
                indicator, methodology, politician_id,
                CalculationResult(None, "failed", {}, f"Erro na coleta: {e}"),
                period_start, period_end,
            )

        # Validate
        if not calculator.validate_inputs(inputs):
            return await self._save_result(
                indicator, methodology, politician_id,
                CalculationResult(None, "insufficient_data", inputs, "Dados insuficientes."),
                period_start, period_end,
            )

        # Calculate
        try:
            result = calculator.calculate(inputs)
        except Exception as e:
            logger.error("Calculation failed for %s: %s", indicator_code, e)
            result = CalculationResult(None, "failed", inputs, f"Erro no cálculo: {e}")

        return await self._save_result(
            indicator, methodology, politician_id, result, period_start, period_end
        )

    async def _save_result(
        self, indicator, methodology, politician_id, result, period_start, period_end
    ) -> IndicatorResult:
        """Persiste resultado do cálculo."""
        record = IndicatorResult(
            indicator_id=indicator.id,
            politician_id=politician_id,
            methodology_id=methodology.id if methodology else None,
            value=result.value,
            status=result.status,
            period_start=period_start,
            period_end=period_end,
            explanation=result.explanation,
            limitations_json=result.limitations,
            inputs_json=result.inputs,
            sources_json=result.sources,
            calculated_at=datetime.now(UTC),
        )
        self.db.add(record)
        await self.db.flush()
        return record

    async def calculate_all_for_politician(
        self, politician_id: uuid.UUID, period_start=None, period_end=None
    ) -> dict[str, IndicatorResult | None]:
        """Calcula todos os indicadores ativos para um político."""
        results = {}
        for code, calculator in self._calculators.items():
            results[code] = await self.calculate_for_politician(
                code, politician_id, period_start, period_end
            )
        return results
