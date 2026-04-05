# Knowledge Bases

Document supported knowledge bases, collection mapping, metadata standards, and ingestion flows.

Current MVP source of truth:

- one runnable knowledge base named `mvp-one`
- ingest and retrieve are owned by `services/rag_api`
- the smoke path is documented in `docs/deployment/local-dev.md`
- retrieval returns `sources` and `citations` with `source_id`, `document_id`, `chunk_id`, `source`, `score`, `text`, and `metadata`
- the MVP embedder is a deterministic local hash embedder configured in `configs/rag/embeddings.yaml`
- `source` values are repo-relative paths, not host filesystem paths
