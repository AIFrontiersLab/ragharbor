# Containers (C4 level 2)

| Container | Technology | Notes |
|---|---|---|
| API process | Python WSGI (`wsgiref` locally, any WSGI server in production) | Stateless; horizontal scaling via replicas |
| Run store | In-memory or JSON Lines | Swap for a transactional database behind `RunRepository` |
| Audit store | JSON Lines | Append-only; hash-chain verification available |
| Corpus | In-memory | Swap for a search engine behind `CorpusRepository` |
| Cache | In-process TTL LRU | Swap for a shared cache behind `RankingCache` |
