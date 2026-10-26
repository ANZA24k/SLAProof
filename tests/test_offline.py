"""Deterministic no-network harness; NOT equivalent to GenVM or Full Consensus."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
from datetime import datetime as RealDateTime, timezone
import pytest

ROOT = Path(__file__).resolve().parents[1]
START, END, DEADLINE = 1790812800, 1790899200, 1793491200
OWNER, CLAIMANT = "0x" + "1"*40, "0x" + "2"*40
COMMIT = "44e49926a411c56414892b1471fa13f4d961175a"


class UserError(Exception):
    pass


class StorageMap(dict):
    @classmethod
    def __class_getitem__(cls, unused):
        return cls


class FakeVM:
    def __init__(self):
        self.Contract = object
        self.public = types.SimpleNamespace(write=lambda f: f, view=lambda f: f)
        self.vm = types.SimpleNamespace(UserError=UserError, Return=type("Return", (), {}),
                                        run_nondet_unsafe=self.consensus)
        self.message = types.SimpleNamespace(sender_address=OWNER)
        self.nondet = types.SimpleNamespace(web=types.SimpleNamespace(get=self.get),
                                           exec_prompt=self.prompt)
        self.web = {}
        self.llm = {"eligible_ids": ["INC001"]}
        self.mismatch = False
        self.validation_calls = 0

    def get(self, url):
        x = self.web.get(url)
        if isinstance(x, Exception):
            raise x
        if x is None:
            return types.SimpleNamespace(status_code=404, body=b"")
        if isinstance(x, int):
            return types.SimpleNamespace(status_code=x, body=b"")
        return types.SimpleNamespace(status_code=200, body=x)

    def prompt(self, text, response_format="json"):
        assert "UNTRUSTED SOURCE DATA" in text
        return self.llm

    def consensus(self, lead, validate):
        value = lead()
        self.validation_calls += 1
        if self.mismatch:
            self.web = {k: b"bad" for k in self.web}
        ret = self.vm.Return()
        ret.calldata = value
        if not validate(ret):
            raise UserError("validator disagreement")
        return value


@pytest.fixture
def state(monkeypatch):
    fake = FakeVM()
    genlayer = types.ModuleType("genlayer")
    genlayer.gl, genlayer.TreeMap = fake, StorageMap
    genlayer.u256 = int
    genlayer.Address = lambda x: str(x).lower()
    monkeypatch.setitem(sys.modules, "genlayer", genlayer)
    spec = importlib.util.spec_from_file_location("sla_test", ROOT/"contracts"/"slaproof.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class Clock:
        @staticmethod
        def now(tz=None):
            return RealDateTime.fromtimestamp(1792500000, timezone.utc)
    monkeypatch.setattr(module, "datetime", Clock)
    instance = module.SLAProof()
    for field in ("agreements", "latest_revisions", "evidence", "assessments", "used_manifests", "settlements"):
        setattr(instance, field, StorageMap())
    return module, fake, instance


def create(state, **extra):
    _, fake, c = state
    a = dict(sla_id="DEMO001", service_id="demo-api", claimant=CLAIMANT,
             period_start=START, period_end=END, deadline=DEADLINE,
             uptime_min_bps=9990, latency_max_ms=250,
             maintenance_json="[]", exclusions_json='["UPSTREAM_FAILURE"]',
             credit_pool_units=1000000, partial_credit_bps=1500, breach_credit_bps=4000)
    a.update(extra)
    c.create_sla(**a)
    fake.message.sender_address = CLAIMANT
    return c


def manifest():
    sources, mapping = [], {}
    for kind, file in (("monitoring", "monitoring.json"), ("incident", "incidents.json")):
        content = (ROOT/"fixtures"/file).read_bytes()
        url = "https://raw.githubusercontent.com/ANZA24k/SLAProof/"+COMMIT+"/fixtures/"+file
        sources.append({"kind": kind, "url": url, "length": len(content),
                        "sha256": hashlib.sha256(content).hexdigest()})
        mapping[url] = content
    return json.dumps({"nonce": "demo001", "sources": sources}, sort_keys=True, separators=(",", ":")), mapping


def submit(state):
    _, fake, c = state
    payload, fake.web = manifest()
    c.submit_evidence("DEMO001", payload)
    return payload


def test_create_immutable_and_duplicate(state):
    c = create(state)
    first = c.get_sla("DEMO001")
    assert len(first["terms_hash"]) == 64
    with pytest.raises(UserError, match="already exists"):
        create(state)
    assert c.get_sla("DEMO001") == first


def test_access_control(state):
    _, fake, c = state
    create(state)
    fake.message.sender_address = OWNER
    with pytest.raises(UserError, match="only claimant"):
        c.submit_evidence("DEMO001", manifest()[0])


def test_met_and_settle_once(state):
    _, fake, c = state
    create(state)
    submit(state)
    fake.message.sender_address = "0x" + "3"*40
    c.evaluate("DEMO001", 1)
    a = c.get_assessment("DEMO001", 1)
    assert fake.validation_calls == 1
    assert a["outcome"] == "MET"
    assert a["details"]["uptime_bps"] == 9993
    assert a["details"]["counted_outage_seconds"] == 60
    assert a["details"]["exempt_seconds"] == 180
    assert len(a["decision_hash"]) == 64
    c.settle("DEMO001")
    receipt = c.get_settlement("DEMO001")
    assert receipt["claimant_credit_units"] == 0
    assert receipt["provider_remaining_units"] == 1000000
    with pytest.raises(UserError, match="already settled"):
        c.settle("DEMO001")


def test_semantic_disagreement_rejects(state):
    _, fake, c = state
    create(state)
    submit(state)
    fake.mismatch = True
    with pytest.raises(UserError, match="disagreement"):
        c.evaluate("DEMO001", 1)
    assert "DEMO001:1" not in c.assessments


def test_inconclusive_retry_and_replay(state):
    mod, fake, c = state
    create(state)
    payload = submit(state)
    fake.web = {}
    c.evaluate("DEMO001", 1)
    assert c.get_assessment("DEMO001", 1)["outcome"] == "INCONCLUSIVE"
    new = json.loads(payload)
    new["nonce"] = "demo002"
    new = mod._canon(new)
    c.submit_evidence("DEMO001", new)
    with pytest.raises(UserError, match="revision must be latest"):
        c.evaluate("DEMO001", 1)
    c.evaluate("DEMO001", 2)
    with pytest.raises(UserError, match="duplicate evidence"):
        c.submit_evidence("DEMO001", new)


def test_bad_bytes_not_accepted(state):
    _, fake, c = state
    create(state)
    submit(state)
    url = next(iter(fake.web))
    fake.web[url] += b"x"
    c.evaluate("DEMO001", 1)
    assert c.get_assessment("DEMO001", 1)["details"]["error_code"] == "LENGTH_MISMATCH"


def test_transient_is_retryable(state):
    _, fake, c = state
    create(state)
    submit(state)
    fake.web = {x: 503 for x in fake.web}
    with pytest.raises(UserError, match="temporary upstream"):
        c.evaluate("DEMO001", 1)
    assert not c.assessments


def test_manifest_security(state):
    mod, fake, c = state
    create(state)
    obj = json.loads(manifest()[0])
    with pytest.raises(UserError, match="canonical"):
        c.submit_evidence("DEMO001", json.dumps(obj))
    obj["sources"][0]["url"] = "http://127.0.0.1/admin"
    with pytest.raises(UserError, match="non-canonical"):
        c.submit_evidence("DEMO001", mod._canon(obj))
    with pytest.raises(UserError, match="invalid manifest JSON"):
        c.submit_evidence("DEMO001", '{"nonce":"bad001","nonce":"bad002","sources":[]}')


def test_expiry_refund_without_custody(state, monkeypatch):
    mod, _, c = state
    create(state)
    class Late:
        @staticmethod
        def now(tz=None):
            return RealDateTime.fromtimestamp(DEADLINE+1, timezone.utc)
    monkeypatch.setattr(mod, "datetime", Late)
    c.settle("DEMO001")
    settlement = c.get_settlement("DEMO001")
    assert settlement["outcome"] == "INCONCLUSIVE"
    assert settlement["claimant_credit_units"] == 0
    assert settlement["provider_remaining_units"] == settlement["total_units"]
    assert settlement["non_custodial"]


def test_deterministic_boundaries(state):
    mod, _, _ = state
    t = {"uptime_min_bps": 9990, "latency_max_ms": 250}
    assert mod._verdict(t, 9993, 220) == "MET"
    assert mod._verdict(t, 9985, 220) == "PARTIAL"
    assert mod._verdict(t, 9991, 260) == "PARTIAL"
    assert mod._verdict(t, 9500, 220) == "BREACHED"
    assert mod._verdict(t, 9993, 400) == "BREACHED"
    source = [{"id": "INC", "start": 20, "end": 100}]
    p = {"start": 0, "end": 1000, "maintenance": [{"start": 40, "end": 80}]}
    assert mod._calculate(p, source, [])[1:] == (40, 40)
    assert mod._calculate(p, source, ["INC"])[1:] == (0, 80)
