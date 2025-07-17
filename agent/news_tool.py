"""
NewsQueryTool: LangChain Tool for searching recent news about SRAG in Brazil.
"""
from langchain_core.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults

from agent.config import settings

def news_query_tool_run(query: str) -> str:
    """
    Search for recent news about Severe Acute Respiratory Syndrome (SRAG) in Brazil using Tavily.
    Args:
        query (str): Additional query string to refine the search.
    Returns:
        str: News results as a string (JSON or plain text).
    """
    search = TavilySearchResults(tavily_api_key=settings.TAVILY_API_KEY)
    search_query = f"notícias recentes Síndrome Respiratória Aguda Grave Brasil {query}"
    return search.run(search_query)

news_query_tool = Tool.from_function(
    news_query_tool_run,
    name="news_query_tool",
    description=(
        "Busca notícias recentes sobre Síndrome Respiratória Aguda Grave (SRAG) no Brasil, "
        "retornando manchetes e resumos relevantes para contextualizar métricas epidemiológicas."
    ),
)
