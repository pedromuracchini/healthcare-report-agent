import os
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("TAVILY_API_KEY", "test")

import pytest
import polars as pl
from scripts.data_quality_check import check_missing, check_date_consistency, check_duplicates

def test_check_missing():
    df = pl.DataFrame({"a": [1, None, 3], "b": [None, None, 1]})
    missing = check_missing(df)
    assert missing[0, "a"] == 1
    assert missing[0, "b"] == 2

def test_check_date_consistency():
    df = pl.DataFrame({
        "DT_SIN_PRI": ["2023-01-01", "2023-01-02"],
        "DT_INTERNA": ["2023-01-02", "2022-12-31"]
    })
    # Only the second row is inconsistent
    assert check_date_consistency(df) == 1

def test_check_duplicates():
    df = pl.DataFrame({"NU_NOTIFIC": [1, 2, 2, 3]})
    assert check_duplicates(df) == 1
    df2 = pl.DataFrame({"NU_NOTIFIC": [1, 2, 3]})
    assert check_duplicates(df2) == 0
