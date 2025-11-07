flowchart TD

A[Frontend: Formulários + Dashboard] --> B[Routes]

B --> C[Controllers]

C --> D[Validators]
C --> E[Services]

D --> E

E --> F[Models]
E --> P[PDF Module]

F --> G[(Postgres: candidatos, vagas, casal, JSONB)]

P --> H[Templates HTML]
H --> I[Puppeteer Renderer]
I --> A

A -->|GET /:id/pdf| B
