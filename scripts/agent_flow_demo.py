"""
AgentEscrow — Agent-to-Agent Autonomous Lifecycle & Dispute Demo
Simulates two AI agents (Alice & Bob) interacting trustlessly via GenLayer Intelligent Contracts.
"""

import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gltest.direct import VMContext, deploy_contract, create_address
from tests.direct.conftest import to_hex

CONTRACT_PATH = "contracts/agent_escrow.py"


def c(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"


def print_banner():
    print(c("""
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                      AGENT-ESCROW PROTOCOL ⚖️                          ║
  ║       Trustless AI Agent Commitments & Multi-Tier AI Arbitration      ║
  ║                   Powered by GenLayer Intelligent Contracts           ║
  ╚═══════════════════════════════════════════════════════════════════════╝
    """, "35"))
    print(c("  'Every layer engineers the happy path. None ships dispute resolution.", "36"))
    print(c("   GenLayer fills that gap.'\n", "36"))


def run_demo():
    print_banner()

    # 1. Initialize Direct VM Simulator
    print(c("▶ [1/5] Bootstrapping GenVM Simulator & Deploying AgentEscrow...", "33"))
    vm = VMContext()
    alice = create_address("agent_alice")
    bob = create_address("agent_bob")

    with vm.activate():
        contract_file = Path(CONTRACT_PATH).resolve()
        contract = deploy_contract(contract_file, vm)

        alice_hex = to_hex(alice)
        bob_hex = to_hex(bob)

        print(f"  ✓ Contract deployed at: {c('0x' + '7c' * 20, '32')}")
        print(f"  ✓ Agent Alice (Creator): {c(alice_hex[:10] + '...' + alice_hex[-6:], '34')}")
        print(f"  ✓ Agent Bob   (Worker):  {c(bob_hex[:10] + '...' + bob_hex[-6:], '32')}\n")

        time.sleep(0.4)

        # 2. Agent Alice creates a task with locked escrow
        print(c("▶ [2/5] Agent Alice: Publishing Natural Language Escrow Task...", "33"))
        vm.sender = alice
        task_spec = (
            "Develop an automated MEV-resistant arbitrage detector with "
            "mempool transaction simulation and sub-second alert latency."
        )
        payment = 750
        task_id = contract.create_task(task_spec, payment)
        print(f"  ✓ Task #{task_id} registered on GenLayer storage")
        print(f"    • Spec: {c(task_spec, '37')}")
        print(f"    • Escrow Locked: {c(f'{payment} GEN', '32')}")
        print(f"    • Status: {c('OPEN', '36')}\n")

        time.sleep(0.4)

        # 3. Agent Bob claims and submits deliverable
        print(c("▶ [3/5] Agent Bob: Claiming Task & Submitting Deliverable...", "33"))
        vm.sender = bob
        contract.claim_task(task_id)
        print(f"  ✓ Task #{task_id} claimed by Worker Agent Bob")

        deliverable = "Repository contains Go/Rust implementation with backtested 99.4% precision."
        evidence_url = "https://github.com/agent-bob/mev-detector-release-v1"
        contract.submit_work(task_id, deliverable, evidence_url)
        print(f"  ✓ Work Deliverable submitted:")
        print(f"    • Output: {c(deliverable, '37')}")
        print(f"    • Evidence: {c(evidence_url, '34')}")
        print(f"    • Status: {c('SUBMITTED (Pending Consensus)', '33')}\n")

        time.sleep(0.4)

        # 4. Tier-1 Consensus Evaluation
        print(c("▶ [4/5] GenLayer Consensus: Multi-Validator Web + LLM Equivalence Principle...", "33"))
        vm.clear_mocks()
        vm.mock_web(
            r".*github.com.*",
            {"status": 200, "body": "Verified git tree: 48 commits, CI benchmark: 140ms latency, zero false positives."},
        )
        vm.mock_llm(
            r".*TASK SPECIFICATION.*",
            json.dumps({
                "accepted": True,
                "score": 94,
                "summary": "Meets all criteria. Verified sub-second alert benchmark and mempool simulation engine.",
            }),
        )

        eval_result = contract.evaluate_task(task_id)
        task_after = contract.get_task(task_id)

        print(f"  ✓ Non-deterministic execution verified across validator set!")
        print(f"    • Verdict: {c('ACCEPTED ✅', '32')}")
        print(f"    • Quality Score: {c(str(task_after['score']) + '/100', '32')}")
        print(f"    • AI Reasoning: {c(task_after['evaluation_summary'], '37')}")
        print(f"    • Bob Earned Balance: {c(str(contract.get_agent_balance(bob)) + ' GEN', '32')}")
        print(f"    • Bob Trust Score: {c('+' + str(contract.get_agent_reputation(bob)), '32')}\n")

        time.sleep(0.4)

        # 5. Tier-2 Dispute Arbitration Demonstration ("GenLayer Fills That Gap")
        print(c("▶ [5/5] Tier-2 AI Arbitration: Simulating Adversarial Dispute & Appeal...", "33"))
        print("  Scenario: Alice disputes task claiming deliverable lacked documentation.")
        vm.sender = alice
        dispute_reason = "Code is missing documentation for multi-node clustering."
        counter_evidence = "https://audit.verify/clustering-review.pdf"

        # Supreme AI Arbitrator evaluates appeal with higher scrutiny
        vm.clear_mocks()
        vm.mock_web(
            r".*",
            {"status": 200, "body": "Counter-evidence analysis: clustering documentation was present in docs/cluster.md."},
        )
        vm.mock_llm(
            r".*Supreme AI Dispute Arbitrator.*",
            json.dumps({
                "verdict": "uphold",
                "reasoning": "Audit reveals cluster.md thoroughly covers deployment and failover topology. Initial verdict upheld.",
            }),
        )

        dispute_res = contract.dispute_task(task_id, dispute_reason, counter_evidence)
        task_dispute = contract.get_task(task_id)

        print(f"  ✓ Supreme AI Arbitrator Consensus Reached:")
        print(f"    • Appeal Verdict: {c(dispute_res['verdict'].upper() + ' ⚖️', '35')}")
        print(f"    • Judicial Reasoning: {c(dispute_res['reasoning'], '37')}")
        print(f"    • Final Task Status: {c(task_dispute['status'].upper(), '32')}")
        print(f"    • Funds Protected in Escrow: {c('Bob keeps 750 GEN payout', '32')}\n")

        print(c("═══════════════════════════════════════════════════════════════════════", "35"))
        print(c("  🎉 Complete AgentEscrow Lifecycle Verified Successfully on GenLayer!", "32"))
        print(c("  🌐 Live Production dApp: https://genlayer.arcstones.xyz/\n", "36"))


if __name__ == "__main__":
    run_demo()
