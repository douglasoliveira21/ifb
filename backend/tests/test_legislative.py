"""Testes para integrações legislativas (Câmara e Senado)."""

import pytest

from app.integrations.camara.constants import CAMARA_API_BASE, VOTE_MAP, EXPENSE_CATEGORIES
from app.integrations.senado.constants import SENADO_API_BASE, VOTE_MAP as SENADO_VOTE_MAP


def test_camara_api_base_url():
    """URL base da Câmara deve estar correta."""
    assert "dadosabertos.camara.leg.br" in CAMARA_API_BASE
    assert CAMARA_API_BASE.startswith("https://")


def test_senado_api_base_url():
    """URL base do Senado deve estar correta."""
    assert "legis.senado.leg.br" in SENADO_API_BASE
    assert SENADO_API_BASE.startswith("https://")


def test_camara_vote_normalization():
    """Votos da Câmara devem mapear para valores normalizados."""
    assert VOTE_MAP["Sim"] == "yes"
    assert VOTE_MAP["Não"] == "no"
    assert VOTE_MAP["Abstenção"] == "abstention"
    assert VOTE_MAP["Obstrução"] == "obstruction"


def test_senado_vote_normalization():
    """Votos do Senado devem mapear para valores normalizados."""
    assert SENADO_VOTE_MAP["Sim"] == "yes"
    assert SENADO_VOTE_MAP["Não"] == "no"
    assert SENADO_VOTE_MAP["Abstenção"] == "abstention"


def test_expense_categories_populated():
    """Categorias de despesas CEAP devem estar preenchidas."""
    assert len(EXPENSE_CATEGORIES) > 10
    assert "COMBUSTÍVEIS E LUBRIFICANTES" in EXPENSE_CATEGORIES
    assert "PASSAGENS AÉREAS" in EXPENSE_CATEGORIES


def test_vote_map_covers_common_values():
    """Mapa de votos deve cobrir valores comuns."""
    common = ["Sim", "Não", "Abstenção"]
    for v in common:
        assert v in VOTE_MAP, f"Missing: {v}"
        assert v in SENADO_VOTE_MAP, f"Missing senado: {v}"
