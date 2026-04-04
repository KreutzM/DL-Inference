from fastapi import FastAPI

app = FastAPI(title="Repo2 RAG API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-api"}


@app.post("/retrieve")
def retrieve() -> dict:
    return {"results": []}
