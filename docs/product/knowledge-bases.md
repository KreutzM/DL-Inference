# Knowledge Bases

Document supported knowledge bases, collection mapping, metadata standards, and ingestion flows.

Current MVP source of truth:

- one runnable knowledge base named `mvp-one`
- ingest and retrieve are owned by `services/rag_api`
- the smoke path is documented in `docs/deployment/local-dev.md`
- retrieval returns `sources` and `citations` with `source_id`, `document_id`, `chunk_id`, `source`, `score`, `text`, and `metadata`
