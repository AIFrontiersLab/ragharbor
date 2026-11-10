# CLI

```text
python -m answer_or_abstain_rag [--config PROFILE.toml] <command>

run [REQUEST.json|-] [--corpus CORPUS.json]   execute one request
serve [--host H] [--port P]                   start the HTTP server
describe                                      print stage topology
config                                        print effective configuration
doctor                                        run readiness checks (exit 2 on failure)
```

Errors are printed to stderr as JSON and exit with status 2.
