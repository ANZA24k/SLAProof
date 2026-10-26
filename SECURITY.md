# SLAProof security

**Unaudited prototype. No custody of GEN or any other token.** Notional settlement receipts do not make on-chain payments or create an enforceable escrow. No funds can be trapped; an external agreement must settle real credits.

- Input URLs must be canonical HTTPS GitHub raw content pinned to 40 lowercase hexadecimal commit characters, without query strings, fragments, userinfo, ports, encoded path or traversal. The host is fixed, not supplied.
- Each response has an exact length and SHA-256 commitment verified **before** UTF-8 decoding. Duplicate JSON keys, replay manifests and unknown fields are rejected. Maximum 16 KiB per document, 32 KiB total, at most 3 descriptors (one per kind), 12 incidents, 8 maintenance windows, 8 exclusion codes and 3 versions. The network might fetch more data before the post-download size check.
- SLA terms cannot be edited; claimant authorization, period, deadline, exclusion codes, maintenance overlaps, numeric limits, payout math, digest, and receipt calculations are deterministic.
- The LLM is asked only for allowed incident IDs, never payment sums, thresholds, URLs or instructions. Evidence text is explicitly untrusted. Each validator independently re-fetches and repeats inference. Correlated model mistakes can still occur.
- 4xx/unavailable or corrupt evidence produces INCONCLUSIVE. 5xx, 429 or transport errors revert without committing a verdict, so retrieval can be retried.
- Service reports may lie. Source hashes establish **bytes**, not independently verified publisher authority, measurements, actual p95 request samples or incident truth. The demo is expressly synthetic.
- Only Full Consensus finalized successful transactions prove deployed behavior. Direct Mode and mocked tests cannot establish that. Subsequent undisputed revisions are locked out; inconclusive revisions can be retried within caps and deadline.
- Settling twice reverts. At expiry unresolved agreements revert 100% of **notional credit units** to provider; nothing is transferred.

Report security issues privately to the repository owner.
