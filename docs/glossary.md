# Glossary

| Term | Meaning |
|---|---|
| Candidate | A document considered as evidence for an answer. |
| Prior score | Score assigned upstream before this pipeline ran. |
| Clearance | Ordered sensitivity level: public < internal < confidential < restricted. |
| Abstain | Return no answer, with an explicit reason. |
| Degraded | A non-critical stage failed and the run continued. |
| Fail closed | On failure, deny rather than allow. |
| Port | Protocol the core depends on. |
| Adapter | Concrete implementation of a port, or a driver of the core. |
| Stage | One strategy in the pipeline with a `process(ctx)` method. |
| Role | The behavioural category a stage implements. |
