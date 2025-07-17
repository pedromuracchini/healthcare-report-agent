"""
LangGraph agent for SRAG reporting, orchestrating LangChain tools (SQL, etc).
Implements a modular LangGraph workflow using the SQLQueryTool and other tools for SQL, summarization, news, and explanations.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_core.tools import Tool
from agent.database_tool import SQLQueryTool
from langchain_openai import ChatOpenAI
from agent.config import settings
import os

from agent.news_tool import news_query_tool
from agent.summary_tool import summary_tool
from agent.sql_generation import generate_sql_from_question

class AgentState(TypedDict, total=False):
    question: str
    sql_query: str  # <--- Propagate SQL query between nodes
    sql_result: str
    summary: str
    explanation: str
    news: str
    final_result: str


# Tool setup (using LangChain)
sql_tool = SQLQueryTool()
tools = [
    Tool.from_function(
        sql_tool._run, name=sql_tool.name, description=sql_tool.description
    )
]


# ================= GUARDRAILS =================
def is_valid_input(question: str) -> bool:
    """
    Guardrail: blocks only questions containing dangerous SQL or security terms. All other scope/intent validation is delegated to the LLM, which receives a strict instruction to answer 'Sim' only if the question is relevant to SRAG, epidemiology, or public health, and 'Não' otherwise.
    This function returns True if the input is valid for the agent workflow, False otherwise.
    """
    blocklist = [
        "drop table",
        "delete from",
        "truncate",
        "insert into",
        "update ",
        "hack",
        "senha",
        "password",
        "token",
        "script>",
    ]
    if not question.strip():
        return False
    if any(bad in question.lower() for bad in blocklist):
        return False
    # Delegate all other scope validation to LLM
    try:

        llm = ChatOpenAI(temperature=0)
        prompt = (
            "Você é um assistente de validação de escopo e deve responder apenas 'Sim' ou 'Não', sem explicação. "
            "Sua função é decidir se a pergunta abaixo está estritamente relacionada a: SRAG (Síndrome Respiratória Aguda Grave), epidemiologia, saúde pública, vigilância epidemiológica, dados de casos, mortalidade, hospitalização, vacinação, tendências epidemiológicas, explicações conceituais desses temas, ou notícias sobre SRAG no Brasil. "
            "Bloqueie perguntas sobre política, economia, esportes, tecnologia, entretenimento, temas genéricos, dúvidas pessoais, ou qualquer assunto fora do contexto epidemiológico de SRAG ou de saúde pública. "
            "Perguntas conceituais ou de definição sobre termos epidemiológicos (ex: 'O que é taxa de mortalidade?', 'Explique o que é incidência') DEVEM ser aceitas. "
            "Responda 'Sim' apenas se a pergunta for claramente relevante para os temas acima. Caso contrário, responda 'Não'. "
            "\n\nExemplos de perguntas válidas:\n"
            "- Quantos casos de SRAG foram notificados em 2024?\n"
            "- Qual a taxa de mortalidade por SRAG em crianças?\n"
            "- Explique o que é SRAG.\n"
            "- Explique o que é taxa de mortalidade.\n"
            "- O que significa incidência?\n"
            "- O que é letalidade?\n"
            "- Como funciona a notificação de casos de SRAG?\n"
            "- Quais as tendências de hospitalização por SRAG?\n"
            "- Quais as últimas notícias sobre SRAG no Brasil?\n"
            "\nExemplos de perguntas inválidas:\n"
            "- Qual a cotação do dólar?\n"
            "- Quem ganhou o jogo de futebol ontem?\n"
            "- Qual o melhor filme de 2024?\n"
            "- Como investir em ações?\n"
            "- O presidente foi reeleito?\n"
            "- Qual a previsão do tempo para amanhã?\n"
            "\nPergunta: " + question
        )
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            response = response.content
        response = response.strip().lower()
        print(
            f"[GUARDRAIL DEBUG] LLM response: '{response}' for question: '{question}'"
        )
        if "sim" in response:
            return True
        else:
            return False
    except Exception as e:
        print(f"[GUARDRAIL DEBUG] LLM exception: {e}")
        return True  # If LLM fails, default to permissive


def is_valid_sql(query: str) -> bool:
    # Allows only SLEECT and whitelited tables
    if not query.strip().lower().startswith("select"):
        return False
    allowed_tables = ["srag_cases"]
    if not any(tbl in query.lower() for tbl in allowed_tables):
        return False
    blocklist = ["--", "/*", "*/", "xp_"]
    if any(bad in query.lower() for bad in blocklist):
        return False
    return True


def is_valid_news_result(news: str) -> bool:
    if not news or len(news) < 30:
        return False
    if "brasil" not in news.lower() and ".br" not in news.lower():
        return False
    return True




def audit_log(node: str, input_state: dict, decision: str, output_state: dict):
    import json
    from datetime import datetime
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "node": node,
        "input_state": input_state,
        "decision": decision,
        "output_state": output_state,
    }
    log_path = os.path.join(
        os.path.dirname(__file__), "..", "logs", "agent_audit.log"
    )
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# ============== NODES WITH GUARDRAILS ==============
def router_node(state: AgentState, **kwargs) -> AgentState:
    """
    Decide para qual nó direcionar a pergunta.
    Aplica guardrails de input.
    """
    question = state["question"].strip()
    input_state = dict(state)
    if not is_valid_input(question):
        output = {
            **state,
            "final_result": "Pergunta inválida ou fora do escopo permitido. Reformule sua questão sobre SRAG ou saúde pública.",
        }
        audit_log(
            "router_node",
            input_state,
            "Pergunta bloqueada por guardrail",
            output,
        )
        return output
    q_lower = question.lower()
    print(f"[ROUTER DEBUG] Pergunta recebida: '{question}'")
    if any(
        word in q_lower
        for word in ["explique", "o que é", "defina", "significa"]
    ):
        output = {**state, "next_node": "explanation"}
        audit_log(
            "router_node", input_state, "Roteado para explanation", output
        )
        print("[ROUTER DEBUG] Roteado para explanation")
        return output
    elif any(
        word in q_lower
        for word in [
            "notícia",
            "notícias",
            "jornal",
            "reportagem",
            "matéria",
            "atualização",
            "mídia",
        ]
    ):
        output = {**state, "next_node": "news"}
        audit_log("router_node", input_state, "Roteado para news", output)
        print("[ROUTER DEBUG] Roteado para news")
        return output
    elif any(
        word in q_lower
        for word in [
            "quantos",
            "total",
            "casos",
            "taxa",
            "percentual",
            "mortes",
            "internados",
            "ocupação",
            "vacinação",
        ]
    ):
        output = {**state, "next_node": "sql_generation"}
        audit_log(
            "router_node", input_state, "Roteado para sql_generation", output
        )
        print("[ROUTER DEBUG] Roteado para sql_generation")
        return output
    else:
        output = {**state, "next_node": "sql_query"}
        audit_log(
            "router_node", input_state, "Fallback para sql_query", output
        )
        print("[ROUTER DEBUG] Fallback para sql_query")
        return output


def sql_query_node(state: AgentState, **kwargs) -> AgentState:
    print("[NODE DEBUG] Entrou no sql_query_node")
    input_state = dict(state)
    query = state.get("sql_query")
    if not query:
        output = {
            **state,
            "final_result": "Erro: Nenhuma query SQL foi gerada a partir da pergunta. Reformule sua questão.",
        }
        audit_log(
            "sql_query_node",
            input_state,
            "Faltando sql_query no estado",
            output,
        )
        print("[NODE DEBUG] sql_query_node retornou por falta de query")
        return output
    if not is_valid_sql(query):
        output = {
            **state,
            "final_result": "Consulta SQL inválida ou não permitida. Apenas SELECTs simples na tabela srag_data são aceitos.",
        }
        audit_log(
            "sql_query_node", input_state, "Consulta SQL inválida", output
        )
        print("[NODE DEBUG] sql_query_node retornou por query inválida")
        return output
    try:
        print(f"[SQL RAW DEBUG] Query executada: {query}")
        result = sql_tool._run(query)
        print(f"[SQL RAW DEBUG] Tipo do resultado: {type(result)}")
        print(
            f"[SQL RAW DEBUG] Resultado bruto retornado pelo banco: {result}"
        )
        if result is None or (isinstance(result, list) and len(result) == 0):
            result_str = "[]"
        else:
            result_str = str(result)
    except Exception as e:
        output = {
            **state,
            "final_result": f"Erro ao executar query SQL: {str(e)}",
        }
        audit_log(
            "sql_query_node",
            input_state,
            f"Erro ao executar SQL: {str(e)}",
            output,
        )
        return output
    print(f"[SQL RAW DEBUG] Valor normalizado para sql_result: {result_str}")
    output = {**state, "sql_result": result_str, "next_node": "summarization"}
    audit_log(
        "sql_query_node",
        input_state,
        "Resultado SQL roteado para summarization",
        output,
    )
    print(
        "[NODE DEBUG] sql_query_node finalizou e retornou para summarization_node"
    )
    return output


def summarization_node(state: AgentState, **kwargs) -> AgentState:
    print("[NODE DEBUG] Entrou no summarization_node")
    input_state = dict(state)
    sql_result = state.get("sql_result", None)
    print(
        f"[SUMMARIZATION DEBUG] Tipo de sql_result: {type(sql_result)} | Valor: {sql_result}"
    )
    if sql_result is None or (
        isinstance(sql_result, str) and not sql_result.strip()
    ):
        msg = "[SUMMARIZATION DEBUG] Nenhum resultado SQL encontrado para resumir."
        print(msg)
        output = {
            **state,
            "final_result": "Não há resultado SQL para resumir.",
        }
        audit_log("summarization_node", input_state, msg, output)
        print("[NODE DEBUG] summarization_node retornou por sql_result vazio")
        return output
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(temperature=0)
    prompt = f"Resuma o seguinte resultado de consulta SQL para um relatório epidemiológico: {sql_result}"
    summary = llm.invoke(prompt)
    if hasattr(summary, "content"):
        summary = summary.content
    output = {**state, "final_result": summary}
    audit_log(
        "summarization_node", input_state, "Resumo gerado por LLM", output
    )
    print("[NODE DEBUG] summarization_node finalizou e retornou resultado")
    return output


def explanation_node(state: AgentState, **kwargs) -> AgentState:
    input_state = dict(state)
    llm = ChatOpenAI(temperature=0)
    prompt = f"Explique em português, de forma simples e clara, o seguinte conceito epidemiológico: {state['question']}"
    explanation = llm.invoke(prompt)
    if hasattr(explanation, "content"):
        explanation = explanation.content
    output = {**state, "explanation": explanation, "final_result": explanation}
    audit_log(
        "explanation_node", input_state, "Explicação gerada por LLM", output
    )
    return output



news_tool = news_query_tool
summary_tool = summary_tool


def news_node(state: AgentState, **kwargs) -> AgentState:
    input_state = dict(state)
    query = state["question"]
    try:
        news_results = news_tool.invoke(query)
    except Exception as e:
        output = {
            **state,
            "final_result": f"Erro ao buscar notícias: {str(e)}",
        }
        audit_log("news_node", input_state, "Erro ao buscar notícias", output)
        return output
    if not is_valid_news_result(news_results):
        output = {
            **state,
            "final_result": "Não foi possível encontrar notícias confiáveis e recentes sobre SRAG no Brasil no momento.",
        }
        audit_log(
            "news_node",
            input_state,
            "Nenhuma notícia confiável encontrada",
            output,
        )
        return output
    output = {**state, "news": news_results, "final_result": news_results}
    audit_log(
        "news_node", input_state, "Notícias retornadas com sucesso", output
    )
    return output


def summary_node(state: AgentState, **kwargs) -> AgentState:
    input_state = dict(state)
    try:
        summary = summary_tool.invoke("")
    except Exception as e:
        output = {
            **state,
            "final_result": f"Erro ao gerar resumo executivo: {str(e)}",
        }
        audit_log("summary_node", input_state, "Erro ao gerar resumo", output)
        return output
    output = {**state, "summary": summary, "final_result": summary}
    audit_log("summary_node", input_state, "Resumo executivo gerado", output)
    return output


# LLM setup (OpenAI, can be swapped for other providers)
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
llm = ChatOpenAI(temperature=0)


# Build the LangGraph


def sql_generation_node(state: AgentState, **kwargs) -> AgentState:
    print("[NODE DEBUG] Entrou no sql_generation_node")
    question = state["question"]
    sql = generate_sql_from_question(question)
    print(f"[SQLGEN DEBUG] SQL gerado para '{question}': {sql}")
    if not sql or not sql.strip().lower().startswith("select"):
        output = {
            **state,
            "final_result": "Erro: Não foi possível gerar uma query SQL válida a partir da pergunta.",
        }
        audit_log("sql_generation_node", state, "Falha ao gerar SQL", output)
        print(
            "[NODE DEBUG] sql_generation_node retornou por falha de geração de SQL"
        )
        return output
    print(
        f"[NODE DEBUG] sql_generation_node retornando estado com sql_query: {sql}"
    )
    return {**state, "sql_query": sql}


workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("sql_generation", sql_generation_node)
workflow.add_node("sql_query", sql_query_node)
workflow.add_node("summarization", summarization_node)
workflow.add_node("explanation", explanation_node)
workflow.add_node("news", news_node)
workflow.add_node("summary", summary_node)

workflow.set_entry_point("router")


def sanitize_next_node(state):
    valid_nodes = {
        "sql_generation",
        "sql_query",
        "explanation",
        "summarization",
        "news",
        "summary",
    }
    n = state.get("next_node", None)
    if n in valid_nodes:
        return [n]
    return []


workflow.add_conditional_edges(
    "router",
    sanitize_next_node,
    {
        "sql_generation": "sql_generation",
        "sql_query": "sql_query",
        "explanation": "explanation",
        "summarization": "summarization",
        "news": "news",
        "summary": "summary",
    },
)
workflow.add_edge("sql_generation", "sql_query")
workflow.add_edge("sql_query", "summarization")
workflow.add_edge("summarization", END)
workflow.add_edge("explanation", END)
workflow.add_edge("news", END)
workflow.add_edge("summary", END)
langgraph_agent = workflow.compile()


def clean_state(state):
    # Removes next_node if it's '__end__'
    if state.get("next_node") == "__end__":
        state = dict(state)
        del state["next_node"]
    return state


def ask_langgraph_agent(question: str):
    state = {"question": question}
    print("[DEBUG] Estado inicial passado ao agente:", state)
    result = langgraph_agent.invoke(clean_state(state))
    return result.get("final_result", "No result")


if __name__ == "__main__":
    print(ask_langgraph_agent("Quantos casos de SRAG de mulheres em 2025?"))
    print(ask_langgraph_agent("Explique o que é taxa de mortalidade"))
