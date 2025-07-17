import os
from sqlalchemy import create_engine, text

from agent.config import DB_PATH
abs_db_path = os.path.abspath(DB_PATH)
print(f"DB_PATH: {abs_db_path}")
print(f"Existe? {os.path.exists(abs_db_path)}")

if not os.path.exists(abs_db_path):
    print("[ERRO] O arquivo do banco NÃO existe!")
    exit(1)

engine = create_engine(f"sqlite:///{abs_db_path}")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) as total FROM srag_cases"))
    rows = result.fetchall()
    columns = result.keys()
    print(f"columns: {columns}")
    print(f"rows: {rows}")
    dict_rows = [dict(zip(columns, row)) for row in rows]
    print(f"dict_rows: {dict_rows}")
