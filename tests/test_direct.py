"""Official genlayer-test Direct Mode smoke tests."""
START = 1790812800
END = 1790899200
CLOSE = END + 2592000

def arguments(bob):
    return ["DIRECT001", "demo-api", str(bob), START, END, CLOSE,
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
