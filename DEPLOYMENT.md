# StudioNet deployment and Full Consensus guide

1. Check GitHub Actions and the GenVM lint / Direct Mode tests for the exact source commit.
2. In [GenLayer Studio](https://studio.genlayer.com/), choose **stable StudioNet** and the built-in account selector (no external wallet, MetaMask or key export). Load `contracts/slaproof.py` from the pinned reviewed GitHub commit, deploy it **once** and capture its contract address, deployment tx, execution status and Explorer link.
3. With the provider Studio account, call `create_sla` using the README sample. Specify a *second* Studio account as claimant. Confirm `get_sla("SLADEMO001")` matches terms and has a stable `terms_hash`.
4. Switch to the claimant Studio account and call `submit_evidence("SLADEMO001", manifest)` with the **single canonical line** in `fixtures/manifest.json` (no trailing newline). Confirm `get_latest_revision` = 1 and verify `get_evidence` state.
5. Submit `evaluate("SLADEMO001", 1)` with **Full Consensus** enabled, not leader-only. Capture transaction hash, Explorer view, finalization/execution status and `get_assessment` verdict/decision hash. If consensus disagrees or fails, do not label it successful.
6. For a decisive result call `settle("SLADEMO001")`, verify `get_settlement`, total-credit conservation and duplicate settlement rejection. An INCONCLUSIVE case can revise evidence up to deadline, then settle after expiry.
7. Record verified source SHA-256, deployed commit, contract address, Explorer tx links and exact readback in `docs/LIVE_EVIDENCE.md`. A docs-only follow-up commit must not change deployed contract bytes.

The historical demo's evidence deadline is 2026-11-01. After expiry, publish a **new pinned fixture** and lock a new period; never overwrite the old commit.

Source APIs: [Studio](https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio), [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [GenLayer Testing](https://docs.genlayer.com/api-references/genlayer-test).

## Verified stable deployment

The canonical contract is deployed at [`0x1Fd460A508CD3bFbc99f38b28b7482169B0aBA78`](https://explorer-studio.genlayer.com/address/0x1Fd460A508CD3bFbc99f38b28b7482169B0aBA78), source SHA-256 `e88de453e664d4641f00a428bb15f189443370605a4e9ade3d06e86e332318a5`. Verified Full Consensus yielded `PARTIAL` (synthetic fixture), and one-time settlement completed. All finalized tx, decision hash and readback are in [LIVE_EVIDENCE.md](docs/LIVE_EVIDENCE.md). **Do not redeploy this unchanged source.**
