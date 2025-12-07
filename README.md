# Scalar - Financial Bodyguard 🛡️

> **Multi-Agent AI System protecting Indians 35-80+ from financial fraud**
> Built with **Google Agent Development Kit (ADK)** + **Gemini AI**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Google ADK](https://img.shields.io/badge/Google-ADK-orange.svg)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0-green.svg)](https://ai.google.dev)

## 🎯 Problem

- **₹1,000+ Crore** lost to UPI fraud in 2024
- **₹3,000+ Crore** lost to digital arrest scams  
- **13.4 Lakh** fraud cases reported
- Elderly Indians are primary targets

## 🛡️ Solution

A multi-agent AI system using **Google ADK** that:
- Analyzes suspicious messages in real-time
- Uses 7 specialized fraud detection tools
- Provides bilingual warnings (English + Hindi)
- Matches against 12 real-world scam trajectories

---

## 🚀 Quick Start

### 1. Install
```bash
pip install google-adk
```

### 2. Set API Key
```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### 3. Run ADK Web UI
```bash
cd scalar_agent
adk web
```

### 4. Open Browser
```
http://127.0.0.1:8000
```

---

## 🤖 How It Uses Google ADK

```python
from google.adk.agents import Agent  # Official Google ADK

# 1. Define tools as Python functions
def detect_upi_scam(message: str) -> dict:
    """Detects UPI fraud patterns."""
    # Pattern matching + risk scoring
    return {"risk_score": 0.95, "threats": [...]}

# 2. Create Agent with Gemini model
root_agent = Agent(
    name="financial_bodyguard",
    model="gemini-2.0-flash",
    instruction="You protect users from fraud...",
    tools=[detect_upi_scam, detect_phishing, ...]  # Functions → AI tools!
)

# 3. Run with: adk web
```

**ADK automatically:**
- Converts Python functions to Gemini tools
- Manages conversation context
- Provides web UI for testing

---

## 🔧 7 Fraud Detection Tools

| Tool | Purpose | Risk Detection |
|------|---------|----------------|
| `detect_upi_scam` | UPI collect, QR, prize scams | Pay-to-receive tricks |
| `detect_kyc_phishing` | Fake KYC, APK malware | Malicious links |
| `detect_police_impersonation` | Digital arrest, fake CBI | Authority scams |
| `decode_loan_agreement` | Hidden loan fees | Foreclosure traps |
| `decode_insurance_policy` | Policy exclusions | Coverage gaps |
| `detect_investment_fraud` | Ponzi, crypto scams | Impossible returns |
| `get_emergency_contacts` | Helpline numbers | 1930, RBI, SEBI |

---

## 📂 Project Structure

```
├── scalar_agent/          # ADK Agent (run: adk web)
│   └── __init__.py        # Agent + 7 tools
│
├── agents/                # Extended implementations
├── core/                  # Framework utilities
├── data/                  # 12 fraud trajectories
├── web/                   # Three.js 3D visualization
├── docker/                # Container deployment
│
├── requirements.txt
└── README.md
```

---

## 🎮 Test Messages

Try these in the ADK chat:

| Scam Type | Test Message |
|-----------|--------------|
| UPI Scam | "You won Rs 50,000! Accept collect request" |
| Digital Arrest | "This is CBI, pay Rs 2 lakh or arrest" |
| KYC Phishing | "KYC expired, download sbi-update.apk" |
| Investment | "15% monthly guaranteed crypto returns" |

---

## 📊 Fraud Trajectories

12 real-world patterns from Reddit, Twitter, Supreme Court cases:

1. UPI Collect Scam
2. Digital Arrest
3. Fake KYC APK
4. Fake Customer Care
5. Jumped Deposit
6. Electricity Threat
7. Crypto Investment
8. Loan Pre-Approval
9. Parcel Drug Scam
10. Insurance Refund
11. SIM Swap
12. QR Code Scam

---

## 📞 Emergency Contacts

| Service | Contact |
|---------|---------|
| Cyber Crime Helpline | **1930** |
| Online Portal | cybercrime.gov.in |
| RBI Sachet | sachet.rbi.org.in |
| SEBI Scores | 1800-227-227 |

---

## 🛠️ Tech Stack

- **AI Framework:** Google ADK + Gemini 2.0
- **Backend:** Python, FastAPI
- **Frontend:** Three.js 3D Visualization
- **Deployment:** Docker

---

## 📜 License

MIT License - See [LICENSE](LICENSE)

---

**Built with ❤️ to protect elders from financial fraud**

*Report scams: 1930 | cybercrime.gov.in*
