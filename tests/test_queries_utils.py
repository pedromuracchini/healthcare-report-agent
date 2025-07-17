import os
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("TAVILY_API_KEY", "test")

import pytest
from metrics.queries import build_where_clause

def test_build_where_clause_empty():
    assert build_where_clause(None) == ""
    assert build_where_clause({}) == ""

def test_build_where_clause_simple():
    filters = {"CS_SEXO": "1", "UTI": 1}
    clause = build_where_clause(filters)
    # Order may vary, so check both possibilities
    assert clause in [
        "WHERE CS_SEXO = '1' AND UTI = 1",
        "WHERE UTI = 1 AND CS_SEXO = '1'"
    ]

def test_build_where_clause_str_and_num():
    filters = {"CS_SEXO": "F", "IDADE": 30}
    clause = build_where_clause(filters)
    assert "CS_SEXO = 'F'" in clause
    assert "IDADE = 30" in clause
    assert clause.startswith("WHERE ")
