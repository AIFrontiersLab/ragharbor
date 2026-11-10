# System context (C4 level 1)

```mermaid
flowchart LR
    user([Analyst / application]) -->|HTTP or library call| sys[Answer-or-Abstain RAG]
    approver([Approver]) -->|approve high-risk runs| sys
    sys -->|reads| corpus[(Document corpus)]
    sys -->|emits| mon[(Monitoring)]
    sys -->|writes| audit[(Audit store)]
```

| Actor | Interaction |
|---|---|
| Caller | Submits a query with a principal and optional pre-retrieved candidates |
| Approver | Releases runs that touch restricted material |
| Corpus | Supplies candidates when the caller sends none |
| Monitoring | Scrapes `/metrics`, consumes logs and traces |
