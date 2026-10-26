"""Official genlayer-test Direct Mode smoke tests."""
START = 1790812800
END = 1790899200
CLOSE = END + 2592000

def arguments(bob):
    return ["DIRECT001", "demo-api", "0x" + bob.hex(), START, END, CLOSE,
            9990, 250, "[]", '["UPSTREAM_FAILURE"]', 1000000, 1500, 4000]

def test_create_read(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = direct_deploy("contracts/slaproof.py")
    direct_vm.sender = direct_alice
    c.create_sla(*arguments(direct_bob))
    record = c.get_sla("DIRECT001")
    assert record["uptime_min_bps"] == 9990
    assert record["service"] == "demo-api"
    assert len(record["terms_hash"]) == 64
    assert c.get_latest_revision("DIRECT001") == 0

def test_duplicate(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = direct_deploy("contracts/slaproof.py")
    direct_vm.sender = direct_alice
    args = arguments(direct_bob)
    c.create_sla(*args)
    with direct_vm.expect_revert("SLA already exists"):
        c.create_sla(*args)

def test_maintenance_overlap(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = direct_deploy("contracts/slaproof.py")
    direct_vm.sender = direct_alice
    args = arguments(direct_bob)
    args[8] = '[{"start":1790812900,"end":1790813100},{"start":1790813050,"end":1790813150}]'
    with direct_vm.expect_revert("overlapping/out-of-range maintenance"):
        c.create_sla(*args)


def test_evidence_with_independent_validator(direct_vm, direct_deploy, direct_alice, direct_bob):
    """Direct Mode web and LLM mocks; exercises the response.status accessor."""
    from pathlib import Path
    direct_vm.warp("2026-10-26T10:00:00Z")
    c = direct_deploy("contracts/slaproof.py")
    direct_vm.sender = direct_alice
    args = arguments(direct_bob)
    args[0] = "DIRECT_EVID001"
    c.create_sla(*args)
    direct_vm.sender = direct_bob
    manifest = Path("fixtures/manifest.json").read_text(encoding="utf-8").strip()
    c.submit_evidence("DIRECT_EVID001", manifest)
    for kind in ("monitoring", "incidents"):
        body = Path("fixtures/" + kind + ".json").read_text(encoding="utf-8")
        direct_vm.mock_web(".*fixtures/" + kind + r"\.json$", {"status": 200, "body": body})
    direct_vm.mock_llm(".*", '{"eligible_ids":["INC001"]}')
    c.evaluate("DIRECT_EVID001", 1)
    result = c.get_assessment("DIRECT_EVID001", 1)
    assert result["outcome"] == "MET"
    assert result["details"]["uptime_bps"] == 9993
    assert direct_vm.run_validator() is True
