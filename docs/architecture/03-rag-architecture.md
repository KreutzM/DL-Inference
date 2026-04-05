# RAG Architecture

The MVP RAG slice uses:

- one knowledge base
- deterministic local hash embeddings
- Qdrant as the vector store
- simple chunking plus top-k semantic retrieval
- stable, repo-relative source and citation payloads for later gateway wiring

Reranking and broader orchestration remain out of MVP scope.
