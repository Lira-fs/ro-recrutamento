                                       ┌───────────────────────────────┐
                                       │           FRONTEND             │
                                       │───────────────────────────────│
                                       │  • Formulários (14)           │
                                       │  • Dashboard                  │
                                       │  • HTML/CSS/JS                │
                                       └───────────────┬───────────────┘
                                                       │  HTTP Request
                                                       ▼
                             ┌────────────────────────────────────────────────┐
                             │                 BACKEND API                     │
                             │────────────────────────────────────────────────│
                             │                    ROUTES                      │
                             │  - /api/candidatos                             │
                             │  - /api/vagas                                  │
                             │  - /api/:id/pdf                                │
                             └───────────────┬────────────────────────────────┘
                                             │ chama
                                             ▼
                        ┌────────────────────────────────────────────┐
                        │               CONTROLLERS                  │
                        │────────────────────────────────────────────│
                        │ - recebe req/res                           │
                        │ - chama validator                          │
                        │ - chama service                            │
                        └───────────────┬────────────────────────────┘
                                        │ valida entrada
                                        ▼
                           ┌───────────────────────────────────┐
                           │            VALIDATORS             │
                           │───────────────────────────────────│
                           │ - Zod/Yup                         │
                           │ - valida formatos                 │
                           └──────────────┬────────────────────┘
                                          │ envia data limpo
                                          ▼
                   ┌──────────────────────────────────────────────────────────┐
                   │                          SERVICES                        │
                   │──────────────────────────────────────────────────────────│
                   │ - regras de negócio                                      │
                   │ - extrai dados universais                                │
                   │ - extrai dados específicos                               │
                   │ - chama model                                            │
                   │ - chama módulo PDF                                       │
                   └───────────────┬──────────────────────────────────────────┘
                                   │ executa regras
                                   ▼
                     ┌────────────────────────────────────────────────┐
                     │                    MODELS                      │
                     │────────────────────────────────────────────────│
                     │ - faz SELECT, INSERT, UPDATE, DELETE           │
                     │ - queries SQL + JSONB                          │
                     └──────────────┬─────────────────────────────────┘
                                    │ queries SQL
                                    ▼
        ┌──────────────────────────────────────────────────────────────────────────────┐
        │                                POSTGRES (DB)                                 │
        │──────────────────────────────────────────────────────────────────────────────│
        │  TABELAS:                                                                    │
        │   • candidatos                                                               │
        │       - universais (colunas)                                                 │
        │       - dados_especificos JSONB                                               │
        │       - tipo_formulario                                                       │
        │                                                                               │
        │   • vagas                                                                     │
        │       - universais (colunas)                                                  │
        │       - dados_especificos JSONB                                               │
        │       - tipo_formulario                                                       │
        │                                                                               │
        │   • casal_candidatos                                                          │
        │       - pessoa1 JSONB                                                         │
        │       - pessoa2 JSONB                                                         │
        │                                                                               │
        └──────────────────────────────────────────────────────────────────────────────┘


                                         PDF FLOW
                                         ────────
Dashboard → GET /api/candidatos/:id/pdf → Controller → Service → PDF Module →
Template HTML → Puppeteer → PDF final → Return to Dashboard
