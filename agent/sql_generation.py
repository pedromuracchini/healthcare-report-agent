"""
Intermediate node for automatic SQL generation via LLM from natural language questions.
"""
from langchain_openai import ChatOpenAI
from agent.data_dictionary import get_field_options

CS_SEXO_OPTIONS = get_field_options("CS_SEXO")
CS_SEXO_DESC = ", ".join([f"{k}={v}" for k,v in CS_SEXO_OPTIONS.items()]) if CS_SEXO_OPTIONS else "1-Male, 2-Female, 9-Ignored"

PROMPT_EXAMPLES = """
Exemplos:
Pergunta: Quantos casos de SRAG de mulheres em 2024?
Query SQL: SELECT COUNT(*) FROM srag_cases WHERE CS_SEXO='F' AND strftime('%Y', DT_NOTIFIC)='2024';

Pergunta: Quantos casos de SRAG de homens?
Query SQL: SELECT COUNT(*) FROM srag_cases WHERE CS_SEXO='M';

Pergunta: Quantos casos ignorados de sexo?
Query SQL: SELECT COUNT(*) FROM srag_cases WHERE CS_SEXO='I';
"""

def generate_sql_from_question(question: str) -> str:
    """
    Uses an LLM to convert a natural language question into a secure SQL query for the srag_cases table, using real options from the data dictionary.
    Args:
        question (str): The natural language question.
    Returns:
        str: A generated SQL query string.
    """
    llm = ChatOpenAI(temperature=0)
    prompt = (
        f"""
Você é um assistente que converte perguntas em português sobre epidemiologia/SRAG em queries SQL para a tabela srag_cases de um banco SQLite.
Utilize apenas as colunas e valores do dicionário de dados abaixo. NÃO use tabelas que não estejam listadas. NÃO inclua comandos perigosos.
Responda apenas com a query SQL completa, sem explicação.

Coluna CS_SEXO: valores possíveis: {CS_SEXO_DESC}.
{PROMPT_EXAMPLES}
Pergunta: {question}
Query SQL:
"""
    )
    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        response = response.content
    for line in response.splitlines():
        if line.strip().lower().startswith("select"):
            return line.strip()
    return response.strip()
