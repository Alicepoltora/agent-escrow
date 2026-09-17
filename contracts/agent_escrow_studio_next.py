# v0.3.0
# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

import json
from dataclasses import dataclass
import genlayer as gl
from genlayer.types import *


@gl.storage.allow
@dataclass
class Task:
    id: u256
    creator: Address
    worker: Address
    spec: str
    payment_amount: u256
    result_content: str
    evidence_url: str
    status: str  # "open", "claimed", "submitted", "accepted", "rejected", "disputed", "overturned", "upheld"
    score: i8
    evaluation_summary: str
    dispute_reason: str
    appeal_verdict: str


class AgentEscrow(gl.contract.Contract):
    """
    AgentEscrow — Trustless Escrow with Multi-Tier AI Arbitration for Autonomous Agents.

    Core Thesis:
    'Every layer engineers the happy path. None ships dispute resolution. GenLayer fills that gap.'
    """

    tasks: gl.storage.TreeMap[u256, Task]
    task_count: u256
    balances: gl.storage.TreeMap[Address, u256]
    reputations: gl.storage.TreeMap[Address, i256]

    def __init__(self):
        self.task_count = u256(0)

    # ─── Task Lifecycle ────────────────────────────────────────────────────────

    @gl.public.write
    def create_task(self, spec: str, payment_amount: u256) -> u256:
        if len(spec.strip()) == 0:
            raise gl.vm.UserError("Task specification cannot be empty")
        if int(payment_amount) <= 0:
            raise gl.vm.UserError("Payment amount must be greater than zero")

        task_id = self.task_count
        creator = gl.message.sender_address
        zero_address = Address("0x0000000000000000000000000000000000000000")

        self.tasks[task_id] = Task(
            id=task_id,
            creator=creator,
            worker=zero_address,
            spec=spec,
            payment_amount=payment_amount,
            result_content="",
            evidence_url="",
            status="open",
            score=0,
            evaluation_summary="",
            dispute_reason="",
            appeal_verdict="",
        )

        self.task_count = u256(int(self.task_count) + 1)
        return task_id

    @gl.public.write
    def claim_task(self, task_id: u256) -> None:
        if task_id not in self.tasks:
            raise gl.vm.UserError("Task does not exist")

        task = self.tasks[task_id]
        if task.status != "open":
            raise gl.vm.UserError("Task is not open for claiming")

        sender = gl.message.sender_address
        if sender == task.creator:
            raise gl.vm.UserError("Creator cannot claim their own task")

        self.tasks[task_id].worker = sender
        self.tasks[task_id].status = "claimed"

    @gl.public.write
    def submit_work(self, task_id: u256, result_content: str, evidence_url: str = "") -> None:
        if task_id not in self.tasks:
            raise gl.vm.UserError("Task does not exist")

        task = self.tasks[task_id]
        sender = gl.message.sender_address

        zero_address = Address("0x0000000000000000000000000000000000000000")
        if task.worker == zero_address:
            if sender == task.creator:
                raise gl.vm.UserError("Creator cannot submit work for own task")
            self.tasks[task_id].worker = sender
        elif task.worker != sender:
            raise gl.vm.UserError("Only the assigned worker can submit work")

        if task.status not in ["open", "claimed"]:
            raise gl.vm.UserError("Task is not in a submittable status")

        if len(result_content.strip()) == 0:
            raise gl.vm.UserError("Submitted work content cannot be empty")

        self.tasks[task_id].result_content = result_content
        self.tasks[task_id].evidence_url = evidence_url
        self.tasks[task_id].status = "submitted"

    # ─── 1st Tier Evaluation: Decentralized LLM + Web Consensus ───────────────

    @gl.public.write
    def evaluate_task(self, task_id: u256) -> dict:
        if task_id not in self.tasks:
            raise gl.vm.UserError("Task does not exist")

        task = self.tasks[task_id]
        if task.status != "submitted":
            raise gl.vm.UserError("Task is not in submitted status")

        task_spec = str(task.spec)
        deliverable = str(task.result_content)
        evidence_url = str(task.evidence_url)

        def leader_fn() -> dict:
            external_context = ""
            if evidence_url and evidence_url.startswith("http"):
                try:
                    web_data = gl.nondet.web.render(evidence_url, mode="text")
                    external_context = f"Evidence from {evidence_url}:\n{web_data[:2000]}"
                except Exception:
                    external_context = f"Evidence URL {evidence_url} could not be rendered."

            prompt = f"""You are an impartial AI consensus judge on GenLayer.
Evaluate whether the worker deliverable satisfies the task specification.

TASK SPECIFICATION:
{task_spec}

WORKER DELIVERABLE:
{deliverable}

ADDITIONAL CONTEXT:
{external_context}

Respond in strict JSON:
{{
    "accepted": true,
    "score": 85,
    "summary": "Brief 1-2 sentence evaluation"
}}
Rules:
- accepted must be true if score >= 60, false otherwise.
- score must be an integer between 0 and 100.
- Output ONLY parsable JSON, no markdown fences or conversational text.
"""
            raw = gl.nondet.exec_prompt(prompt, response_format="json")
            if isinstance(raw, dict):
                return raw
            cleaned = str(raw).strip().replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False

            val = leader_fn()
            # Consensus on verdict
            if leader_result.calldata.get("accepted") != val.get("accepted"):
                return False

            # Score agreement within tolerance
            leader_score = int(leader_result.calldata.get("score", 0))
            val_score = int(val.get("score", 0))
            if abs(leader_score - val_score) > 15:
                return False

            return True

        eval_result = gl.vm.run_nondet(leader_fn, validator_fn)

        accepted = bool(eval_result.get("accepted", False))
        score = int(eval_result.get("score", 0))
        summary = str(eval_result.get("summary", ""))

        self.tasks[task_id].score = score
        self.tasks[task_id].evaluation_summary = summary

        worker = self.tasks[task_id].worker
        creator = self.tasks[task_id].creator
        payment = self.tasks[task_id].payment_amount

        if accepted:
            self.tasks[task_id].status = "accepted"
            current_worker_bal = int(self.balances.get(worker, u256(0)))
            self.balances[worker] = u256(current_worker_bal + int(payment))
            cur_rep = int(self.reputations.get(worker, 0))
            self.reputations[worker] = cur_rep + 10
        else:
            self.tasks[task_id].status = "rejected"
            current_creator_bal = int(self.balances.get(creator, u256(0)))
            self.balances[creator] = u256(current_creator_bal + int(payment))
            cur_rep = int(self.reputations.get(worker, 0))
            self.reputations[worker] = cur_rep - 5

        return eval_result

    # ─── 2nd Tier Arbitration: Dispute Resolution ("GenLayer Fills That Gap") ─

    @gl.public.write
    def dispute_task(self, task_id: u256, dispute_reason: str, counter_evidence_url: str = "") -> dict:
        if task_id not in self.tasks:
            raise gl.vm.UserError("Task does not exist")

        task = self.tasks[task_id]
        sender = gl.message.sender_address

        if sender != task.creator and sender != task.worker:
            raise gl.vm.UserError("Only task creator or worker can file a dispute")

        if task.status not in ["accepted", "rejected"]:
            raise gl.vm.UserError("Can only dispute evaluated tasks (accepted or rejected)")

        if len(dispute_reason.strip()) == 0:
            raise gl.vm.UserError("Dispute reason cannot be empty")

        task_spec = str(task.spec)
        deliverable = str(task.result_content)
        initial_status = str(task.status)
        initial_summary = str(task.evaluation_summary)
        counter_url = str(counter_evidence_url)
        reason = str(dispute_reason)

        def judge_leader_fn() -> dict:
            counter_evidence = ""
            if counter_url and counter_url.startswith("http"):
                try:
                    web_data = gl.nondet.web.render(counter_url, mode="text")
                    counter_evidence = f"Counter Evidence from {counter_url}:\n{web_data[:2000]}"
                except Exception:
                    counter_evidence = f"Counter evidence URL {counter_url} could not be rendered."

            prompt = f"""You are the Supreme AI Dispute Arbitrator for GenLayer AgentEscrow.
An automated evaluation has been disputed. Review all evidence impartially.

ORIGINAL SPECIFICATION:
{task_spec}

WORK DELIVERABLE:
{deliverable}

FIRST-TIER VERDICT: {initial_status}
FIRST-TIER REASONING: {initial_summary}

DISPUTE CLAIM:
{reason}

COUNTER EVIDENCE:
{counter_evidence}

Determine whether to 'uphold' the original verdict or 'overturn' it based on the evidence.
Respond in strict JSON:
{{
    "verdict": "uphold" or "overturn",
    "reasoning": "Clear explanation of arbitrated decision"
}}
Output ONLY valid JSON.
"""
            raw = gl.nondet.exec_prompt(prompt, response_format="json")
            if isinstance(raw, dict):
                return raw
            cleaned = str(raw).strip().replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)

        def judge_validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            val = judge_leader_fn()
            return leader_result.calldata.get("verdict") == val.get("verdict")

        dispute_result = gl.vm.run_nondet(judge_leader_fn, judge_validator_fn)

        verdict = str(dispute_result.get("verdict", "uphold")).lower()
        reasoning = str(dispute_result.get("reasoning", ""))

        self.tasks[task_id].dispute_reason = dispute_reason
        self.tasks[task_id].appeal_verdict = reasoning

        worker = self.tasks[task_id].worker
        creator = self.tasks[task_id].creator
        payment = int(self.tasks[task_id].payment_amount)

        if verdict == "overturn":
            self.tasks[task_id].status = "overturned"
            if initial_status == "rejected":
                cur_creator_bal = int(self.balances.get(creator, u256(0)))
                new_creator_bal = max(0, cur_creator_bal - payment)
                self.balances[creator] = u256(new_creator_bal)

                cur_worker_bal = int(self.balances.get(worker, u256(0)))
                self.balances[worker] = u256(cur_worker_bal + payment)

                self.reputations[worker] = int(self.reputations.get(worker, 0)) + 20
            elif initial_status == "accepted":
                cur_worker_bal = int(self.balances.get(worker, u256(0)))
                new_worker_bal = max(0, cur_worker_bal - payment)
                self.balances[worker] = u256(new_worker_bal)

                cur_creator_bal = int(self.balances.get(creator, u256(0)))
                self.balances[creator] = u256(cur_creator_bal + payment)

                self.reputations[worker] = int(self.reputations.get(worker, 0)) - 25
        else:
            self.tasks[task_id].status = "upheld"

        return dispute_result

    # ─── Views ────────────────────────────────────────────────────────────────

    @gl.public.view
    def get_task_count(self) -> int:
        return int(self.task_count)

    @gl.public.view
    def get_task(self, task_id: u256) -> dict:
        if task_id not in self.tasks:
            raise gl.vm.UserError("Task does not exist")

        t = self.tasks[task_id]
        return {
            "id": int(t.id),
            "creator": str(t.creator),
            "worker": str(t.worker),
            "spec": str(t.spec),
            "payment_amount": int(t.payment_amount),
            "result_content": str(t.result_content),
            "evidence_url": str(t.evidence_url),
            "status": str(t.status),
            "score": int(t.score),
            "evaluation_summary": str(t.evaluation_summary),
            "dispute_reason": str(t.dispute_reason),
            "appeal_verdict": str(t.appeal_verdict),
        }

    @gl.public.view
    def get_all_tasks(self) -> list:
        result = []
        total = int(self.task_count)
        for i in range(total):
            tid = u256(i)
            if tid in self.tasks:
                result.append(self.get_task(tid))
        return result

    @gl.public.view
    def get_agent_balance(self, agent: Address) -> int:
        if isinstance(agent, (str, bytes)):
            agent = Address(agent)
        return int(self.balances.get(agent, u256(0)))

    @gl.public.view
    def get_agent_reputation(self, agent: Address) -> int:
        if isinstance(agent, (str, bytes)):
            agent = Address(agent)
        return int(self.reputations.get(agent, 0))
