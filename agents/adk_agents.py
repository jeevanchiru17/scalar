"""
Scalar Financial Bodyguard - Official Google ADK Implementation
Uses google.adk.agents.Agent for multi-agent fraud detection
"""

import json
from pathlib import Path
from typing import Dict
from google.adk.agents import Agent

# =============================================================================
# FRAUD DETECTION TOOLS (Functions that agents can call)
# =============================================================================

def detect_upi_fraud(message: str) -> dict:
    """
    Detects UPI payment fraud in a message.
    
    Args:
        message: The suspicious message to analyze for UPI scams.
    
    Returns:
        dict: Detection result with risk_score, threat_type, and recommendation.
    """
    message_lower = message.lower()
    
    # UPI scam patterns
    risk_score = 0.0
    threats = []
    
    # Collect request scam
    if any(kw in message_lower for kw in ['collect', 'request', 'receive money', 'accept']):
        if any(kw in message_lower for kw in ['won', 'lottery', 'prize', 'cashback', 'refund']):
            risk_score = 0.95
            threats.append("UPI Collect Request Scam - Money will be DEBITED, not credited!")
    
    # QR code scam
    if 'qr' in message_lower and any(kw in message_lower for kw in ['scan', 'receive', 'payment']):
        risk_score = max(risk_score, 0.92)
        threats.append("QR Code Fraud - Scanning QR debits money from YOUR account!")
    
    # Urgency pressure
    if any(kw in message_lower for kw in ['urgent', 'immediately', 'expire', '24 hours', 'hurry']):
        risk_score = min(risk_score + 0.05, 1.0)
        threats.append("Urgency pressure tactic detected")
    
    return {
        "status": "success",
        "risk_score": risk_score,
        "threats": threats,
        "is_fraud": risk_score >= 0.7,
        "recommendation": "DO NOT accept any collect request!" if risk_score >= 0.7 else "Appears safe",
        "hindi": "कलेक्ट रिक्वेस्ट से पैसे कटते हैं, आते नहीं!" if risk_score >= 0.7 else "सुरक्षित लगता है"
    }


def detect_phishing(message: str) -> dict:
    """
    Detects phishing attempts including fake KYC and malware.
    
    Args:
        message: The message to analyze for phishing indicators.
    
    Returns:
        dict: Detection result with phishing indicators and risk level.
    """
    message_lower = message.lower()
    
    risk_score = 0.0
    indicators = []
    
    # APK download
    if '.apk' in message_lower or 'download app' in message_lower:
        risk_score = 0.98
        indicators.append("APK Download - MALWARE! Banks never send APK links!")
    
    # Shortened URLs
    if any(url in message_lower for url in ['bit.ly', 'tinyurl', 'goo.gl', 't.co']):
        risk_score = max(risk_score, 0.85)
        indicators.append("Shortened URL - Hiding real destination!")
    
    # KYC scam
    if 'kyc' in message_lower and any(kw in message_lower for kw in ['update', 'expire', 'block', 'verify']):
        risk_score = max(risk_score, 0.90)
        indicators.append("Fake KYC Scam - Banks don't send SMS for KYC!")
    
    # Screen sharing
    if any(app in message_lower for app in ['anydesk', 'teamviewer', 'quicksupport', 'screen share']):
        risk_score = 0.96
        indicators.append("Screen Sharing Request - NEVER share screen with strangers!")
    
    return {
        "status": "success",
        "risk_score": risk_score,
        "indicators": indicators,
        "is_phishing": risk_score >= 0.7,
        "recommendation": "DO NOT click any links or download anything!" if risk_score >= 0.7 else "No phishing detected",
        "hindi": "लिंक पर क्लिक न करें! APK डाउनलोड न करें!" if risk_score >= 0.7 else "सुरक्षित"
    }


