"""
Script to perform data quality checks on the selected SRAG columns.

This script reads the processed SRAG CSV, checks for missing values, consistency between dates, and duplicates, and outputs a summary report.
"""
import polars as pl
from agent.config import CSV_PATH, REPORT_PATH

COLUMNS_TO_KEEP = [
    'NU_NOTIFIC',
    'DT_SIN_PRI', 'DT_NOTIFIC', 'DT_INTERNA',
    'EVOLUCAO', 'DT_EVOLUCA',
    'UTI', 'DT_ENTUTI', 'DT_SAIDUTI',
    'SUPORT_VEN',
    'VACINA_COV', 'DOSE_1_COV', 'DOSE_2_COV',
    'DOSE_REF',
    'VACINA', 'DT_UT_DOSE',
    'CLASSI_FIN', 'HOSPITAL',
    'NU_IDADE_N', 'CS_SEXO', 'CO_MUN_RES',
    'CS_RACA',
    'FATOR_RISC'
]


# Helper functions for checks
def check_missing(df):
    """
    Return the count of missing (null) values per column in the DataFrame.
    Args:
        df (pl.DataFrame): Input Polars DataFrame.
    Returns:
        pl.DataFrame: DataFrame with one row and columns as missing counts.
    """
    return df.select([
        pl.col(col).null_count().alias(col) for col in df.columns
    ])


def check_date_consistency(df):
    """
    Count the number of rows where 'DT_INTERNA' is before 'DT_SIN_PRI'.
    Args:
        df (pl.DataFrame): Input Polars DataFrame.
    Returns:
        int: Number of inconsistent date rows.
    """
    inconsistent = 0
    if all(col in df.columns for col in ['DT_SIN_PRI', 'DT_INTERNA']):
        inconsistent = df.filter(
            pl.col('DT_INTERNA') < pl.col('DT_SIN_PRI')
        ).height
    return inconsistent

def check_duplicates(df):
    """
    Count the number of duplicate NU_NOTIFIC values (extra occurrences beyond the first).
    Args:
        df (pl.DataFrame): Input Polars DataFrame.
    Returns:
        int: Number of duplicate NU_NOTIFIC values.
    """
    if 'NU_NOTIFIC' in df.columns:
        counts = df['NU_NOTIFIC'].value_counts()
        n_dups = int(sum([max(x-1, 0) for x in counts['count'].to_list()]))
        return n_dups
    return 0

def main():
    """
    Main function to execute data quality checks and write the report.
    """
    if not CSV_PATH.exists():
        print(f"Error: Source CSV file not found at '{CSV_PATH}'. Aborting.")
        return
    df = pl.read_csv(CSV_PATH, columns=COLUMNS_TO_KEEP, separator=';', ignore_errors=True)
    n_rows = df.height
    report = []
    report.append("# Data Quality Report\n")
    report.append(f"**Total rows:** {n_rows}\n\n")
    report.append("## Summary\n")
    # Missing values
    missing = check_missing(df)
    n_missing = dict(zip(missing.columns, missing.row(0)))
    total_missing = sum(n_missing.values())
    report.append(f"- Total missing values: {total_missing}\n")
    for col, val in n_missing.items():
        report.append(f"  - {col}: {val}\n")
    report.append("\n")
    # Date consistency section
    inconsistent_dates = check_date_consistency(df)
    report.append("## Date Consistency\n")
    report.append(f"- Number of rows where DT_INTERNA < DT_SIN_PRI: {inconsistent_dates}\n\n")
    # Duplicates section
    dups = check_duplicates(df)
    report.append("## Duplicate NU_NOTIFIC\n")
    report.append(f"- Number of duplicate NU_NOTIFIC: {dups}\n\n")
    report.append("---\n")
    report.append("*Gerado automaticamente por scripts/data_quality_check.py*\n")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.writelines(report)
    print(f"Data quality report saved to {REPORT_PATH}")

if __name__ == "__main__":
    main()
