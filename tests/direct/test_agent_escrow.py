"""Direct mode tests for AgentEscrow intelligent contract."""

import json
import pytest
from tests.direct.conftest import to_hex

CONTRACT_PATH = "contracts/agent_escrow.py"


def _setup_eval_mocks(vm, accepted: bool, score: int, summary: str = "Evaluation test"):
    vm.clear_mocks()
    vm.mock_web(
        r".*",
        {"status": 200, "body": "Verified deliverable content and test proofs."},
    )
    vm.mock_llm(
        r".*TASK SPECIFICATION.*",
        json.dumps({"accepted": accepted, "score": score, "summary": summary}),
    )


def _setup_dispute_mocks(vm, verdict: str, reasoning: str = "Dispute arbitrated"):
    vm.clear_mocks()
    vm.mock_web(
        r".*",
        {"status": 200, "body": "Arbitration counter-evidence review doc."},
    )
    vm.mock_llm(
        r".*Supreme AI Dispute Arbitrator.*",
        json.dumps({"verdict": verdict, "reasoning": reasoning}),
    )


def test_create_task(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    alice_hex = to_hex(direct_alice)

    task_id = contract.create_task("Scrape latest research on LLM consensus", 500)
    assert task_id == 0

    count = contract.get_task_count()
    assert count == 1

    task = contract.get_task(0)
    assert task["id"] == 0
    assert task["creator"] == alice_hex
    assert task["spec"] == "Scrape latest research on LLM consensus"
    assert task["payment_amount"] == 500
    assert task["status"] == "open"
    assert task["score"] == 0


def test_create_task_empty_spec_fails(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice

    from gltest.direct import ContractRollback
    with pytest.raises((ContractRollback, Exception)):
        contract.create_task("", 100)


def test_create_task_zero_payment_fails(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice

    from gltest.direct import ContractRollback
    with pytest.raises((ContractRollback, Exception)):
        contract.create_task("Valid spec", 0)


def test_claim_task(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Implement REST API client", 300)

    # Bob claims task
    direct_vm.sender = direct_bob
    bob_hex = to_hex(direct_bob)
    contract.claim_task(0)

    task = contract.get_task(0)
    assert task["worker"] == bob_hex
    assert task["status"] == "claimed"


def test_creator_cannot_claim_own_task(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Self task", 100)

    from gltest.direct import ContractRollback
    with pytest.raises((ContractRollback, Exception)):
        contract.claim_task(0)


def test_submit_work(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Build landing page", 400)

    # Bob claims and submits
    direct_vm.sender = direct_bob
    contract.claim_task(0)
    contract.submit_work(0, "https://github.com/agent/demo-repo", "https://demo.app")

    task = contract.get_task(0)
    assert task["status"] == "submitted"
    assert task["result_content"] == "https://github.com/agent/demo-repo"
    assert task["evidence_url"] == "https://demo.app"


def test_evaluate_task_accepted(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Write smart contract unit tests", 600)

    direct_vm.sender = direct_bob
    bob_hex = to_hex(direct_bob)
    contract.claim_task(0)
    contract.submit_work(0, "Tests implemented with 98% coverage", "https://coverage.report")

    # Mock consensus evaluation accepted
    _setup_eval_mocks(direct_vm, accepted=True, score=92, summary="Full coverage achieved.")

    res = contract.evaluate_task(0)
    assert res["accepted"] is True
    assert res["score"] == 92

    task = contract.get_task(0)
    assert task["status"] == "accepted"
    assert task["score"] == 92

    # Check worker balance and reputation
    bal = contract.get_agent_balance(direct_bob)
    rep = contract.get_agent_reputation(direct_bob)
    assert bal == 600
    assert rep == 10


def test_evaluate_task_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Train LoRA fine-tune", 800)

    direct_vm.sender = direct_bob
    contract.claim_task(0)
    contract.submit_work(0, "Incomplete weights file", "https://weights.com")

    # Mock consensus evaluation rejected
    _setup_eval_mocks(direct_vm, accepted=False, score=30, summary="Weights corrupted and loss diverged.")

    res = contract.evaluate_task(0)
    assert res["accepted"] is False

    task = contract.get_task(0)
    assert task["status"] == "rejected"
    assert task["score"] == 30

    # Check refund to creator
    creator_bal = contract.get_agent_balance(direct_alice)
    assert creator_bal == 800


def test_dispute_resolution_overturn(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Audit security vulnerabilities", 1000)

    direct_vm.sender = direct_bob
    contract.claim_task(0)
    contract.submit_work(0, "Audit report attached", "https://audit.pdf")

    # 1. First evaluation rejects falsely
    _setup_eval_mocks(direct_vm, accepted=False, score=45, summary="Suspected missing signatures.")
    contract.evaluate_task(0)

    task_before = contract.get_task(0)
    assert task_before["status"] == "rejected"

    # 2. Worker disputes with counter evidence
    _setup_dispute_mocks(direct_vm, verdict="overturn", reasoning="Counter evidence confirms all signatures were cryptographic.")
    dispute_res = contract.dispute_task(0, "All cryptographic signatures were valid and verified.", "https://signatures.verified")

    assert dispute_res["verdict"] == "overturn"

    task_after = contract.get_task(0)
    assert task_after["status"] == "overturned"
    assert "cryptographic" in task_after["appeal_verdict"]

    # Balances adjusted: worker gets paid!
    worker_bal = contract.get_agent_balance(direct_bob)
    assert worker_bal == 1000


def test_dispute_resolution_uphold(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = direct_alice
    contract.create_task("Write documentation", 250)

    direct_vm.sender = direct_bob
    contract.claim_task(0)
    contract.submit_work(0, "Empty readme", "")

    _setup_eval_mocks(direct_vm, accepted=False, score=10, summary="Nothing written.")
    contract.evaluate_task(0)

    _setup_dispute_mocks(direct_vm, verdict="uphold", reasoning="Work was genuinely empty.")
    contract.dispute_task(0, "I thought it was good enough")

    task = contract.get_task(0)
    assert task["status"] == "upheld"
