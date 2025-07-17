"""
Streamlit app for interactive SRAG epidemiological reporting.
Shows key metrics and charts for the last 30 days/12 months.
Ready for future agent integration.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics import queries
from agent.summary_tool import ENGINE

from agent.langgraph_agent import ask_langgraph_agent
from agent.news_tool import news_query_tool_run
from report.agent_summary import generate_agent_summary

st.set_page_config(page_title="Relatório SRAG", layout="wide")
st.title("Relatório Epidemiológico de SRAG")
st.markdown("""
Este painel apresenta as principais métricas e tendências epidemiológicas das hospitalizações por Síndrome Respiratória Aguda Grave (SRAG), usando os dados mais recentes disponíveis.
""")

with ENGINE.connect() as conn:
    # Main Metrics (Last 30 Days)
    st.header("Métricas Principais (Últimos 30 dias)")
    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    # Card 1: Daily case increase rate
    with col1:
        daily_df = queries.daily_cases(conn, days=30)
        if not daily_df.empty and daily_df.shape[0] > 1:
            increase_rate = (daily_df["casos"].iloc[-1] - daily_df["casos"].iloc[0]) / max(daily_df["casos"].iloc[0], 1)
        else:
            increase_rate = float('nan')
        st.markdown(f"""
            <div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                <div style='font-size:1.15em; font-weight:600;'>Taxa de aumento de casos</div>
                <div style='font-size:2.1em; font-weight:700; color:#0072B2; margin-top:8px;'>
                    {increase_rate:.2%}
                </div>
            </div>
        """ if pd.notna(increase_rate) else "<div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'><div style='font-size:1.15em; font-weight:600;'>Taxa de aumento de casos</div><div style='font-size:2.1em; font-weight:700; color:#0072B2; margin-top:8px;'>N/A</div></div>", unsafe_allow_html=True)
    # Card 2: Mortality rate
    with col2:
        mortality = queries.mortality_rate(conn, filters=None)
        st.markdown(f"""
            <div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                <div style='font-size:1.15em; font-weight:600;'>Taxa de mortalidade</div>
                <div style='font-size:2.1em; font-weight:700; color:#d7263d; margin-top:8px;'>
                    {mortality:.2%}
                </div>
            </div>
        """ if pd.notna(mortality) else "<div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'><div style='font-size:1.15em; font-weight:600;'>Taxa de mortalidade</div><div style='font-size:2.1em; font-weight:700; color:#d7263d; margin-top:8px;'>N/A</div></div>", unsafe_allow_html=True)
    # Card 3: ICU occupancy rate
    with col3:
        icu = queries.icu_rate(conn, filters=None)
        st.markdown(f"""
            <div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                <div style='font-size:1.15em; font-weight:600;'>Taxa de ocupação UTI</div>
                <div style='font-size:2.1em; font-weight:700; color:#1a936f; margin-top:8px;'>
                    {icu:.2%}
                </div>
            </div>
        """ if pd.notna(icu) else "<div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'><div style='font-size:1.15em; font-weight:600;'>Taxa de ocupação UTI</div><div style='font-size:2.1em; font-weight:700; color:#1a936f; margin-top:8px;'>N/A</div></div>", unsafe_allow_html=True)
    # Card 4: COVID vaccination rate
    with col4:
        covid_vax = queries.covid_vaccination_rate(conn, filters=None)
        st.markdown(f"""
            <div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                <div style='font-size:1.15em; font-weight:600;'>Vacinação COVID-19</div>
                <div style='font-size:2.1em; font-weight:700; color:#e69f00; margin-top:8px;'>
                    {covid_vax:.2%}
                </div>
            </div>
        """ if pd.notna(covid_vax) else "<div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'><div style='font-size:1.15em; font-weight:600;'>Vacinação COVID-19</div><div style='font-size:2.1em; font-weight:700; color:#e69f00; margin-top:8px;'>N/A</div></div>", unsafe_allow_html=True)
    # Card 5: Flu vaccination rate
    with col5:
        flu_vax = queries.flu_vaccination_rate(conn, filters=None)
        st.markdown(f"""
            <div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                <div style='font-size:1.15em; font-weight:600;'>Vacinação Gripe</div>
                <div style='font-size:2.1em; font-weight:700; color:#e69f00; margin-top:8px;'>
                    {flu_vax:.2%}
                </div>
            </div>
        """ if pd.notna(flu_vax) else "<div style='background:#f8f9fa; border-radius:12px; padding:22px 0 18px 0; margin-bottom:6px; box-shadow:0 1px 4px #eee; text-align:center; width:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;'><div style='font-size:1.15em; font-weight:600;'>Vacinação Gripe</div><div style='font-size:2.1em; font-weight:700; color:#e69f00; margin-top:8px;'>N/A</div></div>", unsafe_allow_html=True)

    st.divider()
    # Charts: Case trends
    st.header("Tendências de Casos")
    chart1, chart2 = st.columns(2)
    with chart1:
        # Daily cases chart (last 30 days)
        st.subheader("Casos diários (últimos 30 dias)")
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(daily_df["data"], daily_df["casos"], marker="o")
        ax.set_xlabel("Data")
        ax.set_ylabel("Casos")
        ax.set_title("Casos diários - Últimos 30 dias")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    with chart2:
        # Monthly cases chart (last 12 months)
        st.subheader("Casos mensais (últimos 12 meses)")
        monthly_df = queries.monthly_cases(conn, months=12)
        fig2, ax2 = plt.subplots(figsize=(6,3))
        ax2.bar(monthly_df["mes"], monthly_df["casos"], color="#1f77b4")
        ax2.set_xlabel("Mês")
        ax2.set_ylabel("Casos")
        ax2.set_title("Casos mensais - Últimos 12 meses")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig2)

# Info for users: panel ready for future AI agent integration
st.info("Este painel está pronto para integração futura com agentes de IA para análises dinâmicas e explicações automáticas.")

# ===== LangGraph Agent Integration =====

st.divider()

# News section: always visible at the top
st.header("Notícias recentes sobre SRAG no Brasil")
with st.spinner("Buscando notícias relevantes..."):
    try:
        noticias_raw = news_query_tool_run("")
    except Exception as e:
        noticias_raw = f"Erro ao buscar notícias: {e}"
noticias_list = []
if noticias_raw:
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
    for i, news in enumerate(noticias_list[:3], 1):
        if isinstance(news, dict) and 'title' in news and 'url' in news:
            st.markdown(f"**{i}. [{news['title']}]({news['url']})**")
            if 'snippet' in news:
                st.caption(news['snippet'])
        else:
            st.markdown(f"**{i}.** {news}")

# Agent Executive Summary
with ENGINE.connect() as conn:
    with st.spinner("Gerando resumo executivo do agente..."):
        try:
            agent_summary = generate_agent_summary(conn, noticias_list)
        except Exception as e:
            agent_summary = None
if agent_summary:
    st.info(agent_summary)

# Exemplos de perguntas sugeridas para o agente
EXAMPLE_QUESTIONS = [
    "Quantos casos de SRAG foram notificados em 2025?",
    "Qual a taxa de mortalidade por SRAG em crianças?",
    "Explique o que é SRAG.",
    "Explique o que é taxa de mortalidade.",
    "O que significa incidência?",
    "Como funciona a notificação de casos de SRAG?",
    "Quais as tendências de hospitalização por SRAG?",
    "Quais as últimas notícias sobre SRAG no Brasil?",
]
st.markdown("""
**Exemplos de perguntas para o agente:**
<ul>
""" + "\n".join([f"<li>{q}</li>" for q in EXAMPLE_QUESTIONS]) + "\n</ul>" , unsafe_allow_html=True)

# Pergunte ao Agente Epidemiológico
st.header("Pergunte ao Agente Epidemiológico")
user_question = st.text_input("Digite sua pergunta sobre SRAG, epidemiologia, métricas ou notícias:")

if user_question:
    with st.spinner("Consultando agente..."):
        agent_response = ask_langgraph_agent(user_question)
    # If response is a simple string, maintain compatibility
    if isinstance(agent_response, str):
        st.markdown(f"**Resposta do agente:**\n\n{agent_response}")
        news_items = None
    else:
        st.markdown(f"**Resposta do agente:**\n\n{agent_response.get('final_result', '')}")
        news_items = agent_response.get('news', None)
    # Display news if available
    if news_items:
        st.subheader("Notícias relevantes sobre SRAG no Brasil")
        if isinstance(news_items, str):
            # Try to convert to list if string is JSON/list
            import json
            try:
                news_list = json.loads(news_items)
                if not isinstance(news_list, list):
                    news_list = [news_items]
            except Exception:
                news_list = [news_items]
        else:
            news_list = news_items
        # Show up to 3 news items
        for i, news in enumerate(news_list[:3], 1):
            if isinstance(news, dict) and 'title' in news and 'url' in news:
                st.markdown(f"**{i}. [{news['title']}]({news['url']})**")
                if 'snippet' in news:
                    st.caption(news['snippet'])
            else:
                st.markdown(f"**{i}.** {news}")
