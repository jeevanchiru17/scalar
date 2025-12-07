# Building Scalar: An AI-Powered Financial Bodyguard for India 🛡️

*How I built a multi-agent fraud detection system using Google's Agent Development Kit (ADK) and Gemini AI to protect Indians from financial scams*

---

## The Problem: A Nation Under Siege

Every day in India, thousands fall victim to sophisticated financial scams:

- **₹1,000+ Crore** lost to UPI fraud in 2024
- **₹3,000+ Crore** lost to "digital arrest" scams
- **13.4 Lakh** fraud cases reported
- Primary targets: **Adults aged 35-80+**, especially senior citizens

The scams have evolved. They're no longer obvious Nigerian prince emails. Today's fraudsters impersonate CBI officers on video calls, send fake KYC links that install malware, and manipulate UPI collect requests to drain bank accounts in seconds.

I decided to fight back with AI.

---

## The Solution: Scalar - Financial Bodyguard

**Scalar** is a multi-agent AI system that analyzes suspicious messages in real-time and warns users before they fall victim.

### What makes it special?

1. **7 Specialized Detection Tools** - Each trained on real scam patterns
2. **Bilingual Warnings** - English + Hindi for better reach
3. **12 Real-World Trajectories** - Based on Reddit, Twitter, and Supreme Court cases
4. **Built with Google ADK** - Using the latest Agent Development Kit

---

## How It Works: Google ADK in Action

The magic happens with **Google's Agent Development Kit (ADK)**. Here's the core pattern:

```python
from google.adk.agents import Agent

# Define a fraud detection tool as a simple function
def detect_upi_scam(message: str) -> dict:
    """Detects UPI payment fraud patterns."""
    # Pattern matching logic
    if "collect request" in message.lower() and "won" in message.lower():
        return {
            "risk_score": 0.95,
            "threat": "UPI Collect Scam",
            "warning": "Money will be DEBITED, not credited!"
        }
    return {"risk_score": 0.0}

# Create the agent with Gemini AI
root_agent = Agent(
    name="financial_bodyguard",
    model="gemini-2.0-flash",
    instruction="You protect Indians from financial fraud...",
    tools=[detect_upi_scam, detect_phishing, ...]
)
```

**That's it!** ADK automatically:
- Converts Python functions to Gemini tools
- Manages conversation context
- Provides a web UI for testing

Run it with:
```bash
adk web
```

---

## The 7 Fraud Detection Tools

| Tool | What It Catches |
|------|-----------------|
| `detect_upi_scam` | Collect requests, QR fraud, prize scams |
| `detect_kyc_phishing` | Fake KYC SMS, APK malware, fake bank links |
| `detect_police_impersonation` | Digital arrest, fake CBI/ED calls |
| `decode_loan_agreement` | Hidden fees, foreclosure traps |
| `decode_insurance_policy` | Exclusions, coverage gaps |
| `detect_investment_fraud` | Ponzi schemes, crypto scams |
| `get_emergency_contacts` | Helpline numbers (1930) |

---

## Real Scam Patterns: The 12 Trajectories

I collected real scam patterns from:
- Reddit r/india threads
- Twitter complaints
- Supreme Court cases
- Cybercrime reports

Here's an example - the **Digital Arrest Scam**:

```
1. Call from "CBI Officer" claiming your Aadhaar is linked to crime
2. Shown fake badge on video call
3. Told to stay on call ("digital arrest")
4. Kept isolated for hours
5. Forced to transfer to "RBI safe account"
```

**Reality:** Real police NEVER demands money over phone. Digital arrest is NOT a real thing.

---

## Sample Detection in Action

**User Input:**
> "I got a call from CBI saying my Aadhaar is linked to money laundering. They want Rs 2 lakh to cancel the arrest warrant."

**Scalar Response:**

```
Risk Score: 0.99
Fraud Type: Digital Arrest Scam

🚨 CRITICAL THREAT! This is 100% FRAUD!

Analysis:
This is a well-known "digital arrest" scam. Criminals are pretending 
to be CBI/ED officers to extort money. Real police:
- NEVER demands money over phone
- NEVER conducts arrests via video call
- NEVER asks you to stay on call

Recommendation:
HANG UP IMMEDIATELY! Do NOT transfer any money!

हिंदी में:
🚨 तुरंत फोन काटें! यह धोखाधड़ी है! असली पुलिस कभी फोन पर पैसे 
नहीं मांगती! "डिजिटल अरेस्ट" जैसी कोई चीज़ नहीं है!

Emergency: Call 1930 | cybercrime.gov.in
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         FINANCIAL BODYGUARD             │
│            (Root Agent)                 │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │   UPI   │  │Phishing │  │ Police  │ │
│  │  Tool   │  │  Tool   │  │  Tool   │ │
│  └─────────┘  └─────────┘  └─────────┘ │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  Loan   │  │Insurance│  │ Invest  │ │
│  │  Tool   │  │  Tool   │  │  Tool   │ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘
              ↓
       Gemini 2.0 Flash
              ↓
    User-friendly Response
    (English + Hindi)
```

---

## Getting Started

```bash
# Clone
git clone https://github.com/jeevanchiru17/scalar.git
cd scalar

# Install
pip install google-adk

# Set API key
echo "GOOGLE_API_KEY=your_key" > .env

# Run
cd scalar_agent
adk web
```

Open **http://127.0.0.1:8000** and start testing!

---

## Key Takeaways

1. **Google ADK makes agent development simple** - Define functions, attach to agent, done
2. **Pattern matching + AI = Powerful combination** - Fast local checks + intelligent responses
3. **Bilingual support is crucial for India** - Hindi warnings save lives
4. **Real data matters** - Scam patterns from real cases make detection accurate

---

## What's Next?

- [ ] Deploy to Google Cloud Run
- [ ] Add WhatsApp integration (most scams happen there)
- [ ] Build mobile app for real-time protection
- [ ] Train on more regional language scam patterns

---

## Resources

- **GitHub:** [github.com/jeevanchiru17/scalar](https://github.com/jeevanchiru17/scalar)
- **Google ADK Docs:** [google.github.io/adk-docs](https://google.github.io/adk-docs)
- **Report Scams:** 1930 | [cybercrime.gov.in](https://cybercrime.gov.in)

---

*Built with ❤️ to protect our elders from financial fraud*

**#GoogleADK #GeminiAI #CyberSecurity #India #FraudPrevention**
