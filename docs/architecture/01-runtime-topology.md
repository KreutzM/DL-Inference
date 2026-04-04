# Runtime Topology

Suggested default request flow:

1. client sends a request to the public API
2. gateway authenticates and normalizes the request
3. gateway chooses local backend and assistant profile
4. assistant profile may invoke the RAG API
5. RAG API retrieves evidence from Qdrant
6. gateway forwards final prompt to inference backend
7. response returns with optional citations and metadata
