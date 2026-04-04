FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir fastapi uvicorn pydantic pyyaml qdrant-client
COPY services/rag-api /app/services/rag-api
CMD ["uvicorn", "services.rag_api_pkg.app.main:app", "--host", "0.0.0.0", "--port", "8010"]
