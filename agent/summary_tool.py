"""
SummaryTool: LangChain Tool to generate an executive epidemiological summary using metrics, data, and news.
"""
from langchain_core.tools import Tool
from report.agent_summary import generate_agent_summary
from sqlalchemy import create_engine

from agent.config import DB_PATH
ENGINE = create_engine(f"sqlite:///{DB_PATH}")

def summary_tool_run(_: str = "") -> str:
    """
    Executes the agent's executive summary using the database and current news.
    Returns:
        str: The generated summary string.
    """
    with ENGINE.connect() as conn:
        # For the tool, fetch news within the summary itself
        from agent.news_tool import news_query_tool_run
        noticias_raw = news_query_tool_run("")
        import json
        if isinstance(noticias_raw, str):
            try:
                noticias_list = json.loads(noticias_raw)
                if not isinstance(noticias_list, list):
                    noticias_list = [noticias_raw]
            except Exception:
                noticias_list = [noticias_raw]
        else:
            noticias_list = noticias_raw
        return generate_agent_summary(conn, noticias_list)

summary_tool = Tool.from_function(
    summary_tool_run,
    name="summary_tool",
    description="Gera um resumo executivo epidemiológico combinando métricas, tendências e notícias SRAG para gestores. Sempre responde em português."
)
