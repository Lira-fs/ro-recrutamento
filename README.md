```mermaid
flowchart TD

A[Frontend\n- Formulários (14)\n- Dashboard\n- HTML/CSS/JS] --> B[Routes]

B --> C[Controllers]

C --> D[Validators]
C --> E[Services]

D --> E

E --> F[Models]
E --> P[PDF Module]

F --> G[(Postgres DB\n- candidatos\n- vagas\n- casal\n- JSONB)]

P --> H[Templates HTML]
H --> I[Puppeteer]
I --> A

A -->|GET :id/pdf| B
