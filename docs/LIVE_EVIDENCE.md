# SLAProof — verified stable Studionet evidence

> **Successful Full Consensus demonstration, 26 October 2026.** All five live transactions below returned **FINALIZED / MAJORITY_AGREE**, with **leader_only=false**. Verified using the GenLayer testing SDK's actual finalized transaction receipts and on-chain state-read responses. No production service performance is claimed: the underlying data is synthetic.

## Canonical deployment

- **Network:** Stable GenLayer Studionet, chain ID 61999, RPC `https://studio.genlayer.com/api`.
- **Contract:** `0x1Fd460A508CD3bFbc99f38b28b7482169B0aBA78`
- **Explorer:** https://explorer-studio.genlayer.com/address/0x1Fd460A508CD3bFbc99f38b28b7482169B0aBA78
- **Deployed GitHub commit:** `fdea88dc977247e60b4eb308ffbccd2574b1c955`
- **Canonical `contracts/slaproof.py` SHA-256:** `e88de453e664d4641f00a428bb15f189443370605a4e9ade3d06e86e332318a5`
- **Provider Studio SDK account:** `0xB4279d6C4b9677Cf59134e1bCC6E01ecb59f607C`
- **Claimant Studio SDK account:** `0x7373B2B3E0fB6f5B4e68732CA0Cc8720f512732D`
- **CI:** https://github.com/ANZA24k/SLAProof/actions/runs/40307351446 — GenVM lint/validation and 14 tests passed.
- **Full Consensus execution log:** https://github.com/ANZA24k/SLAProof/actions/runs/40307351443 — one successful end-to-end integration test (3m36s).

## Finalized transactions

| Step | Tx and Explorer | On-chain status | Consensus |
|---|---|---|---|
| Deploy canonical contract | [`0x9e6c963efe2cd5af4c37512bd2510c49f9de7deb58a6b651517ce259a547cb13`](https://explorer-studio.genlayer.com/tx/0x9e6c963efe2cd5af4c37512bd2510c49f9de7deb58a6b651517ce259a547cb13) | FINALIZED | MAJORITY_AGREE |
| Lock `SLADEMO001` | [`0x24e18d09208b2400e8f3e36e939bb8e08614ccb6b96c9b20f49006cb51d433b4`](https://explorer-studio.genlayer.com/tx/0x24e18d09208b2400e8f3e36e939bb8e08614ccb6b96c9b20f49006cb51d433b4) | FINALIZED | MAJORITY_AGREE |
| Claimant submits immutable evidence | [`0x7d1be334810edf5b7d2519c9c5a9277df4b04f3c62f6c2bfca108c9f28b38fba`](https://explorer-studio.genlayer.com/tx/0x7d1be334810edf5b7d2519c9c5a9277df4b04f3c62f6c2bfca108c9f28b38fba) | FINALIZED | MAJORITY_AGREE |
| Full Consensus `evaluate("SLADEMO001", 1)` | [`0x9a3963204750a0f3d183c3a350ba2b1ffde099dbdbadb7a8894126a6c38f9b23`](https://explorer-studio.genlayer.com/tx/0x9a3963204750a0f3d183c3a350ba2b1ffde099dbdbadb7a8894126a6c38f9b23) | FINALIZED | MAJORITY_AGREE |
| One-time settlement | [`0x59000630d20dcc8ce983efbb413b7d9df75c87e17521fb2069bc018db612cb82`](https://explorer-studio.genlayer.com/tx/0x59000630d20dcc8ce983efbb413b7d9df75c87e17521fb2069bc018db612cb82) | FINALIZED | MAJORITY_AGREE |

**Explorer URLs use the standard Studionet `/tx/<hash>` path.** The finalized status and chain readbacks were verified directly from the official StudioNet SDK; automated browser fetching of these Explorer pages was not available.

## Independent public fixture sources

The records are **synthetic**, not real monitoring of a production API, and pinned immutably to fixture GitHub commit `44e49926a411c56414892b1471fa13f4d961175a`.

- **Monitoring:** https://raw.githubusercontent.com/ANZA24k/SLAProof/44e49926a411c56414892b1471fa13f4d961175a/fixtures/monitoring.json — 316 bytes, SHA-256 `bef00e8b7732934dcb966984886c053c0f37528c26e269f216e9630fb35acf3b`
- **Incident report:** https://raw.githubusercontent.com/ANZA24k/SLAProof/44e49926a411c56414892b1471fa13f4d961175a/fixtures/incidents.json — 562 bytes, SHA-256 `53eeb524b8ef14e7afd745815663941fcab8faa0da9264dc147a746003bfb002`
- **Submitted canonical manifest:** `fixtures/manifest.json` (omit trailing newline), with recorded evidence commitment `40292a16535fd0885f153538f5ba290aef615dc0ef3aac9e895871e48544dae8`.

## Finalized SLA terms, verdict, decision hash

- SLA ID: `SLADEMO001`; service: `demo-api`.
- UTC measurement interval: 2026-10-01 00:00 to 2026-10-02 00:00; evidence deadline: 2026-11-01 00:00.
- Locked minimum uptime: **9990 basis points (99.90%)**; maximum p95 latency: **250 ms**.
- Allowed exclusion code: `UPSTREAM_FAILURE`; no maintenance window.
- Two monitored outages: 180 seconds upstream and 60 seconds service-side.
- **Independently accepted exclusion IDs: none**. Validators conservatively did not accept the upstream incident as exempt from the SLA.
- Counted downtime: **240 seconds**; exempted downtime: **0 seconds**.
- Assessed uptime: **9972 basis points (99.72%)**; assessed p95 latency: **220 ms**.
- **Final outcome: `PARTIAL`**. This is based on the live finalized chain assessment; it differs from the conditional `MET` result if the 180-second exclusion were accepted.
- Terms hash: `dfa6af499279133d1ed124a1d7f5f73804e78566006117fbcc2fc2043f60377e`.
- Deterministic decision hash: `559f8c172ffa538437265f5a5a79b93159e3bcb904b6694c2ea640f912575325`.
- Assessment revision: **1**; previous decision hash empty (first assessment).

## Finalized settlement state readback

| Field | Value |
|---|---|
| Result | `PARTIAL` |
| Locked accounting pool | **1,000,000 units** |
| Partial credit rate | **1,500 bps (15%)** |
| Claimant's recorded credit | **150,000 units** |
| Provider's remaining balance | **850,000 units** |
| Total after accounting | **1,000,000 units** |
| Settlement hash | `293cd4f4b00384ec7bb473a0087a183f9dfc33335034da24d4db1f1dd7140434` |
| Decision hash | `559f8c172ffa538437265f5a5a79b93159e3bcb904b6694c2ea640f912575325` |
| Non-custodial | `true` |

**No GEN is escrowed or disbursed.** These are contract-calculated, non-custodial service-credit accounting units requiring external voluntary settlement.

## Development trace and source fixes

Two earlier deployments successfully locked terms and submitted evidence, but their evaluation transactions finalized `MAJORITY_DISAGREE` from a GenVM response-field mismatch. Those earlier deployments are not the canonical submission. The actual runtime exposed `Response.status` rather than the `Response.status_code` used in some published examples. The final source fixes that API mismatch and is verified by a new official Direct Mode web/LLM/validator replay test plus the above successful real Full Consensus and settlement.
