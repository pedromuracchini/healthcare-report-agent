# Relatório Epidemiológico SRAG — Indicium HealthCare Inc

## Sumário

- [Contexto e Desafio](#contexto-e-desafio)
- [Principais Funcionalidades](#principais-funcionalidades)
- [Como a Solução Atende aos Requisitos do Desafio](#como-a-solução-atende-aos-requisitos-do-desafio)
- [Arquitetura da Solução](#arquitetura-da-solução)
- [Pipeline de Dados e Qualidade](#pipeline-de-dados-e-qualidade)
- [Segurança, Governança e Auditoria](#segurança-governança-e-auditoria)
- [Testes](#testes)
- [Instalação e Execução](#instalação-e-execução)
- [Configuração de variáveis de ambiente](#configuração-de-variáveis-de-ambiente)
- [Estrutura dos Principais Arquivos](#estrutura-dos-principais-arquivos)
- [Entrega e Documentação](#entrega-e-documentação)
- [Licença](#licença)

---

## Contexto e Desafio

Este repositório apresenta a Prova de Conceito (PoC) desenvolvida para a Indicium HealthCare Inc., cujo objetivo é construir uma solução de Inteligência Artificial Generativa para gerar relatórios automatizados e dinâmicos sobre a evolução de surtos de doenças, com foco inicial em Síndrome Respiratória Aguda Grave (SRAG).

A solução foi desenhada para auxiliar profissionais de saúde a entenderem, em tempo real, a severidade e o avanço de surtos, integrando dados oficiais e notícias atuais para contextualização.

**Desafio:**
- Integrar dados reais do Open DATASUS (hospitalizações por SRAG) com notícias em tempo real.
- Gerar métricas essenciais, gráficos, explicações e sumarização automática.
- Implementar guardrails, mecanismos de auditoria e arquitetura transparente.
- Garantir código limpo, seguro e documentado.

## Principais Funcionalidades

- **Cálculo e visualização de métricas-chave:**
  - Taxa de aumento de casos
  - Taxa de mortalidade
  - Taxa de ocupação de UTI
  - Cobertura vacinal COVID-19 e Gripe
- **Gráficos dinâmicos:**
  - Casos diários (últimos 30 dias)
  - Casos mensais (últimos 12 meses)
- **Resumo executivo automático:**
  - Gerado por agente de IA, combinando métricas, tendências e notícias
- **Integração com notícias em tempo real:**
  - Busca e exibição das 3 notícias mais relevantes sobre SRAG no Brasil
- **Perguntas livres ao agente:**
  - Respostas dinâmicas baseadas em dados, explicações e contexto epidemiológico
- **Guardrails e auditoria:**
  - Validação de perguntas, logs estruturados e workflow seguro

## Como a Solução Atende aos Requisitos do Desafio

| Requisito                              | Como foi atendido                                                                                              |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Consultar banco de dados               | O agente utiliza ferramentas (tools) SQL seguras para consultar e calcular métricas a partir do SQLite local. |
| Apresentar métricas essenciais         | Todas as métricas solicitadas (aumento, mortalidade, UTI, vacinação) estão implementadas e exibidas no painel. |
| Gerar gráficos                        | Dois gráficos (casos diários e mensais) são gerados dinamicamente com matplotlib/Streamlit.                   |
| Integrar notícias em tempo real        | Integração com Tavily API para busca e exibição das notícias mais relevantes sobre SRAG.                      |
| Gerar explicações                      | O agente utiliza LLM para gerar explicações e sumarizações, contextualizando com dados e notícias.            |
| Tratamento de dados sensíveis          | Variáveis sensíveis são gerenciadas via Pydantic Settings e nunca ficam hardcoded.                            |
| Guardrails                             | Validação de escopo e segurança em todas as entradas do agente (blocklist SQL, escopo epidemiológico).        |
| Governança e transparência             | Logs estruturados, workflow auditável e código aberto/documentado.                                            |
| Clean code/documentação                | Código padronizado, docstrings e comentários em inglês, UI em português, organização modular.                 |

## Arquitetura da Solução

- **Orquestração por LangGraph:**
  - O agente é implementado como um workflow modular com múltiplos nós (SQL, sumarização, explicação, roteamento, notícias).
  - Cada nó executa uma função/tool específica, garantindo flexibilidade e escalabilidade.
- **Ferramentas (Tools):**
  - Consulta SQL segura ao banco (apenas SELECT e tabelas whitelisted).
  - Busca de notícias via Tavily API.
  - Geração de resumo executivo e explicações com LLM (OpenAI).
- **Fluxo de Decisão:**
  - O agente roteia perguntas para nós apropriados (SQL, explicação, sumarização) conforme o tipo de solicitação.
  - Guardrails bloqueiam perguntas inseguras ou fora do escopo.
- **Painel Streamlit:**
  - Interface interativa para exibição de métricas, gráficos, notícias, resumo e perguntas livres ao agente.

Veja o diagrama conceitual em `docs/README_DIAGRAM.pdf` para detalhes visuais da arquitetura e interações.

## pipeline-de-dados-e-qualidade

- **Fonte:** Dados reais do Open DATASUS (hospitalizações por SRAG).
- **Formato:** CSV (~100 colunas, 165.000 linhas).
- **Scripts de ETL:**
  - `scripts/data_quality_check.py` — Checagem e limpeza dos dados, tratamento de valores ausentes/inválidos.
  - Conversão de datas, padronização de valores "Ignorado", seleção de colunas relevantes.
- **Banco de Dados:**
  - SQLite populado automaticamente após ETL.
- **Dicionário de Dados:**
  - Arquivo JSON limpo usado para validação dinâmica de queries e prompts do agente.

## Segurança, Governança e Auditoria

- **Variáveis sensíveis:**
  - Gerenciadas via Pydantic Settings e `.env` (nunca hardcoded).
- **Guardrails:**
  - Blocklist explícita para termos perigosos em SQL.
  - Validação de escopo via LLM para restringir perguntas ao contexto epidemiológico.
- **Auditoria:**
  - Logging estruturado das decisões do agente e workflow.
  - Todos os fluxos e transições são rastreáveis.

## Testes

- **Testes unitários abrangentes:**
  - Funções de métricas, transformação de dados, ETL e validação.
  - Cobertura de edge cases e cenários reais.
  - Testes localizados em `tests/` (ex: `test_metrics_queries.py`, `test_load_data.py`, `test_data_quality_check.py`).

## Instalação e Execução

```bash
make setup

make app

make etl

make test
```

Esses comandos:
- Criam o ambiente virtual
- Ativam e sincronizam as dependências automaticamente
- Executam o painel localmente
- Executam o pipeline de checagem, limpeza e atualização do banco de dados
- Executam todos os testes unitários localizados em `tests/`

## Configuração de variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
OPENAI_API_KEY=sua-api-key-openai
TAVILY_API_KEY=sua-api-key-tavily
```

Veja `.env.example` para referência.

## Estrutura dos Principais Arquivos

- `report/app.py` — Código principal do painel Streamlit
- `metrics/queries.py` — Funções de métricas e queries SQL
- `agent/langgraph_agent.py` — Orquestração do agente IA (LangGraph)
- `agent/news_tool.py` — Tool para busca de notícias (Tavily)
- `report/agent_summary.py` — Geração do resumo executivo pelo agente
- `database/srag_database.db` — Banco de dados SQLite populado via ETL
- `scripts/data_quality_check.py` — Checagem de qualidade dos dados

## Entrega e Documentação

- **Este repositório público contém:**
  - Código-fonte completo e organizado.
  - Documentação detalhada neste README.md.
  - PDF do diagrama conceitual da arquitetura em `docs/README_DIAGRAM.pdf`.


**Posso rodar sem a chave do OpenAI?**
- Não. O agente depende do LLM da OpenAI para sumarização e respostas.


## Licença

MPL 2.0. Veja LICENSE.

---

Indicium HealthCare Inc. — Projeto PoC SRAG
