# EcoChain — Decentralized Sustainability Tracker

**EcoChain** is a Web3 sustainability tracker built on the ASI Alliance stack (Fetch.ai + SingularityNET). Users upload energy bills, EV receipts, or other proofs; autonomous agents (uAgents) verify the data, MeTTa performs structured reasoning to calculate carbon impact, and verified users are awarded **EcoCredits** (ERC‑20 tokens). Proofs are stored off‑chain (IPFS/Fetch Storage) and minimal metadata/hashes are recorded on‑chain for transparency.

---

## TL;DR

* **What:** A decentralised app that verifies sustainability actions and mints EcoCredits.
* **Why:** Makes carbon tracking verifiable, privacy‑minded, and rewarding using autonomous agents and structured reasoning.
* **Built with:** uAgents (Fetch.ai), ASI:One Chat, MeTTa, IPFS/Fetch Storage, Solidity ERC‑20 token.

---

## Key Features

* Chat‑driven onboarding and interactions via **ASI:One**.
* Modular autonomous agents (UserAgent, DocumentScanner/VerifierAgent, MeTTa Reasoner, CreditMintingAgent).
* Immutable proof storage on **IPFS** / Fetch Storage with on‑chain proof (CID + metadata).
* Minting EcoCredits (ERC‑20) to validated users on an EVM compatible chain (Fetch.ai or other).
* Agent listing & discovery via **Agentverse**.

---

## Motivation

Individuals and small organisations want to measure and get rewarded for sustainable behaviour but face two core problems: (1) fragmented, hard‑to‑verify data sources and (2) centralized systems that lack transparency. EcoChain solves this with agentic automation, rule‑based reasoning (MeTTa), and immutable proofs on decentralized storage and ledgers.

---

## Architecture (Overview)

```
                ┌────────────────────────┐
                │        User            │
                │  (Web App / ASI Chat)  │
                └──────────┬─────────────┘
                           │
                           ▼
                ┌────────────────────────┐
                │      UserAgent          │
                │ (Represents user ID,    │
                │  handles consent, chat) │
                └──────────┬─────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│DocumentScanner │  │  DataAgent     │  │ VerifierAgent  │
│ Agent          │  │ (API/Manual)   │  │ (MeTTa logic)  │
│ - Reads PDFs   │  │ - Collects raw │  │ - Validates &  │
│ - Extracts kWh │  │   usage data   │  │   reasons data │
└────────────────┘  └────────────────┘  └────────────────┘
         │                 │                 │
         └────────────┬────┴──────┬──────────┘
                      ▼           ▼
              ┌────────────────────────┐
              │     MeTTa Engine        │
              │ - Structured reasoning  │
              │ - Knowledge graph       │
              └──────────┬─────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │     CreditAgent         │
              │ - Mints EcoCredits      │
              │   on Fetch Network      │
              │ - Posts summary to      │
              │   Agentverse listing    │
              └──────────┬─────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │   Fetch Network Ledger │
              │  (Stores verifiable    │
              │   footprint + credits) │
              └────────────────────────┘
```

---

## Components & Responsibilities

### Frontend (React)

* Wallet connect (MetaMask / WalletConnect / Keplr)
* Chat UI connected to ASI:One (routes messages to UserAgent)
* File upload (bills/receipts) and dashboard (footprint history, EcoCredits balance)

### UserAgent (Python / uAgents)

* Entry point for user interactions from the chat UI
* Manages sessions, permissions (consent) and routes tasks to other agents

### DocumentScannerAgent

* Parses uploaded files (PDF/image) using OCR or accepts structured JSON (MVP)
* Produces cleaned data: `{ provider, date, kWh, meter_id, ... }`

### VerifierAgent

* Validates document structure and metadata
* Uploads raw file to IPFS or Fetch Storage and returns CID
* Emits a verification payload: `{cid, user, kWh, date, signature, verified: true}`

### MeTTa ReasonerAgent

* Encodes sustainability rules and emission factors in MeTTa
* Computes CO₂e and derives credit amounts
* Produces a provenance record that can be hashed and stored

### CreditMintingAgent

* Receives validated claims & provenance hash
* Calls ERC‑20 `mint(to, amount)` function on the deployed contract (only authorized minter)
* Logs transaction hash and updates user dashboard

### Smart Contracts (Solidity)

* `EcoCreditToken.sol` — ERC‑20 with minter role (OpenZeppelin)
* Optional `EcoReportRegistry.sol` — store minimal claim metadata or emit events for indexing

### Storage & Indexing

* **IPFS / Fetch Storage** for raw files and reasoning proofs
* On‑chain stores only hashes/CIDs, timestamps and minimal numerical metadata
* Agentverse for discoverability (agent manifests + README)

---

## Tech Stack

* **Frontend:** React, Tailwind (optional), Vite or Next.js, WalletConnect / web3modal, `ethers.js`
* **Agents / Backend:** Python 3.10+, uAgents SDK, FastAPI or Flask
* **Reasoning:** MeTTa (SingularityNET) via Python bindings or microservice
* **Storage:** IPFS (pinning via Pinata or PinataPy) or Fetch Storage
* **Smart Contracts:** Solidity, Hardhat (or Truffle), OpenZeppelin libraries
* **Blockchain:** Fetch.ai EVM (preferred) or compatible testnet (Goerli / Sepolia) for prototyping
* **Dev Tools:** Docker, GitHub Actions (CI), ngrok (local testing with public endpoints)

