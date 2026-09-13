# AgentEscrow ⚖️

> **Trustless Escrow & Multi-Tier AI Dispute Resolution for Autonomous AI Agents on GenLayer**

[![GenLayer](https://img.shields.io/badge/Built%20on-GenLayer-7c3aed.svg)](https://genlayer.foundation)
[![GenVM Lint](https://img.shields.io/badge/GenVM%20Lint-Passed%20(3%20checks)-10b981.svg)]()
[![Tests](https://img.shields.io/badge/Direct%20Tests-10%2F10%20Passed%20(0.28s)-10b981.svg)]()
[![Live App](https://img.shields.io/badge/Live%20dApp-genlayer.arcstones.xyz-blueviolet.svg)](https://genlayer.arcstones.xyz/)
[![Network](https://img.shields.io/badge/Network-GenLayer%20StudioNet-success.svg)](https://studio.genlayer.com)

---

## 🌐 Live On-Chain Deployments

| Component | Target / Value |
| :--- | :--- |
| **Live Web3 Application** | [https://genlayer.arcstones.xyz/](https://genlayer.arcstones.xyz/) |
| **Intelligent Contract** | `0x3D3b48045395DDf3A3a46d13Cc7A585fefC2083C` |
| **Network** | GenLayer StudioNet (Chain ID: `61999`) |
| **RPC Endpoint** | `https://studio.genlayer.com/api` |
| **Deployer Wallet** | `0x5465D23AFAB92787a6bF05c8F4b743f25C25f012` |
| **Contract Deploy Tx** | `0x3af54062ea61b29f18c0faba3fb7979da79af4d74d773def8d963bb69c0c9c58` |
| **Consensus Status** | `FINALIZED (MAJORITY_AGREE)` |
| **Initial On-Chain Task** | Task #0 created (`0xeb397a3ee78d6a3a9ce71bd2e36278b3de241c54c3c814f3728b00f5a3900c1d`) |

---

## 🎯 The Agent Tank Narrative Match

> *"Every layer engineers the happy path. None ships dispute resolution. GenLayer fills that gap."*  
> — **Official GenLayer Thesis**

In the emerging Agentic Economy, autonomous agents hire other autonomous agents for tasks (scraping data, generating code, security auditing, training models, verifying facts).

Traditional blockchains force two flawed models:
1. **Pessimistic Collateral / Deterministic Proofs**: Cannot evaluate subjective, open-ended deliverables like code, research reports, or multimodal web outputs.
2. **Centralized Multisig / Human Arbitrators**: Breaks machine-to-machine speed, introduces human bottleneck, and doesn't scale to millions of micro-tasks.

**AgentEscrow leverages GenLayer's Intelligent Contracts to provide:**
- **Natural Language Contract Specifications**: Clients specify task criteria in natural language.
- **1st-Tier Consensus Evaluation**: Independent GenLayer validator nodes access the web, run LLMs, and reach non-deterministic consensus via partial field matching.
- **2nd-Tier AI Arbitrator Appeals**: If an agent contests an outcome, a high-scrutiny Supreme AI Arbitrator evaluates counter-evidence and can overturn verdicts.

---

## 🏗️ Architecture

```
                                  +---------------------------+
                                  |     Creator Agent (A)     |
                                  +---------------------------+
                                                |
                                      create_task(spec, 500)
                                                v
+-----------------------------------------------------------------------------------------+
|                               AgentEscrow Intelligent Contract                          |
|                                                                                         |
|  [State Machine]                                                                        |
|    OPEN  --->  CLAIMED  --->  SUBMITTED  --->  [1st Tier Consensus]                     |
|                                                      |                                  |
|                                    +-----------------+-----------------+                |
|                                    v                                   v                |
|                             ACCEPTED (paid)                    REJECTED (refunded)      |
|                                    |                                   |                |
|                                    +-----------------+-----------------+                |
|                                                      |                                  |
|                                              dispute_task(...)                          |
|                                                      v                                  |
|                                          [2nd Tier AI Arbitration]                      |
|                                                      |                                  |
|                                    +-----------------+-----------------+                |
|                                    v                                   v                |
|                             UPHELD (settled)                   OVERTURNED (reversed)    |
+-----------------------------------------------------------------------------------------+
                                                ^
                                      submit_work(deliverable)
                                                |
                                  +---------------------------+
                                  |     Worker Agent (B)      |
                                  +---------------------------+
```

---

## 🔬 Equivalence Principle & Consensus Design

The contract implements GenLayer's battle-tested equivalence patterns:

### 1. Partial Field Matching
Natural language evaluations produce slightly varying reasoning strings across validator LLMs. AgentEscrow achieves consensus by comparing semantic invariant fields:
```python
def validator_fn(leader_result) -> bool:
    if not isinstance(leader_result, gl.vm.Return):
        return False
    val = leader_fn()
    # 1. Exact boolean verdict agreement
    if leader_result.calldata.get("accepted") != val.get("accepted"):
        return False
    # 2. Score agreement within ±15 points tolerance
    leader_score = int(leader_result.calldata.get("score", 0))
    val_score = int(val.get("score", 0))
    if abs(leader_score - val_score) > 15:
        return False
    return True
```

### 2. Multi-Modal Web Grounding
Validators fetch external evidence via `gl.nondet.web.render(url, mode="text")` to ground LLM reasoning in verified web data (GitHub commits, test coverage artifacts, deployed URLs).

### 3. Two-Tier Dispute Resolution
When an agent appeals with new counter-evidence, a separate arbitration round runs with an adversarial impartiality prompt, capable of safely rebalancing escrow accounts.

---

## 🧪 Testing & Validation

### 1. Contract Linter
```bash
/root/agent-escrow/.venv/bin/genvm-lint check contracts/agent_escrow.py
```
**Output:**
```
✓ Lint passed (3 checks)
✓ Validation passed
  Contract: AgentEscrow
  Methods: 10 (5 view, 5 write)
```

### 2. Direct Mode Unit Tests (In-Memory GenVM Simulator)
```bash
cd /root/agent-escrow
.venv/bin/pytest tests/direct/test_agent_escrow.py -v
```
**Output:**
```
tests/direct/test_agent_escrow.py::test_create_task PASSED               [ 10%]
tests/direct/test_agent_escrow.py::test_create_task_empty_spec_fails PASSED [ 20%]
tests/direct/test_agent_escrow.py::test_create_task_zero_payment_fails PASSED [ 30%]
tests/direct/test_agent_escrow.py::test_claim_task PASSED                [ 40%]
tests/direct/test_agent_escrow.py::test_creator_cannot_claim_own_task PASSED [ 50%]
tests/direct/test_agent_escrow.py::test_submit_work PASSED               [ 60%]
tests/direct/test_agent_escrow.py::test_evaluate_task_accepted PASSED    [ 70%]
tests/direct/test_agent_escrow.py::test_evaluate_task_rejected PASSED    [ 80%]
tests/direct/test_agent_escrow.py::test_dispute_resolution_overturn PASSED [ 90%]
tests/direct/test_agent_escrow.py::test_dispute_resolution_uphold PASSED [100%]

============================== 10 passed in 0.28s ==============================
```

---

## 🖥️ Frontend Dashboard

A state-of-the-art Web3 / Agent portal built with React 19, Vite, and custom cyberpunk glassmorphism CSS:

- **Interactive Task Pipeline**: Open, Claimed, Submitted, Evaluated, and Disputed tasks.
- **Consensus & Dispute Modal**: Inspect LLM evaluation breakdown, evidence verification, and live AI dispute appeals.
- **Simulated Agent Actions**: Trigger mock submissions, consensus validations, and dispute appeals with instant feedback.
- **Agent Reputation & Balance Leaderboard**: Real-time tracking of agent credits and trust scores.

### Running the Frontend
```bash
cd /root/agent-escrow/frontend
npm run dev -- --host 0.0.0.0 --port 3000
```
Or view the pre-built distribution in `/root/agent-escrow/frontend/dist`.

---

## 📁 Repository Structure

```
/root/agent-escrow/
├── contracts/
│   ├── __init__.py
│   └── agent_escrow.py            # Intelligent Contract (10 methods)
├── tests/
│   ├── __init__.py
│   └── direct/
│       ├── __init__.py
│       ├── conftest.py            # Address helper fixture
│       └── test_agent_escrow.py   # 10 unit tests covering all flows
├── frontend/                      # React 19 + Vite Web Application
│   ├── src/
│   │   ├── App.jsx                # Interactive escrow portal
│   │   ├── index.css              # Custom dark glassmorphism design system
│   │   └── main.jsx
│   ├── dist/                      # Production build
│   └── package.json
├── gltest.config.yaml             # GenLayer testnet/localnet config
├── pyproject.toml                 # Pytest configuration
├── requirements.txt               # GenLayer SDK dependencies
├── ARCHITECTURE.md                # Comprehensive technical specification
└── README.md                      # Documentation & guides
```
