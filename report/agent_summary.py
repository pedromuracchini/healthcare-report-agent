from langchain_openai import ChatOpenAI
from metrics import queries
from sqlalchemy.engine.base import Connection


def generate_agent_summary(conn: Connection, noticias: list) -> str:
    """
    Generate a summary in Portuguese that combines:
    - Key SRAG metrics (last 30 days: increase rate, mortality, ICU, vaccination)
    - Recent SRAG news headlines
    - Data trends
    The summary should be concise, analytical, and suitable for a health manager.
    """
    # Get metrics
    daily_df = queries.daily_cases(conn, days=30)
    mortality = queries.mortality_rate(conn, filters=None)
    icu = queries.icu_rate(conn, filters=None)
    covid_vax = queries.covid_vaccination_rate(conn, filters=None)
    flu_vax = queries.flu_vaccination_rate(conn, filters=None)
    # Prepare news
    news_str = "\n".join([
        f"- {n['title']} ({n['url']})" if isinstance(n, dict) and 'title' in n and 'url' in n else f"- {n}" for n in noticias[:3]
    ])
    # Prepare metrics summary
    if not daily_df.empty and daily_df.shape[0] > 1:
        increase_rate = (daily_df["casos"].iloc[-1] - daily_df["casos"].iloc[0]) / max(daily_df["casos"].iloc[0], 1)
    else:
        increase_rate = None
    prompt = f"""
Você é um agente epidemiológico. Faça um resumo executivo, em português, para um gestor de saúde, combinando as métricas abaixo, as tendências dos dados e as notícias recentes sobre SRAG no Brasil. Destaque riscos, alertas, pontos positivos e negativos. Seja conciso e analítico.

Métricas (últimos 30 dias):
- Taxa de aumento de casos: {increase_rate:.2%} {'(N/A)' if increase_rate is None else ''}
- Taxa de mortalidade: {mortality:.2%}
- Taxa de ocupação UTI: {icu:.2%}
- Vacinação COVID-19: {covid_vax:.2%}
- Vacinação Gripe: {flu_vax:.2%}

Notícias recentes:
{news_str}

Tendências: analise os dados acima e as notícias para gerar um panorama geral.
"""
    llm = ChatOpenAI(temperature=0)
    summary = llm.invoke(prompt)
    if hasattr(summary, "content"):
        summary = summary.content
    return summary