---

## Quick Start (Developer Guide)

> These steps assume you have `node`, `npm`/`yarn`, `python`, and `docker` installed.

### 1. Clone repo

```bash
git clone <repo-url>
cd ecochain
```

### 2. Frontend (React)

```bash
cd frontend
npm install
# set .env (REACT_APP_API_URL, REACT_APP_CHAIN_ID etc.)
npm run dev
```

### 3. Backend & Agents (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# set env vars in .env (see below)\python -m backend.user_agent
# run other agents similarly (verifier, metta, minter)
```

### 4. IPFS (local / Pinata)

* Use Pinata or a local IPFS node. Example with Pinata: set `PINATA_API_KEY` and `PINATA_SECRET` in `.env` and use provided `storage_utils.py` to pin files.

### 5. Smart Contracts

```bash
cd contracts
npm install
# compile & test
npx hardhat compile
# configure networks in hardhat.config.js
npx hardhat run scripts/deploy.js --network <network>
```

* Use `ethers.js` or `web3.py` to interact with the deployed contract.

---

## Environment Variables (example `.env`)

```
# General
APP_HOST=https://your-app.example
PORT=8000

# IPFS / Pinata
PINATA_API_KEY=your_pinata_key
PINATA_SECRET=your_pinata_secret

# Web3 / RPC
RPC_URL=https://rpc.fetch.ai
PRIVATE_KEY=0x...
CONTRACT_ADDRESS=0x...

# ASI / Agentverse
AGENTVERSE_API_KEY=your_agentverse_key
ASI_API_ENDPOINT=https://asi1.ai/api
```

---

## MeTTa Rules (Example)

Below is a brief pseudo‑MeTTa snippet demonstrating an emission factor rule. Implement these in the MeTTa program used by the `MeTTa ReasonerAgent`.

```
(emission-factor electricity 0.4) ; kg CO2 per kWh
(emission-factor car 0.12)       ; kg CO2 per km
(define (calc-electricity kwh) (* kwh (emission-factor electricity)))
(define (calc-ev-charging kwh) (* kwh 0.05)) ; example EV factor
(define (credit-for-savings saved_kg) (floor (/ saved_kg 100))) ; 1 credit per 100 kg
```

Store a human‑readable proof of the reasoning and a hashed version of the proof (e.g., SHA‑256) on IPFS; store the hash on‑chain.

---

## Agentverse Registration (short)

1. Prepare an agent manifest and README for each agent.
2. Use the Fetch.ai SDK to register: `register_with_agentverse(identity, url, token, title, readme)`.
3. Publish endpoint URLs and ensure agents are reachable by ASI:One.

See Fetch.ai docs for exact API calls and required manifest format.

---

## Testing & Validation

* Unit test MeTTa rules (examples for edge cases).
* Simulate document uploads (sample PDFs / JSON fixtures) and run the full verification + minting pipeline in a dev environment.
* Use a local blockchain (Hardhat/Ganache) for contract tests before deploying to testnet.

---

## Roadmap (Suggested Sprints)

1. Chat foundation & UserAgent (week 1)
2. Document upload & OCR parsing (week 2)
3. VerifierAgent + IPFS integration (week 3)
4. MeTTa reasoning + credit calculation (week 4)
5. Smart contract implementation & deploy (week 5)
6. CreditMintingAgent & full E2E demo (week 6)
7. Agentverse registration & polish (week 7)

---

## Contributor Guide

* Follow the repo branching strategy: `main` for stable demo, `dev` for ongoing work, feature branches for PRs.
* Run linters and tests before PR.
* Document MeTTa rules and agent manifests thoroughly — judges will review integration and documentation.

---

## Security & Privacy Considerations

* **Do not store sensitive PII on‑chain.** Hashes/CIDs only.
* **Offer encryption** for files before uploading to IPFS (user holds decryption key) if privacy is required.
* **Limit minting rights** to the CreditMintingAgent and consider multi‑agent attestation for high‑value mints.

---

## Resources & Links

* Fetch.ai Innovation Lab docs: [https://innovationlab.fetch.ai/resources/docs/intro](https://innovationlab.fetch.ai/resources/docs/intro)
* uAgents docs & examples: [https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation)
* Agentverse docs: [https://innovationlab.fetch.ai/resources/docs/agentverse/](https://innovationlab.fetch.ai/resources/docs/agentverse/)
* MeTTa tutorials: [https://metta-lang.dev/docs/learn/tutorials/python_use/metta_python_basics.html](https://metta-lang.dev/docs/learn/tutorials/python_use/metta_python_basics.html)
* Example agent integration: [https://github.com/fetchai/innovation-lab-examples/tree/main/web3/singularity-net-metta](https://github.com/fetchai/innovation-lab-examples/tree/main/web3/singularity-net-metta)

---

## License

This project is released under the MIT License. See `LICENSE`.

---

## Contact

Project lead: **You** (update README with your contact/email/links).
Questions or feature ideas? Create an issue in this repo.

---

*Generated for the EcoChain project to support development, demo, and hackathon submission. Modify as needed for your final repo and presentation.*
