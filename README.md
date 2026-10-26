# SLAProof

**Standalone GenLayer Intelligent Contract** that verifies locked service-level uptime, p95 latency, maintenance and incident exclusions from immutable public monitoring evidence. No frontend, backend, MetaMask, wallet connector, authentication service, database or token escrow.

## How it works

1. The **provider** calls `create_sla` once, locking an SLA ID, claimant, service, UTC Unix measurement start/end, evidence deadline, minimum uptime in basis points, maximum p95 latency in integer milliseconds, approved non-overlapping maintenance windows, incident exclusion codes and a notional service-credit schedule.
2. The **claimant** submits one exact canonical JSON evidence manifest via `submit_evidence`. Each source must be a public `https://raw.githubusercontent.com/OWNER/REPO/40-char-lowercase-commit/path` URL, with SHA-256 hex digest and exact byte length. Monitoring is required; a separate incident report is needed when incidents are present.
3. Any account calls `evaluate(sla_id, revision)`. A GenLayer leader retrieves and verifies bytes, parses strict reports and uses semantic inference only to decide which pre-authorized exclusion candidates are truly supported. **Validators independently re-fetch sources and repeat the interpretation**, checking the decision-bearing fields. Deterministic uptime/latency logic yields MET, PARTIAL, BREACHED or INCONCLUSIVE; every accepted assessment gets a deterministic decision hash and an append-only previous-hash pointer. Transport/5xx failures are retryable, not permanent evidence failures.
4. After an accepted inconclusive outcome, the claimant may submit a revised nonce/manifest, up to three revisions. A decisive assessment precludes further revisions.
5. Anyone can call `settle` exactly once after a decisive result, or after the deadline if still inconclusive. Accounting is strictly **non-custodial**: no GEN is deposited, held, transferred or refunded. Locked notional units are assigned to claimant and provider.

## Verdict and accounting

- **MET**: verified full coverage, uptime >= locked minimum AND p95 latency <= locked limit.
- **PARTIAL**: exactly one requirement misses, within the non-severe margin.
- **BREACHED**: both miss, OR uptime is more than 100 bps below minimum, OR latency is over 125% of the limit.
- **INCONCLUSIVE**: missing/invalid evidence, mismatching hashes or byte counts, unsupported schemas, coverage gaps or semantic uncertainty.

Outages are non-overlapping bounded intervals. Approved maintenance intersections and independently accepted whole-incident exclusions are deducted without double-counting. Uptime basis points = floor((period - unexcused_outage_seconds)*10000/period). Monitoring must assert exactly full-period coverage; p95 is the pinned report's declared measurement rather than a reconstruction from raw samples.

Claimant credit units = floor(locked_pool * eligible_credit_bps / 10000), where the rate is 0 for MET/expired INCONCLUSIVE, locked partial rate for PARTIAL and locked breach rate for BREACHED. Provider remaining units = pool - claimant credits. This records an **off-chain obligation**, not enforceable on-chain transfers.

## Synthetic fixture demonstration

The checked-in reports are **fictional**, not production service measurements. The public commit-pinned source URLs and hashes are in `docs/LIVE_EVIDENCE.md` and one-line `fixtures/manifest.json`. The measurement spans UTC 2026-10-01 through 2026-10-02 (Unix 1790812800 to 1790899200). The deadline is Unix 1793491200.

Demo call: `create_sla("SLADEMO001", "demo-api", "<different built-in Studio account address>", 1790812800, 1790899200, 1793491200, 9990, 250, "[]", "[\"UPSTREAM_FAILURE\"]", 1000000, 1500, 4000)`

Then the locked claimant submits the **single line of manifest JSON with the final newline removed**, and any account runs `evaluate("SLADEMO001",1)` under **Full Consensus**, not leader-only. A 180-second simulated upstream exclusion and 60-second service error imply conditional uptime **9993 bps** and measured p95 **220ms**. If validators accept the exclusion, the deterministic result is **MET**. No live outcome is claimed until Explorer finalization and chain readback.

## Quality verification

Python 3.12+:

```bash
pip install -r requirements.txt
genvm-lint check contracts/slaproof.py
python -m pytest -q tests/test_offline.py tests/test_direct.py
```

`tests/test_offline.py` is an isolated deterministic mock harness and **not** GenVM or Full Consensus proof. `tests/test_direct.py` uses official GenLayer Direct Mode. Review the published GitHub Actions status, `SECURITY.md`, `DEPLOYMENT.md`, and `docs/SUBMISSION.md`.

Official references: [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [Web Access](https://docs.genlayer.com/developers/intelligent-contracts/features/web-access), [Storage](https://docs.genlayer.com/developers/intelligent-contracts/storage), [GenVM Linter](https://docs.genlayer.com/api-references/genlayer-linter), [GenLayer Testing](https://docs.genlayer.com/api-references/genlayer-test).
