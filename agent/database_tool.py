"""
LangChain tool for secure SQL queries to the SRAG SQLite database.
Exposes only SELECT queries and whitelisted tables for the agent.
"""
from langchain.tools import BaseTool
from sqlalchemy import create_engine, text
from typing import Any

from agent.config import DB_PATH, ALLOWED_TABLES
import os

class SQLQueryTool(BaseTool):
    name: str = "query_sqlite"
    description: str = (
        "Use this tool to query the SRAG database (SQLite). "
        "Only SELECT statements are allowed. Table available: srag_cases. "
        "Example: SELECT COUNT(*) FROM srag_cases WHERE CS_SEXO='F';"
    )

    def _run(self, query: str) -> Any:
        """
        Execute a secure SQL SELECT query on the SRAG SQLite database, only allowing whitelisted tables.
        Args:
            query (str): The SQL SELECT query to execute.
        Returns:
            Any: Query result as a list of dictionaries or an error message.
        """
        if not query.strip().lower().startswith("select"):
            return "Only SELECT statements are allowed."
        if any(tbl not in query for tbl in ALLOWED_TABLES):
            return f"Only the following tables are allowed: {ALLOWED_TABLES}"
        abs_db_path = os.path.abspath(DB_PATH)
        print(f"[DB TOOL DEBUG] DB_PATH (relativo): {DB_PATH}")
        print(f"[DB TOOL DEBUG] DB_PATH (absoluto): {abs_db_path}")
        if not os.path.exists(abs_db_path):
            print(f"[DB TOOL ERROR] O arquivo do banco NÃO existe: {abs_db_path}")
            raise FileNotFoundError(f"Banco de dados não encontrado: {abs_db_path}")
        else:
            print(f"[DB TOOL DEBUG] O arquivo do banco existe: {abs_db_path}")
        engine = create_engine(f"sqlite:///{abs_db_path}")
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()
                print(f"[DB TOOL DEBUG] rows: {rows}")
                print(f"[DB TOOL DEBUG] columns: {columns}")
                dict_rows = [dict(zip(columns, row)) for row in rows]
                print(f"[DB TOOL DEBUG] dict_rows: {dict_rows}")
                return dict_rows
        except Exception as e:
            return f"Query error: {str(e)}"

    async def _arun(self, query: str) -> Any:
        return self._run(query)
