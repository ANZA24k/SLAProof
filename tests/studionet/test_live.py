"""One-shot public Studionet deployment + Full Consensus trace.

Run only from .github/workflows/studionet-once.yml.
No secrets, external wallet connectors, or native GEN escrow.
Never invent transaction hashes or finality.
"""
import hashlib
import json
from pathlib import Path

from gltest import get_contract_factory, get_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

EXPLORER = "https://explorer-studio.genlayer.com"
CONTRACT = Path("contracts/slaproof.py")
EVIDENCE = Path("fixtures/manifest.json")
PINNED_SHA256 = "e88de453e664d4641f00a428bb15f189443370605a4e9ade3d06e86e332318a5"


def _print_receipt(stage, receipt):
    # Never print private account keys. Receipts are public chain data.
    data = {"hash": receipt.get("hash"), "status_name": receipt.get("status_name"), "result_name": receipt.get("result_name"), "leader_only": receipt.get("leader_only")}
    leaders = receipt.get("consensus_data", {}).get("leader_receipt", [])
    errors = [x.get("genvm_result", {}).get("stderr", "") for x in leaders if x.get("genvm_result", {}).get("stderr", "")]
    if errors:
        data["leader_errors"] = [error[:5000] for error in errors]
    print("SLA_PROOF_RECEIPT", stage, json.dumps(data, default=str), flush=True)


def _assert_chain_success(stage, receipt):
    _print_receipt(stage, receipt)
    assert tx_execution_succeeded(receipt), "Not a successful finalized " + stage


def _write(call):
    return call.transact(
        consensus_max_rotations=3,
        wait_transaction_status=TransactionStatus.FINALIZED,
        wait_interval=4000,
        wait_retries=90,
    )


def test_live_studionet_full_consensus():
    original = CONTRACT.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    print("SLA_PROOF_SOURCE_SHA256", digest, flush=True)
    assert digest == PINNED_SHA256, "Source differs from reviewed lint/test hash"

    accounts = get_accounts()
    assert len(accounts) >= 2, "Studionet SDK needs two configured built-in test accounts"
    provider, claimant = accounts[0], accounts[1]
    print("SLA_PROOF_PROVIDER", provider.address, flush=True)
    print("SLA_PROOF_CLAIMANT", claimant.address, flush=True)

    factory = get_contract_factory(contract_file_path="slaproof.py")
    deployment = factory.deploy_contract_tx(
        account=provider,
        consensus_max_rotations=3,
        wait_transaction_status=TransactionStatus.FINALIZED,
        wait_interval=4000,
        wait_retries=90,
    )
    _assert_chain_success("DEPLOY", deployment)
    address = extract_contract_address(deployment)
    print("SLA_PROOF_CONTRACT", address, flush=True)
    print("SLA_PROOF_EXPLORER", EXPLORER + "/address/" + str(address), flush=True)

    contract = factory.build_contract(address, account=provider)
    claimant_contract = contract.connect(claimant)

    created = _write(contract.create_sla(args=[
        "SLADEMO001", "demo-api", claimant.address,
        1790812800, 1790899200, 1793491200,
        9990, 250, "[]", '["UPSTREAM_FAILURE"]',
        1000000, 1500, 4000,
    ]))
    _assert_chain_success("CREATE", created)
    print("SLA_PROOF_TERMS", json.dumps(contract.get_sla(args=["SLADEMO001"]).call(), default=str), flush=True)

    evidence = EVIDENCE.read_text(encoding="utf-8").rstrip("\n")
    assert json.dumps(json.loads(evidence), sort_keys=True, separators=(",", ":")) == evidence
    submitted = _write(claimant_contract.submit_evidence(args=["SLADEMO001", evidence]))
    _assert_chain_success("SUBMIT", submitted)
    print("SLA_PROOF_REVISION", contract.get_latest_revision(args=["SLADEMO001"]).call(), flush=True)

    evaluated = _write(contract.evaluate(args=["SLADEMO001", 1]))
    _assert_chain_success("FULL_CONSENSUS_EVALUATION", evaluated)
    decision = contract.get_assessment(args=["SLADEMO001", 1]).call()
    print("SLA_PROOF_FINAL_ASSESSMENT", json.dumps(decision, sort_keys=True, default=str), flush=True)

    if decision["outcome"] in ("MET", "PARTIAL", "BREACHED"):
        settled = _write(contract.settle(args=["SLADEMO001"]))
        _assert_chain_success("SETTLEMENT", settled)
        state = contract.get_settlement(args=["SLADEMO001"]).call()
        print("SLA_PROOF_FINAL_ACCOUNTING", json.dumps(state, sort_keys=True, default=str), flush=True)
        assert state["claimant_credit_units"] + state["provider_remaining_units"] == state["total_units"]
        assert state["non_custodial"] is True
    else:
        print("SLA_PROOF_SETTLEMENT_SKIPPED_INCONCLUSIVE", flush=True)
