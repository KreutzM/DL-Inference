def list_models() -> list[dict]:
    return [
        {"id": "local-default", "object": "model", "owned_by": "repo2"},
        {"id": "local-qwen", "object": "model", "owned_by": "repo2"},
    ]
