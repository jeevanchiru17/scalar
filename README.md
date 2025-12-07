# Scalar - Financial Bodyguard

> **Multi-Agent AI System protecting Indians 35-80+ from financial fraud**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Problem

- **₹1,000+ Crore** lost to UPI fraud in 2024
- **₹3,000+ Crore** lost to digital arrest scams  
- **13.4 Lakh** fraud cases reported
- Elderly Indians are primary targets

## 🛡️ Solution

A multi-agent system using **Google ADK** and **Gemini AI** that:
- Analyzes suspicious messages in real-time
- Coordinates 5 specialist fraud detection agents
- Provides bilingual warnings (English + Hindi)
- Matches against 12 real-world scam trajectories

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│            FINANCIAL BODYGUARD ORCHESTRATOR             │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │   UPI   │ │Phishing │ │ Police  │ │Document │       │
│  │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│                    ┌─────────┐                          │
│                    │ Invest  │                          │
│                    │  Agent  │                          │
│                    └─────────┘                          │
└─────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
scalar/
├── agents/           # Specialist agents
├── core/             # ADK framework + Gemini client
├── data/             # Fraud trajectories (12 patterns)
├── api/              # FastAPI service
├── web/              # Three.js 3D visualization
├── docker/           # Container configs
└── demo.py           # Demo script
```

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/scalar.git
cd scalar

# Install
pip install -r requirements.txt

# Set API key
echo "GEMINI_API_KEY=your_key" > .env

# Run demo
python demo.py

# Open UI
open web/index.html
```

## 🤖 Specialist Agents

| Agent | Expertise | Risk Detection |
|-------|-----------|----------------|
| 📱 **UPI Agent** | Collect scams, QR fraud | Pay-to-receive tricks |
| 🔗 **Phishing Agent** | Fake KYC, APK malware | Malicious links |
| 👮 **Impersonation Agent** | Fake CBI/Police | Digital arrest |
| 📈 **Investment Agent** | Ponzi, crypto scams | Guaranteed returns |
| 📄 **Document Agent** | Loan/insurance terms | Hidden fees |

## 📊 Fraud Trajectories

Real-world scam patterns from Reddit, Twitter, Supreme Court cases:

1. **T001** - UPI Collect Request Scam
2. **T002** - Digital Arrest (CBI/ED impersonation)
3. **T003** - Fake KYC APK Download
4. **T004** - Fake Customer Care
5. **T005** - Jumped Deposit Scam
6. **T006** - Electricity Bill Threat
7. **T007** - Crypto Investment Fraud
8. **T008** - Loan Pre-Approval Scam
9. **T009** - Parcel/Courier Drug Scam
10. **T010** - Insurance Premium Refund
11. **T011** - SIM Swap Fraud
12. **T012** - QR Code Payment Scam

## 🐳 Docker

```bash
cd docker
docker-compose up --build
```

Access: `http://localhost:3000`

## 📞 Emergency Contacts

- **Cyber Crime Helpline:** 1930
- **Portal:** https://cybercrime.gov.in
- **RBI Sachet:** https://sachet.rbi.org.in
- **IRDAI:** 155255

## 🛠️ Tech Stack

- **AI:** Google Gemini, ADK
- **Backend:** Python, FastAPI
- **Frontend:** Three.js, HTML/CSS
- **Deployment:** Docker, Nginx

## 📜 License

MIT License - See [LICENSE](LICENSE)

---

**Built with ❤️ to protect elders from financial fraud**
