# SLAProof submission

**Project:** SLAProof

**One-line description:** Independently verify locked SLA uptime, latency and incident exclusions with GenLayer consensus.

**Recommended tags:** #SourceVerification #EvidenceAssessment #VerifiableInference #DisputeResolution

**Long description:** SLAProof is a standalone GenLayer Intelligent Contract for service-level agreement verification. Providers immutably lock measurement periods, uptime thresholds, p95 latency targets, maintenance windows, permitted exclusions and deterministic service-credit rules. Claimants commit immutable public monitoring and incident reports by SHA-256, byte length and GitHub commit pin. Validators independently retrieve evidence and judge the validity of ambiguous exclusions. Deterministic rules derive MET, PARTIAL, BREACHED or INCONCLUSIVE and append hash-linked assessment history. Replay protection, evidence caps, permissionless evaluation and one-time non-custodial accounting support a verifiable dispute workflow. The fixture is synthetic, not production uptime.

**Live verification:** Stable Studionet Full Consensus completed with all five transactions FINALIZED and MAJORITY_AGREE. Verified outcome PARTIAL on clearly synthetic service evidence (uptime 99.72% against 99.90% target; p95 220 ms). Settlement stores a non-custodial credit receipt of 150,000 units for claimant, 850,000 for provider. Deployed contract, decision hash and transaction links: [LIVE_EVIDENCE.md](LIVE_EVIDENCE.md).

**Notes / Description (under 1000 characters):**

SLAProof locks SLA uptime, latency, maintenance, incident exclusions, deadlines and notional credit rules. Claimants submit SHA-256/byte-length commitments to public commit-pinned reports. GenLayer validators independently re-fetch evidence and semantically review outage exclusions; deterministic rules return MET, PARTIAL, BREACHED or INCONCLUSIVE. Live stable Studionet Full Consensus finalized PARTIAL on a synthetic fixture: uptime 99.72% vs 99.90% required, p95 220ms vs 250ms; validators did not accept the claimed upstream exclusion. Five transactions finalized MAJORITY_AGREE, including one-time settlement: 150,000 claimant and 850,000 provider non-custodial units. No GEN transferred. Includes replay protection, bounded evidence, hash-linked decisions, 14 passing tests and GenVM lint. Explorer and all receipts in docs/LIVE_EVIDENCE.md.
