# Runtime Topology

Suggested MVP request flow:

1. client sends a request to the public API
2. gateway authenticates and normalizes the request
3. gateway chooses the configured assistant profile
4. assistant profile may invoke the RAG API
5. RAG API retrieves evidence from Qdrant
6. gateway forwards the final prompt to OpenRouter
7. response returns with optional citations and metadata

The MVP contract that constrains this flow is documented in `docs/product/mvp-contract.md`.
