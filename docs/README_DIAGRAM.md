# Arquitetura do SRAG HealthCare Agent

**Padrão adotado: Tool Use Pattern (Orquestração de Ferramentas com LangGraph/LangChain)**

Esta arquitetura segue o padrão moderno de orquestração de agentes, no qual um agente principal (orquestrador) utiliza ferramentas especializadas (Tools) para executar tarefas complexas, delegando consultas a banco de dados, busca de notícias, sumarização ou explicação a módulos dedicados. O fluxo e as decisões são controlados por um grafo de estados (LangGraph), permitindo modularidade, rastreabilidade e fácil expansão.

**Por que foi utilizada?**

- Permite separar claramente responsabilidades: o agente decide, as ferramentas executam.
- Facilita a integração de múltiplas fontes de dados (banco, LLM, web) de forma auditável.
- É escalável: novas ferramentas podem ser adicionadas sem reescrever o agente principal.
- O padrão é alinhado com as melhores práticas atuais em IA aplicada, garantindo robustez, segurança e transparência.
- O uso de LangGraph/LangChain permite logging, guardrails e auditoria de decisões, essenciais para aplicações sensíveis em saúde pública.

Este diretório contém o diagrama conceitual da arquitetura da solução.

## Visualização rápida

- Veja o diagrama em formato Mermaid: [`architecture.mmd`](architecture.mmd)
- Você pode visualizar diretamente em [Mermaid Live Editor](https://mermaid.live/) ou no VSCode com extensão Mermaid.

## Legenda e explicação

- O diagrama mostra:

    - O agente principal (orquestrador LangGraph)
    - As ferramentas (Tools) SQLQueryTool, NewsTool, SummaryTool
    - As interações com LLM, banco de dados e fontes de notícias
    - O fluxo do usuário até a resposta final