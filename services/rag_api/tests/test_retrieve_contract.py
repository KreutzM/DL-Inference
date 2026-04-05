from fastapi.testclient import TestClient

from services.rag_api.app.main import app


def test_retrieve_contract() -> None:
    client = TestClient(app)
    response = client.post(
        "/retrieve",
        json={
            "query": "How do I reset settings in JAWS?",
            "assistant": "jaws-support",
            "knowledge_base": "jaws",
            "top_k": 3,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == []
    assert payload["meta"]["status"] == "placeholder"
    assert payload["meta"]["assistant"] == "jaws-support"
