# Forensic Eye — Facial Recognition & Web3 Immutability Monorepo

[![Polygon Amoy Testnet](https://img.shields.io/badge/Blockchain-Polygon%20Amoy%20(Chain%20ID%2080002)-8247E5?style=flat&logo=polygon)](https://amoy.polygonscan.com)
[![FastAPI Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](http://localhost:8000/docs)
[![Vite React Frontend](https://img.shields.io/badge/Frontend-Vite%20%2B%20React-61DAFB?style=flat&logo=react)](http://localhost:5173)
[![IPFS Storage](https://img.shields.io/badge/Storage-IPFS%20%2F%20Kubo-65C2CB?style=flat&logo=ipfs)](https://ipfs.io)

**Forensic Eye** is a production-grade full-stack monorepo featuring a **FastAPI backend** (`/backend`) and a **Vite + React frontend** (`/frontend`). It detects faces, extracts 128-dimensional embedding vectors, performs real reverse image search across web & social media platforms (Twitter/X, Instagram, LinkedIn, Reddit), verifies visual match authenticity using cosine similarity, and commits tamper-evident verification records to IPFS and the Polygon Amoy blockchain.

---

## 🌟 The 3 "X-Factor" Innovations That Elevate This Submission

Most hackathon entries build a linear pipeline that treats the blockchain as a simple timestamp log and publishes raw biometrics. **Forensic Eye** solves the core real-world challenges:

### 1. 🛡️ Privacy-Preserving Biometric Commitment (GDPR Compliant)
- **Problem**: Storing raw 128-d face floating-point coordinates on IPFS/Polygon creates a permanent privacy compliance breach under GDPR / PII regulations.
- **Our Solution**: **Salted Cryptographic Vector Commitment**. The pipeline computes:
  $$\text{DataHash} = \text{SHA256}(\text{FaceEmbedding}_{128d} + \text{PostURL} + \text{Timestamp} + \text{Salt})$$
  Only the 32-byte hash (`bytes32 dataHash`) and IPFS metadata CID are stored on-chain. **Zero raw biometric coordinates are ever exposed publicly.**

### 2. ⚡ Facial Cosine Similarity Verification Gate (Phase 3)
- **Problem**: Web reverse search engines (Google Lens / SerpAPI) frequently return visually similar background images (e.g. matching jackets or room furniture) that DO NOT match the subject's face.
- **Our Solution**: **Automated Secondary Verification**. Our pipeline automatically fetches candidate page thumbnails, detects candidate faces, recomputes 128-d embeddings, and evaluates **Cosine Similarity ($\ge 65\%$)**. Only verified facial matches are permitted for on-chain submission.

### 3. 🔥 Live Interactive "Tamper Attack" Showcase (`/api/tamper-demo`)
- **Problem**: Standard demo recordings show static green checkmarks without proving that blockchain immutability actively prevents data tampering.
- **Our Solution**: **Live Cryptographic Proof Breakdown**. The UI includes an interactive **"Run Tamper Test"** trigger that deliberately mutates 1 byte of stored metadata, recomputes the SHA-256 hash, and queries `Verification.sol` to **prove on-camera that verification FAILS (returns `FALSE`)**.

---

## 📐 Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Vite + React Frontend                            │
│           (3-Step Stepper UI: Face Scan ──▶ Matches ──▶ On-Chain)           │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ REST API Proxy (:5173 -> :8000)
┌────────────────────────────────────▼────────────────────────────────────────┐
│                               FastAPI Backend                               │
│                                (/backend/main.py)                           │
├───────────────────┬───────────────────┬───────────────────┬─────────────────┤
│    Face Module    │   Search Module   │    Web3 Chain     │   Job Engine    │
│  (encode.py)      │ (reverse_search)  │  (web3_client)    │(scan_pipeline)  │
│  • 128-d Vector   │ • SerpAPI / Lens  │ • IPFS Upload     │ • Phase 1-3 Scan│
│  • Quality/Blur   │ • Social Filter   │ • Verification.sol│ • Phase 4 Commit│
└─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐┌──────────────────┐┌─────────────────────────────────────┐
│   OpenCV / dlib  ││ SerpAPI / Vision ││ IPFS & Polygon Amoy Testnet         │
│  Face Embeddings ││   Search Engine  ││ (Verification.sol - Chain ID 80002) │
└──────────────────┘└──────────────────┘└─────────────────────────────────────┘
```

---

## 📹 Script for 90-Second Screen Recording

| Time | Visual Action | What to Say in Narration |
| :--- | :--- | :--- |
| **0:00 - 0:15** | Open `http://localhost:5173`. Upload or capture face photo in Step 1. | *"Welcome to Forensic Eye. Most identity tools log data to the web, but can you prove a social media post wasn't altered? Watch our end-to-end pipeline."* |
| **0:15 - 0:35** | Click **Scan Face & Search Web**. Progress bar shows Phase 1–3 polling. | *"Phase 1 extracts a 128-d face vector. Phase 2 executes live reverse search across social platforms. Phase 3 automatically re-runs facial cosine similarity on candidate thumbnails to guarantee a genuine match above 65%."* |
| **0:35 - 0:55** | Step 2 candidate cards appear with `92.2% Cosine Match`. Click **Verify & Record On-Chain**. | *"We select a verified candidate match and submit a transaction to Polygon Amoy Testnet. Our pipeline pushes metadata to IPFS and records the salted dataHash in Verification.sol."* |
| **0:55 - 1:15** | Step 3 displays transaction hash, IPFS CID, and clickable Polygonscan link. | *"The match record is now immutable on Polygon Amoy. Here is the block transaction hash, IPFS CID, and smart contract verification state."* |
| **1:15 - 1:30** | Click the red **"Run Tamper Test"** button. Red alert flashes showing hash mismatch. | *"Here is our standout feature: when we deliberately mutate 1 byte of the stored record, recomputed SHA-256 fails on-chain verification instantly. Thank you!"* |

---

## ⚡ Smart Contract & Blockchain Details

- **Blockchain Network**: Polygon Amoy Testnet
- **Chain ID**: `80002`
- **RPC Provider**: `https://rpc-amoy.polygon.technology`
- **Smart Contract File**: [backend/chain/contracts/Verification.sol](file:///d:/DEV/hhgoa_task3/backend/chain/contracts/Verification.sol)
- **Deployment Script**: [backend/chain/scripts/deploy.js](file:///d:/DEV/hhgoa_task3/backend/chain/scripts/deploy.js)
- **Block Explorer**: [https://amoy.polygonscan.com](https://amoy.polygonscan.com)

### Contract Interface (`Verification.sol`)
```solidity
event RecordStored(bytes32 indexed dataHash, string ipfsCID, address indexed submitter, uint256 timestamp);

function record(bytes32 dataHash, string memory ipfsCID) public;
function getRecord(bytes32 dataHash) public view returns (string memory ipfsCID, address submitter, uint256 timestamp, bool exists);
```

---

## 🚀 How to Run the Project

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

---

### 1. Environment Setup

Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```

Set your configuration in `.env`:
```env
SERPAPI_KEY=your_serpapi_key_here
WEB3_PROVIDER_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your_polygon_amoy_private_key
CONTRACT_ADDRESS=0x82fA0...your_deployed_contract_address
```

---

### 2. Run Backend Server (FastAPI)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3. Run Frontend Application (Vite + React)

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
- **Web App URL**: [http://localhost:5173](http://localhost:5173)

---

### 4. CLI Verification & Tamper Demo Scripts

```bash
cd backend
# 1. Face Encoding Test
.\.venv\Scripts\python.exe face/test_encode.py

# 2. Reverse Search & Social Filter Test
.\.venv\Scripts\python.exe search/test_reverse_search.py

# 3. IPFS & Blockchain Recording Test
.\.venv\Scripts\python.exe chain/test_chain.py

# 4. Standout Tamper Attack Demo CLI Script
.\.venv\Scripts\python.exe chain/test_tamper_demo.py
```

---

## ⚠️ Known Limitations

1. **API Quota & Rate Limits**: SerpAPI Google Lens endpoints operate within free tier quotas; fallbacks to Google Vision `WEB_DETECTION` ensure test continuity.
2. **Face Match Thresholds**: Cosine similarity uses a default cutoff ($\ge 0.65$). Severe lighting distortion or extreme angles may yield false negatives.
3. **Testnet Non-Binding Scope**: Records are published to Polygon Amoy Testnet (`Chain ID 80002`) for proof-of-concept verification.

---

## 📜 License
MIT License — Hacker House Goa 2026.
