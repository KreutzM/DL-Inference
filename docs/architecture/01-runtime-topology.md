# Runtime Topology

Suggested default request flow:

1. client sends a request to the public API
2. gateway authenticates and normalizes the request
3. gateway chooses the configured assistant profile
4. gateway invokes the RAG API when retrieval is enabled for that assistant
5. RAG API retrieves evidence from the local vector store
6. gateway assembles the final prompt with assistant instructions and retrieved evidence
7. gateway forwards the final prompt to OpenRouter
8. response returns with citation metadata derived from retrieved sources
