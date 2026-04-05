# RAG API agent notes

This subtree owns the repo-managed retrieval service.

## Canonical import path

Use `services.rag_api...` imports.
Do not use `services.rag_api_pkg...`.
Do not create new code under `services/rag-api`.

## Expectations

- Keep request and response contracts explicit.
- Keep placeholder behavior honest.
- Prefer config-backed metadata over hidden defaults.
- Update smoke tests when endpoint contracts change.
