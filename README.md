```mermaid
flowchart TD
    %% FRONTEND
    A[Frontend<br/>- Formulários (14)<br/>- Dashboard<br/>- HTML/CSS/JS] --> B[Routes]

    %% ROUTES -> CONTROLLERS
    B --> C[Candidatos Controller]
    B --> D[Vagas Controller]
    B --> E[PDF Controller]

    %% CONTROLLERS -> VALIDATORS
    C --> F[Candidato Validator]
    D --> G[Vaga Validator]

    %% CONTROLLERS -> SERVICES
    C --> H[Candidato Service]
    D --> I[Vaga Service]
    E --> J[PDF Service]

    %% SERVICES -> MODEL
    H --> K[Candidato Model]
    I --> L[Vaga Model]
    J --> K
    J --> L

    %% MODEL -> DATABASE
    K --> M[(Postgres DB<br/>Tabela candidatos<br/>- universais<br/>- dados_especificos JSONB<br/>- tipo_formulario)]
    L --> N[(Postgres DB<br/>Tabela vagas<br/>- universais<br/>- dados_especificos JSONB<br/>- tipo_formulario)]

    %% PDF MODULE DETAILS
    J --> O[Templates HTML<br/>caseiro, arrumadeira, etc]
    O --> P[Puppeteer Renderer]
    P --> A

    %% CASAL TABLE
    C --> Q[Candidato Casal Service]
    Q --> R[Candidato Casal Model]
    R --> S[(Postgres DB<br/>casal_candidatos<br/>pessoa1 JSONB<br/>pessoa2 JSONB)]
```
