# 🏆 GenLayer Agent Tank Hackathon — Submission Package

**Project Name:** AgentEscrow ⚖️  
**Tagline:** Trustless Escrow & Multi-Tier AI Dispute Resolution for Autonomous AI Agents  
**Live Application:** [https://genlayer.arcstones.xyz/](https://genlayer.arcstones.xyz/)  
**GitHub Repository:** [https://github.com/Alicepoltora/agent-escrow](https://github.com/Alicepoltora/agent-escrow)  
**Contract Address (Studio Next - Chain 61997):** [`0xE01D1CE3D823126A841b64475a3D97e9CfA1d009`](https://explorer-studio-dev.genlayer.com/address/0xE01D1CE3D823126A841b64475a3D97e9CfA1d009)  
**Studio Next Explorer:** [https://explorer-studio-dev.genlayer.com/address/0xE01D1CE3D823126A841b64475a3D97e9CfA1d009](https://explorer-studio-dev.genlayer.com/address/0xE01D1CE3D823126A841b64475a3D97e9CfA1d009)  
**Contract Deploy Tx:** [`0x6b61f77c8e85a30b1413528df2732079774c80d7b870b26c340cc9a90cf179f5`](https://explorer-studio-dev.genlayer.com/tx/0x6b61f77c8e85a30b1413528df2732079774c80d7b870b26c340cc9a90cf179f5)  
**Live On-Chain Transaction Proofs (Chain 61997):**
* **`create_task` Tx:** [`0x9d8ead39420fd90ca253217c69f16a0c97e3fb670d21e24b15f9ee7814121806`](https://explorer-studio-dev.genlayer.com/tx/0x9d8ead39420fd90ca253217c69f16a0c97e3fb670d21e24b15f9ee7814121806)
* **`submit_work` Tx:** [`0x71b0461ad283c06f552ada401c6db70852dcfa2b8ce61e5578eb0237993d552a`](https://explorer-studio-dev.genlayer.com/tx/0x71b0461ad283c06f552ada401c6db70852dcfa2b8ce61e5578eb0237993d552a)
* **`evaluate_task` (AI Consensus) Tx:** [`0x7d95862143cf89ae01a93b497b838590041fc0978a8313ea7ba6d88d8c94fa5c`](https://explorer-studio-dev.genlayer.com/tx/0x7d95862143cf89ae01a93b497b838590041fc0978a8313ea7ba6d88d8c94fa5c) — *Score 85/100, Accepted by Quorum*
* **`dispute_task` (Supreme AI Arbitration) Tx:** [`0x57694361f2e192d9cabe6df5afcb593e3fc0cb8546e925938e1a800118efd140`](https://explorer-studio-dev.genlayer.com/tx/0x57694361f2e192d9cabe6df5afcb593e3fc0cb8546e925938e1a800118efd140) — *Verdict: UPHELD with written judicial justification*
**3-Minute Demo Video (1080p MP4):** [https://genlayer.arcstones.xyz/media/AgentEscrow_Demo_Pitch.mp4](https://genlayer.arcstones.xyz/media/AgentEscrow_Demo_Pitch.mp4)  

---

## 1. Short Description (1-2 sentences)
AgentEscrow is the first decentralized escrow protocol purpose-built for the agentic economy. It allows autonomous AI agents to contract work in natural language and resolve subjective deliverable disputes through multi-tier validator LLM consensus on GenLayer — without human bottlenecks.

---

## 2. The Problem
In the emerging agentic economy, AI agents need to hire other autonomous agents for open-ended tasks: code auditing, web research, copywriting, data extraction, and model fine-tuning.

However, traditional Web3 escrow faces a fatal trilemma:
1. **Deterministic smart contracts** cannot evaluate subjective, qualitative deliverables (code quality, report accuracy, prompt adherence) without mathematical proofs that don't exist for creative work.
2. **Centralized human arbiters (Kleros, Aragon, multisigs)** break agent autonomy: they take days or weeks to resolve micro-disputes, cost dozens of dollars in fees, and cannot scale to millions of high-frequency agent subtasks.
3. **Optimistic happy-path protocols** assume good behavior: *"Every layer engineers the happy path. None ships dispute resolution."* When deliverables are sub-par, agents are either rugged or locked in limbo.

---

## 3. The Solution & GenLayer Thesis Match
AgentEscrow directly fulfills GenLayer's vision: **shipping dispute resolution for autonomous agents**.

* **Natural Language Specifications**: Contracts accept task requirements in plain English, with explicit quality thresholds and criteria.
* **Non-Deterministic Web & AI Consensus**: Independent GenLayer validator nodes browse live evidence (GitHub commits, PRs, URLs) using `gl.nondet.web.render()` and evaluate subjective quality using `gl.nondet.exec_prompt()`.
* **The Equivalence Principle**: Deterministic consensus is reached across non-deterministic LLM responses through invariant boolean and numerical score tolerance matching (within ±15 points).
* **Multi-Tier Dispute Resolution**: When an agent appeals a rejected submission, a 2nd-tier arbitration round convenes with an adversarial impartiality prompt. If the dispute is valid, validators overturn the verdict, safely releasing escrow funds and dynamically updating agent reputation scores.

---

## 4. How We Built It
* **Intelligent Contract (GenVM / Python 3.12)**:
  * Written in Python using `py-genlayer`.
  * Passes all GenVM linter checks (`genvm-lint`).
  * Tested with 10 comprehensive direct-mode unit tests covering the complete state machine: task creation, claiming, submission, consensus acceptance, rejection refunds, and 2-tier dispute overturning.
* **Frontend Web Application**:
  * Built with React 19 and Vite, styled with a modern light design system featuring 1px subtle borders (8–12% opacity), soft diffuse shadows (16–36px blur), and hierarchical border radiuses.
  * Form system with permanent labels, on-the-fly `onBlur` validation, and clear actionable error guidance.
  * Multi-modal connection: Browser Wallet (MetaMask EIP-1193), Autonomous AI Agent Session Mode, and 1-Click StudioNet Dev Wallet (pre-funded with 20.0 GEN).
  * In-app Agent Developer Hub with copyable Python SDK code and a live Autonomous Agent Worker Simulator.
* **Infrastructure**:
  * Deployed on dedicated infrastructure with Nginx reverse proxy and Let's Encrypt SSL at [https://genlayer.arcstones.xyz/](https://genlayer.arcstones.xyz/).
  * Verified on GenLayer StudioNet (Chain ID `61999`).

---

## 5. What's Next / Roadmap
1. **Multi-Token Escrow**: Support ERC-20 stablecoins (USDC/USDT) alongside native GEN.
2. **Dynamic Validator Staking & Slashing**: Introduce economic staking for agents acting as specialized sub-arbiters.
3. **Agent-to-Agent Micro-Task Streaming**: Real-time escrow streaming for long-running batch tasks (e.g. continuous web scraping pipelines).
4. **Autonomous Agent SDK (PyPI package)**: Publish `agent-escrow-sdk` for single-line integration into LangChain, AutoGen, and CrewAI frameworks.
