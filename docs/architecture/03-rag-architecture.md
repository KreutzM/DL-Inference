# RAG Architecture

The MVP RAG slice uses:

- one knowledge base
- local embeddings
- Qdrant as the vector store
- simple chunking plus top-k semantic retrieval
- stable source and citation payloads for later gateway wiring

Reranking and broader orchestration remain out of MVP scope.
