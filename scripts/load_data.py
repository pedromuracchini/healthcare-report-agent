"""
Processes and loads SRAG hospitalization data into a SQLite database.

This script performs the following actions:
1.  Reads the raw SRAG data from a CSV file using Polars.
2.  Selects only the columns necessary for the analysis.
3.  Cleans the data by converting data types and handling missing value codes.
4.  Loads the cleaned data into a SQLite database table, replacing any old data.
"""

import polars as pl

# --- PROJECT CONSTANTS ---
from agent.config import CSV_PATH, DB_PATH

# Define table name and DB connection URI locally for this script
TABLE_NAME = "srag_cases"
DB_CONNECTION_URI = f"sqlite:///{DB_PATH}"

# Columns to keep for the analysis.
COLUMNS_TO_KEEP = [
    'DT_SIN_PRI', 'DT_NOTIFIC', 'DT_INTERNA',  # Dates for case counting
    'EVOLUCAO', 'DT_EVOLUCA',                 # Mortality
    'UTI', 'DT_ENTUTI', 'DT_SAIDUTI',         # ICU occupancy
    'SUPORT_VEN',                             # Severity indicator
    'VACINA_COV', 'DOSE_1_COV', 'DOSE_2_COV', # COVID vaccination
    'DOSE_REF',                               # COVID booster vaccination
    'VACINA', 'DT_UT_DOSE',                   # Flu vaccination
    'CLASSI_FIN', 'HOSPITAL',                 # Quality filters
    'NU_IDADE_N', 'CS_SEXO', 'CO_MUN_RES', 
    'CS_RACA',                                # Demographics
    'FATOR_RISC'                              # Com/orbidities
]

def treat_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Applies cleaning and transformation rules to the SRAG DataFrame.

    This function performs two main cleaning operations:
    - Converts all date-related columns to a proper datetime format.
    - Replaces the numeric code for 'Ignorado' (9 or 9.0) with null
    dvalues for better analytical processing.

    Args:
        df: The input Polars DataFrame with raw data.

    Returns:
        A new Polars DataFrame with the transformations applied.
    """
    print("Applying data treatment rules...")
    date_cols = [col for col in df.columns if 'DT_' in col or 'DOSE_' in col]
    ignored_val_cols = ['EVOLUCAO', 'UTI', 'CS_SEXO', 'FATOR_RISC', 'VACINA']

    # Detect column types for Ignorado
    ign_map = {}
    for c in ignored_val_cols:
        dtype = df[c].dtype if c in df.columns else None
        if dtype is not None and dtype == pl.Utf8:
            ign_map[c] = ['9']
        else:
            ign_map[c] = [9.0]

    # Função auxiliar para parsing robusto: tenta YYYY-MM-DD, se falhar tenta DD/MM/YYYY
    def parse_date_col(col):
        return (
            pl.when(
                pl.col(col).str.strptime(pl.Date, format="%Y-%m-%d", strict=False).is_not_null()
            )
            .then(pl.col(col).str.strptime(pl.Date, format="%Y-%m-%d", strict=False))
            .otherwise(pl.col(col).str.strptime(pl.Date, format="%d/%m/%Y", strict=False))
            .dt.strftime("%Y-%m-%d")
            .alias(col)
        )

    transformed_df = df.with_columns(
        *[parse_date_col(c) for c in date_cols],
        *[
            pl.when(pl.col(c).cast(str).is_in(['9']))
              .then(None)
              .otherwise(pl.col(c))
              .alias(c)
            for c in ignored_val_cols
        ]
    )
    print("Data treatment finished.")
    return transformed_df

def load_to_sqlite(df: pl.DataFrame, db_uri: str, table_name: str):
    """
    Loads a DataFrame into a specified SQLite table.

    The function will replace the table if it already exists, making this
    operation idempotent and suitable for development workflows.

    Args:
        df: The cleaned Polars DataFrame to be loaded.
        db_uri: The connection URI for the SQLite database.
        table_name: The name of the table to create or replace.
    """
    print(f"Loading data into table '{table_name}'...")
    try:
        # Remove a tabela se já existir
        import sqlalchemy
        engine = sqlalchemy.create_engine(db_uri.replace('sqlite:///', 'sqlite:///'))
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {table_name}"))
        df.write_database(
            table_name=table_name,
            connection=db_uri
        )
        print("Data loaded successfully.")
    except Exception as e:
        print(f"An error occurred during database write operation: {e}")
        raise

def main():
    """Main function to orchestrate the ETL process."""
    if not CSV_PATH.exists():
        print(f"Error: Source CSV file not found at '{CSV_PATH}'. Aborting.")
        return

    print(f"Starting ETL process from '{CSV_PATH}'...")
    # 1. Extract
    raw_df = pl.read_csv(
        CSV_PATH,
        columns=COLUMNS_TO_KEEP,
        separator=';',
        ignore_errors=True
    )
    # 2. Transform
    treated_df = treat_data(raw_df)
    # 3. Load
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    load_to_sqlite(treated_df, DB_CONNECTION_URI, TABLE_NAME)
    print("ETL process completed successfully.")

if __name__ == "__main__":
    main()