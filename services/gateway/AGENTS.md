# Gateway agent notes

This subtree owns the repo-managed OpenAI-compatible edge facade.

## Canonical import path

Use `services.gateway...` imports.
Do not use `services.gateway_pkg...`.

## Expectations

- Keep the external contract OpenAI-like.
- Prefer config-driven model discovery.
- Keep placeholder logic explicit rather than pretending to be complete.
- Update smoke tests when routes or contracts change.
