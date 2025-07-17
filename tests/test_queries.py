"""
Unit tests for metrics/queries.py
Covers edge cases, column checks, empty results, and filter logic.
All test code and comments are in English.
"""

import pandas as pd
from sqlalchemy import create_engine
from metrics import queries

# Use the main database for integration tests
TEST_DB = "sqlite:///database/srag_database.db"

def test_daily_cases_columns():
    """Test that daily_cases returns expected columns and non-negative case counts."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        df = queries.daily_cases(conn, days=7)
        assert isinstance(df, pd.DataFrame)
        assert set(df.columns) == {"data", "casos"}
        assert (df["casos"] >= 0).all()

def test_monthly_cases_columns():
    """Test that monthly_cases returns expected columns and non-negative case counts."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        df = queries.monthly_cases(conn, months=3)
        assert isinstance(df, pd.DataFrame)
        assert set(df.columns) == {"mes", "casos"}
        assert (df["casos"] >= 0).all()

def test_mortality_rate_range():
    """Test that mortality_rate returns a float in [0, 1] or NaN if no data."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        rate = queries.mortality_rate(conn)
        assert isinstance(rate, float)
        assert (0.0 <= rate <= 1.0) or pd.isna(rate)

def test_icu_rate_range():
    """Test that icu_rate returns a float in [0, 1] or NaN if no data."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        rate = queries.icu_rate(conn)
        assert isinstance(rate, float)
        assert (0.0 <= rate <= 1.0) or pd.isna(rate)

def test_covid_vaccination_rate_range():
    """Test that covid_vaccination_rate returns a float in [0, 1] or NaN if no data."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        rate = queries.covid_vaccination_rate(conn)
        assert isinstance(rate, float)
        assert (0.0 <= rate <= 1.0) or pd.isna(rate)

def test_flu_vaccination_rate_range():
    """Test that flu_vaccination_rate returns a float in [0, 1] or NaN if no data."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        rate = queries.flu_vaccination_rate(conn)
        assert isinstance(rate, float)
        assert (0.0 <= rate <= 1.0) or pd.isna(rate)

def test_filters_combined():
    """Test that combined filters work and return valid results."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        rate = queries.mortality_rate(conn, filters={"CS_SEXO": "F", "CS_RACA": "1"})
        assert isinstance(rate, float)
        assert (0.0 <= rate <= 1.0) or pd.isna(rate)

def test_empty_filter_returns_all():
    """Test that empty filter returns same as no filter for daily_cases."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        df1 = queries.daily_cases(conn, days=3)
        df2 = queries.daily_cases(conn, days=3, filters={})
        pd.testing.assert_frame_equal(df1, df2)

def test_invalid_filter_returns_empty():
    """Test that a filter with no matching data returns empty DataFrame or NaN for rates."""
    engine = create_engine(TEST_DB)
    with engine.connect() as conn:
        df = queries.daily_cases(conn, days=3, filters={"CS_SEXO": "INVALID"})
        assert df.empty
        rate = queries.mortality_rate(conn, filters={"CS_SEXO": "INVALID"})
        assert pd.isna(rate)
