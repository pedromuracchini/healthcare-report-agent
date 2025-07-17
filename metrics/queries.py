"""
Module with queries and functions for calculating epidemiological metrics for SRAG.
Designed for use by agents (LangChain/LangGraph) and Python scripts.
"""

import pandas as pd
from typing import Dict, Any, Optional
from sqlalchemy.engine import Connection

# Utility to build dynamic WHERE clause for SQL queries


def build_where_clause(filters: Optional[Dict[str, Any]]) -> str:
    """
    Build a dynamic SQL WHERE clause from a dictionary of filters.
    Args:
        filters: Dictionary where keys are column names and values are filter values.
    Returns:
        SQL WHERE clause as a string (empty if no filters).
    """
    if not filters:
        return ""
    clauses = []
    for k, v in filters.items():
        if isinstance(v, str):
            clauses.append(f"{k} = '{v}'")
        else:
            clauses.append(f"{k} = {v}")
    return "WHERE " + " AND ".join(clauses)


# 1. Daily case increase (last N days)
def daily_cases(
    conn: Connection, days: int = 30, filters: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Get daily case counts for the last N days, optionally filtered.
    Args:
        conn: SQLAlchemy connection to the database.
        days: Number of days to look back from today.
        filters: Optional dictionary of filters (e.g. {"CS_SEXO": "F"}).
    Returns:
        DataFrame with columns ['data', 'casos'].
    """
    where = build_where_clause(filters)
    query = f"""
        SELECT DT_SIN_PRI AS data, COUNT(*) AS casos
        FROM srag_cases
        WHERE DT_SIN_PRI >= date('now', '-{days} days')
        {("AND " + where[6:]) if where else ""}
        GROUP BY DT_SIN_PRI
        ORDER BY DT_SIN_PRI
    """
    return pd.read_sql(query, conn)


# 2. Monthly case counts (last N months)
def monthly_cases(
    conn: Connection,
    months: int = 12,
    filters: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Get monthly case counts for the last N months, optionally filtered.
    Args:
        conn: SQLAlchemy connection to the database.
        months: Number of months to look back from today.
        filters: Optional dictionary of filters.
    Returns:
        DataFrame with columns ['month', 'cases'].
    """
    where = build_where_clause(filters)
    query = f"""
        SELECT strftime('%Y-%m', DT_SIN_PRI) AS mes, COUNT(*) AS casos
        FROM srag_cases
        WHERE DT_SIN_PRI >= date('now', '-{months} months')
        {("AND " + where[6:]) if where else ""}
        GROUP BY mes
        ORDER BY mes;
    """
    return pd.read_sql(query, conn)


# 3. Mortality rate
def mortality_rate(
    conn: Connection, filters: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate the mortality rate (fraction of cases with outcome 'death').
    Args:
        conn: SQLAlchemy connection to the database.
        filters: Optional dictionary of filters.
    Returns:
        Float between 0 and 1. Returns NaN if denominator is zero.
    """
    where = build_where_clause(filters)
    query = f"""
        SELECT
            SUM(CASE WHEN EVOLUCAO = '2' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS taxa_mortalidade
        FROM srag_cases
        {where};
    """
    return pd.read_sql(query, conn).iloc[0, 0]


# 4. ICU admission rate
def icu_rate(
    conn: Connection, filters: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate the ICU admission rate (fraction of cases admitted to ICU).
    Args:
        conn: SQLAlchemy connection to the database.
        filters: Optional dictionary of filters.
    Returns:
        Float between 0 and 1. Returns NaN if denominator is zero.
    """
    where = build_where_clause(filters)
    query = f"""
        SELECT
            SUM(CASE WHEN UTI = '1' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS taxa_uti
        FROM srag_cases
        {where};
    """
    return pd.read_sql(query, conn).iloc[0, 0]


# 5. COVID-19 vaccination rate
def covid_vaccination_rate(
    conn: Connection, filters: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate the COVID-19 vaccination rate (fraction of cases with vaccine).
    Args:
        conn: SQLAlchemy connection to the database.
        filters: Optional dictionary of filters.
    Returns:
        Float between 0 and 1. Returns NaN if denominator is zero.
    """
    where = build_where_clause(filters)
    query = f"""
        SELECT
            SUM(CASE WHEN VACINA_COV = '1' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS taxa_vacinacao_covid
        FROM srag_cases
        {where};
    """
    return pd.read_sql(query, conn).iloc[0, 0]


# 6. Flu vaccination rate
def flu_vaccination_rate(
    conn: Connection, filters: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate the flu vaccination rate (fraction of cases vaccinated for flu).
    Args:
        conn: SQLAlchemy connection to the database.
        filters: Optional dictionary of filters.
    Returns:
        Float between 0 and 1. Returns NaN if denominator is zero.
    """
    where = build_where_clause(filters)
    query = f"""
        SELECT
            SUM(CASE WHEN VACINA = '1' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS taxa_vacinacao_gripe
        FROM srag_cases
        {where};
    """
    return pd.read_sql(query, conn).iloc[0, 0]