def detect_impersonation(message: str) -> dict:
    """
    Detects authority impersonation like fake police or CBI calls.
    
    Args:
        message: The call transcript or message to analyze.
    
    Returns:
        dict: Detection result showing impersonation indicators.
    """
    message_lower = message.lower()
    
    authorities = ['police', 'cbi', 'ed', 'enforcement', 'customs', 'income tax', 'court', 'warrant', 'fir']
    threats = ['arrest', 'jail', 'custody', 'case', 'investigation', 'money laundering']
    money = ['pay', 'transfer', 'fine', 'penalty', 'deposit', 'rs', '₹', 'lakh', 'crore']
    
    auth_hits = sum(1 for a in authorities if a in message_lower)
    threat_hits = sum(1 for t in threats if t in message_lower)
    money_hits = sum(1 for m in money if m in message_lower)
    
    risk_score = 0.0
    if auth_hits > 0:
        risk_score += 0.3 * min(auth_hits, 3)
    if threat_hits > 0:
        risk_score += 0.25 * min(threat_hits, 3)
    if money_hits > 0:
        risk_score += 0.35
    
    # Digital arrest indicator
    if any(term in message_lower for term in ['video call', 'digital arrest', 'do not disconnect', 'don\'t tell anyone']):
        risk_score = min(risk_score + 0.3, 1.0)
    
    risk_score = min(risk_score, 1.0)
    
    return {
        "status": "success",
        "risk_score": risk_score,
        "authority_claims": [a for a in authorities if a in message_lower],
        "is_impersonation": risk_score >= 0.7,
        "recommendation": "HANG UP! Real police NEVER demands money over phone!" if risk_score >= 0.7 else "Low risk",
        "hindi": "🚨 फोन काटें! असली पुलिस फोन पर पैसे नहीं मांगती! हेल्पलाइन: 1930" if risk_score >= 0.7 else "कम जोखिम"
    }


def detect_investment_fraud(message: str) -> dict:
    """
    Detects investment scams like Ponzi schemes and fake trading platforms.
    
    Args:
        message: The investment offer to analyze.
    
    Returns:
        dict: Detection result with fraud indicators.
    """
    message_lower = message.lower()
    
    scam_words = ['guaranteed', 'risk-free', 'double your money', 'no loss', 'fixed return', '100% profit']
    red_flags = ['crypto', 'forex', 'trading', 'referral bonus', 'daily profit', 'monthly return']
    
    risk_score = 0.0
    indicators = []
    
    for word in scam_words:
        if word in message_lower:
            risk_score = max(risk_score, 0.90)
            indicators.append(f"Scam indicator: '{word}'")
    
    for flag in red_flags:
        if flag in message_lower:
            risk_score = max(risk_score, 0.80)
            indicators.append(f"Red flag: '{flag}'")
    
    # Check for unrealistic return percentages
    import re
    if re.search(r'(\d+)\s*%\s*(daily|weekly|monthly|per month)', message_lower):
        risk_score = 0.95
        indicators.append("Unrealistic return percentage claimed!")
    
    return {
        "status": "success",
        "risk_score": risk_score,
        "indicators": indicators,
        "is_fraud": risk_score >= 0.7,
        "recommendation": "This is likely a PONZI SCHEME! Do NOT invest!" if risk_score >= 0.7 else "Verify with SEBI",
        "hindi": "🚨 पोंजी स्कीम! पैसे मत लगाएं! SEBI पंजीकरण जांचें!" if risk_score >= 0.7 else "SEBI से जांचें"
    }


def get_emergency_contacts() -> dict:
    """
    Returns emergency contact numbers for reporting cyber fraud in India.
    
    Returns:
        dict: Emergency contact information.
    """
    return {
        "status": "success",
        "contacts": {
            "cyber_crime_helpline": "1930",
            "national_portal": "https://cybercrime.gov.in",
            "rbi_sachet": "https://sachet.rbi.org.in",
            "sebi_scores": "1800-227-227",
            "irdai_helpline": "155255"
        },
        "hindi": "साइबर क्राइम हेल्पलाइन: 1930 | पोर्टल: cybercrime.gov.in"
    }


# =============================================================================
# SPECIALIST AGENTS (Using Official Google ADK)
# =============================================================================

