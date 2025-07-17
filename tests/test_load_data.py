import os
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("TAVILY_API_KEY", "test")

import pytest
import polars as pl
from scripts.load_data import treat_data

@pytest.mark.parametrize(
    "input_df,expected_dates,expected_ignored",
    [
        # Test: valid and invalid dates, 'Ignorado' as '9' and as 9.0
        (
            pl.DataFrame({
                "DT_SIN_PRI": ["2023-01-01", "01/02/2023", "invalid"],
                "EVOLUCAO": ["1", "9", "2"],
                "UTI": [9.0, 1.0, 2.0],
                "CS_SEXO": ["9", "2", "1"],
                "FATOR_RISC": ["9", "1", "2"],
                "VACINA": ["1", "9", "2"]
            }),
            ["2023-01-01", "2023-02-01", None],
            {"EVOLUCAO": ["1", None, "2"], "UTI": [9.0, 1.0, 2.0], "CS_SEXO": [None, "2", "1"], "FATOR_RISC": [None, "1", "2"], "VACINA": ["1", None, "2"]}
        ),
    ]
)
def test_treat_data(input_df, expected_dates, expected_ignored):
    result = treat_data(input_df)
    # Dates
    assert result["DT_SIN_PRI"].to_list() == expected_dates
    # Ignorado
    for col, expected in expected_ignored.items():
        assert result[col].to_list() == expected
