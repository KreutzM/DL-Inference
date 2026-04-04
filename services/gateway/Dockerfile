FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx pyyaml
COPY services/gateway /app/services/gateway
CMD ["uvicorn", "services.gateway_pkg.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