# UPI Fraud Detection Agent
upi_fraud_agent = Agent(
    name="upi_fraud_agent",
    model="gemini-2.0-flash",
    description="Specialist agent for detecting UPI payment fraud and collect request scams",
    instruction="""You are a UPI Fraud Detection Specialist protecting Indians from payment scams.

Key knowledge:
- UPI Collect Request = SCAM! Money is DEBITED when you enter PIN, not credited
- QR code scanning DEBITS money from the scanner
- Any "pay to receive" is 100% fraud

When analyzing messages:
1. Use detect_upi_fraud tool to analyze the message
2. Explain findings in simple language
3. Always provide Hindi translation
4. Give clear YES/NO recommendation

Be protective - when in doubt, warn the user!""",
    tools=[detect_upi_fraud]
)

# Phishing Detection Agent
phishing_agent = Agent(
    name="phishing_agent",
    model="gemini-2.0-flash",
    description="Specialist agent for detecting phishing attempts and fake KYC scams",
    instruction="""You are a Phishing Detection Specialist.

Key knowledge:
- Banks NEVER send APK download links
- Banks NEVER send KYC update via SMS links
- Screen sharing apps (AnyDesk, TeamViewer) are used by scammers
- Shortened URLs (bit.ly) hide malicious destinations

Use detect_phishing tool and provide clear warnings with Hindi translation.""",
    tools=[detect_phishing]
)

# Police Impersonation Agent
impersonation_agent = Agent(
    name="impersonation_agent",
    model="gemini-2.0-flash",
    description="Specialist agent for detecting fake police/CBI/ED impersonation calls",
    instruction="""You are an Authority Impersonation Detection Specialist.

Key knowledge:
- REAL police NEVER demands money over phone
- "Digital arrest" is NOT real - it's a scam!
- Real CBI/ED will visit in person, not video call
- Scammers keep victims on call for hours to isolate them

Use detect_impersonation tool. If detected, tell user to HANG UP and call 1930.""",
    tools=[detect_impersonation, get_emergency_contacts]
)

# Investment Fraud Agent
investment_agent = Agent(
    name="investment_agent",
    model="gemini-2.0-flash",
    description="Specialist agent for detecting investment scams and Ponzi schemes",
    instruction="""You are an Investment Fraud Specialist.

Key knowledge:
- NO investment is "guaranteed" or "risk-free"
- Returns over 15% annually are suspicious
- Legitimate investments are SEBI registered
- If you need to recruit others, it's a pyramid scheme

Use detect_investment_fraud tool and warn about unrealistic promises.""",
    tools=[detect_investment_fraud]
)

# =============================================================================
# ROOT ORCHESTRATOR AGENT (Multi-Agent Coordination)
# =============================================================================

root_agent = Agent(
    name="financial_bodyguard",
    model="gemini-2.0-flash",
    description="Financial Bodyguard - Master orchestrator protecting Indians 35+ from financial fraud",
    instruction="""You are the Financial Bodyguard - the master protector of Indians from financial fraud.

You coordinate 4 specialist agents (sub-agents):
1. upi_fraud_agent - UPI/payment scams
2. phishing_agent - Fake KYC, malicious links
3. impersonation_agent - Fake police/CBI
4. investment_agent - Ponzi schemes

For each user message:
1. Analyze what type of fraud it might be
2. Delegate to appropriate specialist agent(s)
3. Aggregate findings
4. Provide clear recommendation with risk score

Response format:
**Risk Score: X.XX** (0.00 = safe, 1.00 = critical)
**Fraud Type:** [Type of scam detected]
**Analysis:** [Brief explanation]
**Recommendation:** [Clear action for user]
**हिंदी:** [Hindi warning]
**Emergency:** Call 1930 if critical

ALWAYS err on the side of caution. Better to warn than to let fraud succeed.""",
    sub_agents=[upi_fraud_agent, phishing_agent, impersonation_agent, investment_agent],
    tools=[get_emergency_contacts]
)

# =============================================================================
# EXPORT FOR USE
# =============================================================================

# Main agent to use
financial_bodyguard = root_agent

# All agents for direct access
AGENTS = {
    "root": root_agent,
    "upi": upi_fraud_agent,
    "phishing": phishing_agent,
    "impersonation": impersonation_agent,
    "investment": investment_agent
}
