"""Testes para integração TSE."""

import pytest

from app.integrations.tse.constants import CANDIDACY_STATUS_MAP, RESULT_STATUS_MAP, UF_CODES
from app.integrations.tse.mappers import (
    hash_cpf,
    hash_document,
    map_candidacy_status,
    map_result_status,
    parse_tse_date,
    parse_tse_value,
)


def test_hash_cpf():
    """CPF deve gerar hash SHA-256 determinístico."""
    h1 = hash_cpf("12345678901")
    h2 = hash_cpf("12345678901")
    h3 = hash_cpf("98765432100")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64  # SHA-256 hex


def test_hash_cpf_with_formatting():
    """CPF formatado deve gerar mesmo hash que limpo."""
    h1 = hash_cpf("123.456.789-01")
    h2 = hash_cpf("12345678901")
    assert h1 == h2


def test_hash_document():
    """Documentos devem gerar hash determinístico."""
    h1 = hash_document("12.345.678/0001-90")
    h2 = hash_document("12345678000190")
    assert h1 == h2


def test_map_candidacy_status():
    """Status de candidatura deve mapear corretamente."""
    assert map_candidacy_status("DEFERIDO") == "deferido"
    assert map_candidacy_status("INDEFERIDO") == "indeferido"
    assert map_candidacy_status("APTO") == "deferido"
    assert map_candidacy_status(None) == "unknown"
    assert map_candidacy_status("DESCONHECIDO") == "unknown"


def test_map_result_status():
    """Status de resultado deve mapear corretamente."""
    status, elected = map_result_status("ELEITO")
    assert status == "eleito"
    assert elected is True

    status, elected = map_result_status("NÃO ELEITO")
    assert status == "nao_eleito"
    assert elected is False

    status, elected = map_result_status("SUPLENTE")
    assert status == "suplente"
    assert elected is False


def test_parse_tse_date_formats():
    """Datas TSE devem ser parseadas em múltiplos formatos."""
    d1 = parse_tse_date("01/06/1980")
    assert d1 is not None
    assert d1.year == 1980
    assert d1.month == 6
    assert d1.day == 1

    d2 = parse_tse_date("1980-06-01")
    assert d2 is not None
    assert d2.year == 1980


def test_parse_tse_date_null():
    """Valores nulos TSE devem retornar None."""
    assert parse_tse_date(None) is None
    assert parse_tse_date("") is None
    assert parse_tse_date("#NULO#") is None
    assert parse_tse_date("#NE#") is None


def test_parse_tse_value():
    """Valores monetários TSE devem ser parseados corretamente."""
    assert parse_tse_value("1.234,56") == 1234.56
    assert parse_tse_value("100,00") == 100.00
    assert parse_tse_value("0,00") == 0.0
    assert parse_tse_value(None) == 0.0
    assert parse_tse_value("#NULO#") == 0.0
    assert parse_tse_value("") == 0.0


def test_all_ufs_present():
    """Todas as 27 UFs + BR devem estar presentes."""
    assert len(UF_CODES) == 28
    assert "SP" in UF_CODES
    assert "BR" in UF_CODES


def test_candidacy_status_map_has_common_statuses():
    """Mapa de status deve conter os valores mais comuns."""
    assert "DEFERIDO" in CANDIDACY_STATUS_MAP
    assert "INDEFERIDO" in CANDIDACY_STATUS_MAP
    assert "APTO" in CANDIDACY_STATUS_MAP
    assert "CANCELADO" in CANDIDACY_STATUS_MAP


def test_result_status_map_has_common_statuses():
    """Mapa de resultados deve conter os valores mais comuns."""
    assert "ELEITO" in RESULT_STATUS_MAP
    assert "NÃO ELEITO" in RESULT_STATUS_MAP
    assert "SUPLENTE" in RESULT_STATUS_MAP
    assert "2º TURNO" in RESULT_STATUS_MAP
