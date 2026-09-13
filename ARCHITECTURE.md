# AgentEscrow — System Architecture & Specification

## 1. System Overview

AgentEscrow is an Intelligent Contract decentralized application designed for the GenLayer blockchain ecosystem, targeting the **Agent Tank** competition.

### Core Premise
Current AI agent architectures are brittle when attempting economic transactions. Standard smart contracts (EVM, SVM) cannot parse natural language deliverables, inspect external web artifacts without centralized oracles, or adjudicate ambiguous quality standards.

GenLayer's **Intelligent Contracts** and **Optimistic Non-Deterministic Consensus** allow decentralized networks of AI validator nodes to execute non-deterministic code, render web pages, query LLMs, and reach cryptographically verified consensus.

AgentEscrow turns this unique capability into infrastructure: a trustless escrow engine with multi-tier dispute arbitration for agent-to-agent commitments.

---

## 2. Component Design

### 2.1 State Model (`contracts/agent_escrow.py`)

```python
@allow_storage
@dataclass
class Task:
    id: u256
    creator: Address
    worker: Address
    spec: str
    payment_amount: u256
    result_content: str
    evidence_url: str
    status: str            # open | claimed | submitted | accepted | rejected | overturned | upheld
    score: i8              # 0..100
    evaluation_summary: str
    dispute_reason: str
    appeal_verdict: str
```

### 2.2 Storage Layout
- `tasks: TreeMap[u256, Task]`: Keyed storage for all escrow tasks.
- `task_count: u256`: Monotonically incrementing task counter.
- `balances: TreeMap[Address, u256]`: Internal accounting of earned / escrowed funds.
- `reputations: TreeMap[Address, i256]`: Trust score dynamically updated by task outcomes and dispute verdicts.

---

## 3. Consensus Mechanism

### Tier 1: Primary Non-Deterministic Evaluation
When `evaluate_task(task_id)` is called:
1. **Leader Execution**:
   - Fetches evidence via `gl.nondet.web.render(url, mode="text")` if URL provided.
   - Executes LLM prompt through `gl.nondet.exec_prompt(..., response_format="json")`.
   - Returns JSON containing `{"accepted": bool, "score": int, "summary": str}`.
2. **Validator Verification**:
   - Validates that `leader_result` is an instance of `gl.vm.Return`.
   - Independent validator execution of `leader_fn()`.
   - **Partial Field Matching**:
     - `leader_result.calldata["accepted"] == validator_result["accepted"]`
     - `abs(leader_result.calldata["score"] - validator_result["score"]) <= 15`
3. **Escrow Execution**:
   - If accepted: Worker balance credited `+payment`, worker reputation `+10`.
   - If rejected: Creator balance refunded `+payment`, worker reputation `-5`.

### Tier 2: Supreme AI Dispute Arbitrator ("GenLayer Fills That Gap")
If either creator or worker disputes the outcome:
1. `dispute_task(task_id, dispute_reason, counter_evidence_url)`
2. A separate arbitration round runs with higher scrutiny impartiality instructions.
3. If overturned:
   - Status switches to `overturned`.
   - Escrow balances are rebalanced atomically (reversing payment/refund).
   - Worker reputation adjusted to reward legitimate appeals or penalize fraudulent claims.
4. If upheld:
   - Status switches to `upheld`.

---

## 4. Safety & Linter Conformance

The contract adheres to all GenVM constraints:
- Uses `gl.vm.UserError` for clean exceptions rather than bare Python exceptions.
- Uses `Address(str_or_bytes)` conversion pattern for polymorphic address inputs.
- Safe integer casting for `u256` storage keys and arithmetic.
- Verified by `genvm-lint` with 0 warnings and 0 errors.

---

## 5. Security & Isolation on Host Server

To preserve host system integrity:
1. **Isolated Path**: All files and environments reside strictly inside `/root/agent-escrow/`.
2. **Untouched Existing Projects**: `/root/agent-reputation-oracle/`, `/root/MoneyPrinterTurbo/`, and other existing processes were neither modified nor interrupted.
3. **Zero Port Collisions**: Development servers bind to dedicated configurable ports or run via direct CLI/tests without occupying ports 80/443.
