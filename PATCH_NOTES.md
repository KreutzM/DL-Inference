# DL-Inference Codex prep patch

This overlay patch prepares the repo for a Codex CLI workflow with:

- `gpt-5.4-mini` as the default implementation model
- `gpt-5.4` for planning and review
- canonical service roots at `services/gateway` and `services/rag_api`
- explicit review-info output expectations after each Codex run

## After extracting

1. Overwrite existing files with this patch.
2. Delete the legacy paths listed in `DELETE_LIST.txt`.
3. Run:

```bash
python -m repo2ctl.cli lint
python -m repo2ctl.cli test
python -m repo2ctl.cli smoke
```
