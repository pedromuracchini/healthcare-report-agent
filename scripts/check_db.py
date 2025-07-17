import pandas as pd
from sqlalchemy import create_engine

from agent.config import DB_PATH, TABLE_NAME

engine = create_engine(f"sqlite:///{DB_PATH}")

with engine.connect() as conn:
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} LIMIT 5", conn)
    count = pd.read_sql(f"SELECT COUNT(*) as total FROM {TABLE_NAME}", conn)

print("Primeiras 5 linhas:")
print(df)
print("\nTotal de linhas:")
print(count['total'][0])
