"""
Configuration using Pydantic Settings for environment variables.
"""
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }
    """
    Project settings loaded from environment .env file.
    """
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str 

# Path to the main SRAG database (relative to project root)
DB_PATH = os.getenv("DB_PATH", "database/srag_database.db")

# Path to the SRAG CSV file (relative to project root)
CSV_PATH = os.getenv("CSV_PATH", "data/srag_data.csv")

# Path to the data quality report output (relative to project root)
REPORT_PATH = os.getenv("REPORT_PATH", "report/data_quality_report.md")

# List of allowed tables for SQL queries (security guardrail)
ALLOWED_TABLES = [
    "srag_cases"
]

# Directory for audit logs
LOGS_DIR = os.getenv("LOGS_DIR", os.path.join(os.path.dirname(__file__), "..", "logs"))

# Path to the cleaned data dictionary JSON (relative to project root)
DATA_DICTIONARY_PATH = os.getenv("DATA_DICTIONARY_PATH", os.path.join(os.path.dirname(__file__), "..", "docs", "data_dictionary_clean.json"))

settings = Settings()

__all__ = [
    "DB_PATH",
    "CSV_PATH",
    "REPORT_PATH",
    "ALLOWED_TABLES",
    "LOGS_DIR",
    "DATA_DICTIONARY_PATH",
    "settings"
]
