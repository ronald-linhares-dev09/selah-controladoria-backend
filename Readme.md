## Selah
Sistema de prestação e gestão de consultorias financeiras baseado em um diagnóstico empresarial fornecido por um questionário estratégico. Cada questionário é composto por 7 pilares, que representam áreas específicas de uma empresa, que possuem blocos de perguntas principais - essenciais para o diagnóstico e perguntas validações - auxiliam validar a pergunta principal. O diagnóstico é feito através de indicadores que analisam a maturidade de cada setor empresarial e o nível de conexões entre cada setor da empresa.
O sistema também conta com um CRM, para que o consultor consiga gerenciar os contratos ativos, bem como verificar as receitas geradas e as projetadas para um dado período.

## Stacks
- **Back-End :** FastApi + Pandas - Python (3.11.6)
- **Banco de Dados :** PostgreSQL
- **Deploy :** Railway (backend)

## Funcionalidades 
- PDF com diagnóstico empresarial baseado nos indicadores de maturidade e de conexões, com acréscimo da conclusão do consultor
- Diagnóstico delimitado por uma Análise dos Indicadores identificando possíveis setores fragilizados e setores com bom desenvolvimento
- Planilha Excel com perguntas e respostas de validação segregadas pelo bloco e pilar a que pertencem
- Dashboards que informam : 
   Receita projetada para 6 meses com bases no contratos ativos 
   Categorização dos clientes 
   Receita Gerada por cada Cliente
- Cadastro e Pipeline de Clientes com categorização em :
  Prospecção - apenas cadastro realizado
  Em Negociação - cadastro realizado e reunião agendada
  Diagnóstico - questionário respondido e contrato em aberto
  Contratado - contrato fechado
- Cadastro de Contratos e Pipeline de Contratos - informando o valor contratado e a validade do contrato

## Como Rodar Localmente

Copie `.env.example` para o `.env` de cada setor - frontend + backend - e preencha :

| Variável | Importância | O que é |
| -------- | --------- | ------- |
| `URL_SUPABASE` | essencial | URL utilizada para consultar o banco |
| `SERVICE_ROLE_KEY` | essencial | Chave de serviço utilizada para habilitar operações no banco de dados |


**Pré-Requisitos** : Python (3.11.6), Projeto Ativo no SUPABASE


````bash
git clone https://github.com/ronald-linhares-dev09/selah-controladoria-backend.git
cd selah-controladoria-backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload

````

## Arquitetura
````mermaid
graph LR
    A[BROWSER] -->|1. login| B[Supabase auth]
    A -->|2. JWT| C[FastAPI API]
    C -->|3. SERVICE KEY| D[(Supabase - PostgreSQL)]
````

````
app/
├── routers/     # rotas - delimitadas por cada entidade presente no banco, apontam para qual operação realizar
├── schemas/     # validação de dados recebidos ou enviados - categorizados por entidade
└── core/        # autenticação e extração do uuid de usuário
````

## Decisões Técnicas

**CPF com constraint UNIQUE e uuid do Cliente como FK nas tabelas contratos e questionários** A restrição garante que haverá CPF´s únicos por cliente, o que torna essa coluna uma chave candidata, e as tabelas contratos e questionários apresentam agora uma ligação concreta com a tabela clientes através do uuid. ([ADR 0001](docs/adr/0001-ligacoes-por-cliente.md))

**Versionamento das Rotas e Partição em Camadas** Cada rota foi divida em camadas separadas por tipo de entidade, bem como os schemas utilizados. Essa divisão e o versionamento facilitam alterações e ajustes nos endpoints de forma ágil, bastando apenas após a alteração incluir a nova versão com include_router no app do FastAPI. ([ADR 0002](docs/adr/0002-versionamento-api.md)) 

**RLS habilitado nas tabelas** Dessa forma, o banco de dados só será acessado via backend, já que o RLS bloqueia requisições com a chave pública, ou seja, os dados são protegidos em duas frentes : validação de JWT no backend e RLS no Banco. ([ADR 0003](docs/adr/0003-habilitar-rls.md))










