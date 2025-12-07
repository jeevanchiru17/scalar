"""
Scalar Financial Bodyguard - Official Google ADK Agent
Complete fraud detection system with all tools
"""

import re
from typing import Optional
from google.adk.agents import Agent

# =============================================================================
# TOOL 1: UPI SCAM DETECTOR
# =============================================================================

def detect_upi_scam(message: str, amount: Optional[float] = None) -> dict:
    """
    Analyzes UPI transaction messages for fraud patterns including collect scams,
    prize fraud, refund tricks, and QR code manipulation.
    
    Args:
        message: The UPI-related message to analyze for scam indicators.
        amount: Optional transaction amount in rupees.
    
    Returns:
        dict: Detection result with risk_score, scam_type, red_flags, and Hindi warning.
    """
    message_lower = message.lower()
    
    # Scam patterns with risk scores
    SCAM_PATTERNS = {
        'collect_scam': {
            'keywords': ['collect request', 'accept to receive', 'pay to receive', 'claim prize'],
            'risk': 0.98,
            'explanation': 'UPI collect request scam - money debits from your account!'
        },
        'prize_lottery': {
            'keywords': ['won lottery', 'prize money', 'lucky winner', 'claim reward', 'cashback'],
            'risk': 0.95,
            'explanation': 'Fake prize/lottery scam - you never entered any lottery!'
        },
        'refund_trick': {
            'keywords': ['refund pending', 'reversal', 'failed transaction', 'enter pin to receive'],
            'risk': 0.92,
            'explanation': 'Fake refund trick - entering PIN debits money!'
        },
        'qr_scam': {
            'keywords': ['scan qr', 'qr code', 'scan to receive', 'qr for payment'],
            'risk': 0.90,
            'explanation': 'QR code scam - scanning QR debits YOUR money!'
        },
        'marketplace_fraud': {
            'keywords': ['olx', 'army person', 'crpf', 'posting transfer', 'urgent sale'],
            'risk': 0.88,
            'explanation': 'Marketplace fraud - fake buyer/seller scam'
        }
    }
    
    detected_scams = []
    max_risk = 0.0
    red_flags = []
    
    for scam_type, data in SCAM_PATTERNS.items():
        for keyword in data['keywords']:
            if keyword in message_lower:
                detected_scams.append(scam_type)
                max_risk = max(max_risk, data['risk'])
                red_flags.append(data['explanation'])
                break
    
    # Check for urgency amplifiers
    urgency_words = ['urgent', 'immediately', 'now only', 'limited time', 'expire today', '24 hours']
    if any(word in message_lower for word in urgency_words):
        max_risk = min(max_risk + 0.05, 1.0)
        red_flags.append('Urgency pressure tactic detected')
    
    # Check suspicious amounts
    if amount and amount in [1, 10, 49999, 50000, 99999, 100000]:
        max_risk = min(max_risk + 0.05, 1.0)
        red_flags.append(f'Suspicious round amount: ₹{amount}')
    
    # Determine threat level
    if max_risk >= 0.9:
        threat_level = 'CRITICAL'
        action = '🚨 STOP! This is a SCAM! Do NOT proceed!'
        hindi = '🚨 रुकें! यह धोखाधड़ी है! आगे न बढ़ें! कोई OTP या PIN न दें!'
    elif max_risk >= 0.7:
        threat_level = 'HIGH'
        action = '⚠️ HIGH RISK! Do not accept this request.'
        hindi = '⚠️ उच्च जोखिम! इस रिक्वेस्ट को स्वीकार न करें!'
    elif max_risk >= 0.4:
        threat_level = 'MEDIUM'
        action = '⚡ Exercise caution. Verify before proceeding.'
        hindi = '⚡ सावधान! पहले जाँच करें।'
    else:
        threat_level = 'LOW'
        action = '✅ Appears safe, but stay vigilant.'
        hindi = '✅ सुरक्षित लगता है।'
    
    return {
        "status": "success",
        "tool": "upi_scam_detector",
        "risk_score": max_risk,
        "threat_level": threat_level,
        "scam_types": detected_scams,
        "red_flags": red_flags,
        "recommendation": action,
        "hindi_warning": hindi,
        "key_fact": "UPI Collect Request = Money DEBITED, not credited! Never enter PIN to 'receive' money."
    }


# =============================================================================
# TOOL 2: KYC PHISHING DETECTOR
# =============================================================================

def detect_kyc_phishing(message: str) -> dict:
    """
    Detects fake KYC update scams including APK malware, fake bank links,
    account blocking threats, and screen sharing traps.
    
    Args:
        message: The message to analyze for KYC phishing patterns.
    
    Returns:
        dict: Detection result with phishing indicators and risk assessment.
    """
    message_lower = message.lower()
    
    PHISHING_INDICATORS = {
        'apk_malware': {
            'patterns': [r'\.apk', r'download.*app', r'install.*apk', r'banking.*app.*link'],
            'risk': 0.99,
            'explanation': '🚨 APK MALWARE - Banks NEVER send app download links!'
        },
        'shortened_url': {
            'patterns': [r'bit\.ly', r'tinyurl', r'goo\.gl', r't\.co', r'short\.'],
            'risk': 0.85,
            'explanation': '⚠️ Shortened URL hiding real malicious destination'
        },
        'fake_bank_link': {
            'patterns': [r'sbi.*update', r'hdfc.*kyc', r'icici.*verify', r'axis.*confirm'],
            'risk': 0.92,
            'explanation': '🚨 Fake bank link - Real banks use official apps only'
        },
        'account_threat': {
            'patterns': [r'block.*account', r'suspend', r'deactivate', r'close.*account'],
            'risk': 0.80,
            'explanation': '⚠️ Account blocking threat - Scare tactic by scammers'
        },
        'screen_share': {
            'patterns': [r'anydesk', r'teamviewer', r'quicksupport', r'screen.*share'],
            'risk': 0.97,
            'explanation': '🚨 Screen sharing request - MAXIMUM DANGER!'
        },
        'otp_request': {
            'patterns': [r'share.*otp', r'enter.*otp', r'send.*otp', r'tell.*otp'],
            'risk': 0.98,
            'explanation': '🚨 OTP sharing request - NEVER share OTP with anyone!'
        },
        'kyc_urgency': {
            'patterns': [r'kyc.*expir', r'update.*kyc.*urgent', r'immediate.*kyc'],
            'risk': 0.88,
            'explanation': '⚠️ Fake KYC urgency - Banks give adequate time'
        }
    }
    
    detected = []
    max_risk = 0.0
    
    for indicator_type, data in PHISHING_INDICATORS.items():
        for pattern in data['patterns']:
            if re.search(pattern, message_lower, re.IGNORECASE):
                detected.append({
                    'type': indicator_type,
                    'risk': data['risk'],
                    'explanation': data['explanation']
                })
                max_risk = max(max_risk, data['risk'])
                break
    
    # Additional KYC check
    if 'kyc' in message_lower and any(w in message_lower for w in ['link', 'click', 'update']):
        if max_risk < 0.85:
            max_risk = 0.85
            detected.append({
                'type': 'kyc_link',
                'risk': 0.85,
                'explanation': '⚠️ KYC update via link - Banks use official apps!'
            })
    
    if max_risk >= 0.9:
        threat_level = 'CRITICAL'
        hindi = '🚨 खतरा! यह फ़िशिंग है! कुछ भी क्लिक न करें! कोई APP डाउनलोड न करें!'
    elif max_risk >= 0.7:
        threat_level = 'HIGH'
        hindi = '⚠️ उच्च जोखिम! लिंक पर क्लिक न करें!'
    else:
        threat_level = 'LOW'
        hindi = '✅ सुरक्षित लगता है।'
    
    return {
        "status": "success",
        "tool": "kyc_phishing_detector",
        "risk_score": max_risk,
        "threat_level": threat_level,
        "indicators": detected,
        "is_phishing": max_risk >= 0.7,
        "hindi_warning": hindi,
        "key_facts": [
            "Banks NEVER send APK download links",
            "Banks NEVER ask for OTP via SMS/call",
            "Banks NEVER use screen sharing apps",
            "Always use official bank app or visit branch"
        ]
    }


# =============================================================================
# TOOL 3: POLICE IMPERSONATION DETECTOR
# =============================================================================

def detect_police_impersonation(message: str) -> dict:
    """
    Detects fake police, CBI, ED, and other law enforcement impersonation scams.
    Includes digital arrest detection and extortion patterns.
    
    Args:
        message: The call transcript or message to analyze.
    
    Returns:
        dict: Detection result with impersonation indicators and emergency guidance.
    """
    message_lower = message.lower()
    
    AUTHORITY_KEYWORDS = [
        'police', 'cbi', 'ed', 'enforcement directorate', 'crime branch',
        'cyber cell', 'income tax', 'customs', 'narcotics', 'ncb',
        'interpol', 'fir', 'warrant', 'court order', 'legal notice',
        'supreme court', 'high court', 'rbi', 'sebi'
    ]
    
    THREAT_INDICATORS = [
        'arrest', 'custody', 'jail', 'prison', 'warrant issued',
        'case registered', 'investigation', 'money laundering',
        'illegal activity', 'suspicious transaction', 'linked to crime',
        'aadhaar misused', 'pan linked'
    ]
    
    MONEY_DEMANDS = [
        'pay fine', 'transfer money', 'deposit', 'security money',
        'clearance fee', 'bail amount', 'penalty', 'safe account',
        'rbi account', 'government account', 'lakh', 'crore', '₹'
    ]
    
    DIGITAL_ARREST_SIGNS = [
        'stay on call', 'do not disconnect', 'video call', 'skype',
        'whatsapp video', 'don\'t tell anyone', 'confidential',
        'keep this secret', 'digital arrest'
    ]
    
    auth_hits = [kw for kw in AUTHORITY_KEYWORDS if kw in message_lower]
    threat_hits = [t for t in THREAT_INDICATORS if t in message_lower]
    money_hits = [m for m in MONEY_DEMANDS if m in message_lower]
    digital_arrest = [d for d in DIGITAL_ARREST_SIGNS if d in message_lower]
    
    # Calculate risk
    risk_score = 0.0
    if auth_hits:
        risk_score += 0.25 * min(len(auth_hits), 3)
    if threat_hits:
        risk_score += 0.25 * min(len(threat_hits), 3)
    if money_hits:
        risk_score += 0.35
    if digital_arrest:
        risk_score += 0.30
    
    risk_score = min(risk_score, 1.0)
    
    if risk_score >= 0.8:
        threat_level = 'CRITICAL'
        action = '🚨 HANG UP IMMEDIATELY! This is 100% FRAUD!'
        hindi = '''🚨 तुरंत फोन काटें! यह धोखाधड़ी है!

असली पुलिस कभी फोन पर पैसे नहीं मांगती!
"डिजिटल अरेस्ट" असली नहीं है - यह स्कैम है!

हेल्पलाइन: 1930
पोर्टल: cybercrime.gov.in'''
    elif risk_score >= 0.5:
        threat_level = 'HIGH'
        action = '⚠️ Likely impersonation. Disconnect and verify independently.'
        hindi = '⚠️ संभावित धोखाधड़ी। फोन काटें और स्वतंत्र रूप से सत्यापित करें।'
    else:
        threat_level = 'LOW'
        action = 'Low risk detected.'
        hindi = 'कम जोखिम।'
    
    return {
        "status": "success",
        "tool": "police_impersonation_detector",
        "risk_score": risk_score,
        "threat_level": threat_level,
        "authority_claims": auth_hits,
        "threats_made": threat_hits,
        "money_demands": money_hits,
        "digital_arrest_signs": digital_arrest,
        "is_impersonation": risk_score >= 0.7,
        "recommendation": action,
        "hindi_warning": hindi,
        "emergency": {
            "helpline": "1930",
            "portal": "cybercrime.gov.in"
        },
        "key_facts": [
            "Real police NEVER demands money over phone",
            "Real police visits in person for serious matters",
            "Digital arrest is NOT real - it's a scam",
            "Real CBI/ED never uses WhatsApp/video calls",
            "If threatened, hang up and call 1930"
        ]
    }


# =============================================================================
# TOOL 4: LOAN AGREEMENT DECODER
# =============================================================================

def decode_loan_agreement(document_text: str) -> dict:
    """
    Analyzes loan agreements for hidden fees, unfair terms, foreclosure penalties,
    and other clauses that harm borrowers.
    
    Args:
        document_text: The loan agreement text to analyze.
    
    Returns:
        dict: Analysis with hidden terms, risk assessment, and recommendations.
    """
    text_lower = document_text.lower()
    
    HIDDEN_TERMS = {
        'processing_fee': {
            'patterns': ['processing fee', 'documentation charge', 'administrative fee'],
            'risk': 'MEDIUM',
            'explanation': 'Processing fees add to total loan cost'
        },
        'foreclosure_penalty': {
            'patterns': ['foreclosure charge', 'prepayment penalty', 'early closure fee', 'part payment charge'],
            'risk': 'HIGH',
            'explanation': 'Penalty for paying off loan early - restricts your freedom'
        },
        'floating_rate': {
            'patterns': ['floating rate', 'variable interest', 'linked to repo', 'mclr', 'subject to change'],
            'risk': 'MEDIUM',
            'explanation': 'Interest rate can increase without notice'
        },
        'forced_insurance': {
            'patterns': ['mandatory insurance', 'credit protect', 'loan cover', 'protection plan required'],
            'risk': 'HIGH',
            'explanation': 'Forced insurance adds unnecessary cost'
        },
        'penal_interest': {
            'patterns': ['penal interest', 'default charge', 'late payment fee', 'penalty interest'],
            'risk': 'HIGH',
            'explanation': 'Extra interest on missed payments - can compound quickly'
        },
        'cross_default': {
            'patterns': ['cross default', 'other loans', 'all loans due'],
            'risk': 'CRITICAL',
            'explanation': 'Default on one loan triggers all loans becoming due'
        },
        'arbitration_clause': {
            'patterns': ['arbitration', 'no court', 'dispute resolution'],
            'risk': 'MEDIUM',
            'explanation': 'Limits your legal options in case of dispute'
        }
    }
    
    found_issues = []
    
    for term_type, data in HIDDEN_TERMS.items():
        for pattern in data['patterns']:
            if pattern in text_lower:
                found_issues.append({
                    'term': term_type.replace('_', ' ').title(),
                    'risk': data['risk'],
                    'explanation': data['explanation'],
                    'matched': pattern
                })
                break
    
    # Extract interest rate if mentioned
    rate_match = re.search(r'(\d+\.?\d*)\s*%\s*(p\.?a\.?|per annum)?', text_lower)
    interest_rate = float(rate_match.group(1)) if rate_match else None
    
    if interest_rate:
        if interest_rate > 24:
            found_issues.append({
                'term': 'Very High Interest Rate',
                'risk': 'CRITICAL',
                'explanation': f'{interest_rate}% is extremely high - likely predatory',
                'matched': f'{interest_rate}%'
            })
        elif interest_rate > 15:
            found_issues.append({
                'term': 'High Interest Rate',
                'risk': 'HIGH',
                'explanation': f'{interest_rate}% is above normal bank rates',
                'matched': f'{interest_rate}%'
            })
    
    risk_score = min(len(found_issues) * 0.15, 1.0)
    high_risk_count = sum(1 for i in found_issues if i['risk'] in ['HIGH', 'CRITICAL'])
    
    if high_risk_count >= 3:
        overall_risk = 'CRITICAL'
        recommendation = '🚨 Do NOT sign! Multiple serious issues found.'
    elif high_risk_count >= 1:
        overall_risk = 'HIGH'
        recommendation = '⚠️ Negotiate these terms before signing.'
    elif found_issues:
        overall_risk = 'MEDIUM'
        recommendation = '⚡ Review highlighted terms carefully.'
    else:
        overall_risk = 'LOW'
        recommendation = '✅ No major issues found.'
    
    return {
        "status": "success",
        "tool": "loan_agreement_decoder",
        "issues_found": len(found_issues),
        "issues": found_issues,
        "interest_rate": interest_rate,
        "overall_risk": overall_risk,
        "risk_score": risk_score,
        "recommendation": recommendation,
        "hindi_summary": f"कुल {len(found_issues)} छिपी शर्तें मिलीं। हस्ताक्षर से पहले ध्यान से पढ़ें।" if found_issues else "कोई बड़ी समस्या नहीं।",
        "tips": [
            "Always ask for total cost of loan including all fees",
            "Negotiate foreclosure charges - RBI allows free foreclosure for floating rate",
            "Compare with at least 3 lenders before signing",
            "Read every page - don't just sign where asked"
        ]
    }


# =============================================================================
# TOOL 5: INSURANCE POLICY DECODER
# =============================================================================

def decode_insurance_policy(policy_text: str) -> dict:
    """
    Analyzes insurance policies for exclusions, waiting periods, sub-limits,
    and clauses that may result in claim rejection.
    
    Args:
        policy_text: The insurance policy text to analyze.
    
    Returns:
        dict: Analysis with exclusions, limitations, and coverage gaps.
    """
    text_lower = policy_text.lower()
    
    POLICY_ISSUES = {
        'pre_existing': {
            'patterns': ['pre-existing', 'prior condition', 'existing disease', 'ongoing treatment'],
            'risk': 'HIGH',
            'explanation': 'Pre-existing conditions may not be covered initially'
        },
        'waiting_period': {
            'patterns': ['waiting period', 'cooling off', 'initial wait', '30 days wait', '90 days wait'],
            'risk': 'MEDIUM',
            'explanation': 'No coverage during waiting period'
        },
        'room_rent_cap': {
            'patterns': ['room rent limit', 'per day maximum', 'room rent cap', '1% of sum insured'],
            'risk': 'HIGH',
            'explanation': 'Room rent cap limits hospital room choice'
        },
        'co_payment': {
            'patterns': ['co-pay', 'copay', 'co-insurance', 'you pay', 'deductible'],
            'risk': 'MEDIUM',
            'explanation': 'You pay a percentage of every claim'
        },
        'exclusions': {
            'patterns': ['not covered', 'excluded', 'exception', 'does not include'],
            'risk': 'HIGH',
            'explanation': 'Critical exclusions can leave you unprotected'
        },
        'age_limit': {
            'patterns': ['age limit', 'maximum age', 'entry age', 'renewal age'],
            'risk': 'MEDIUM',
            'explanation': 'Policy may not cover you after certain age'
        },
        'claim_limit': {
            'patterns': ['claim limit', 'maximum claims', 'annual limit', 'per illness cap'],
            'risk': 'MEDIUM',
            'explanation': 'Limits on number or amount of claims per year'
        },
        'network_hospital': {
            'patterns': ['network hospital only', 'empanelled hospital', 'approved facility'],
            'risk': 'LOW',
            'explanation': 'Cashless only at specific hospitals'
        }
    }
    
    found_issues = []
    
    for issue_type, data in POLICY_ISSUES.items():
        for pattern in data['patterns']:
            if pattern in text_lower:
                found_issues.append({
                    'issue': issue_type.replace('_', ' ').title(),
                    'risk': data['risk'],
                    'explanation': data['explanation'],
                    'matched': pattern
                })
                break
    
    # Extract sum insured if mentioned
    sum_match = re.search(r'(\d+)\s*(lakh|lac|crore)', text_lower)
    sum_insured = None
    if sum_match:
        amount = int(sum_match.group(1))
        unit = sum_match.group(2)
        sum_insured = amount * (10000000 if 'crore' in unit else 100000)
    
    risk_score = min(len(found_issues) * 0.12, 1.0)
    high_risk = sum(1 for i in found_issues if i['risk'] == 'HIGH')
    
    if high_risk >= 3:
        overall_risk = 'HIGH'
        recommendation = '⚠️ Multiple coverage gaps found. Consider better policy.'
    elif high_risk >= 1:
        overall_risk = 'MEDIUM'
        recommendation = '⚡ Review exclusions carefully before buying.'
    else:
        overall_risk = 'LOW'
        recommendation = '✅ Policy terms appear reasonable.'
    
    return {
        "status": "success",
        "tool": "insurance_policy_decoder",
        "issues_found": len(found_issues),
        "issues": found_issues,
        "sum_insured": sum_insured,
        "overall_risk": overall_risk,
        "risk_score": risk_score,
        "recommendation": recommendation,
        "hindi_summary": f"{len(found_issues)} exclusions/limitations मिले। दावा करने से पहले जानें।",
        "tips": [
            "Always check waiting period for specific diseases",
            "Verify if room rent is capped",
            "Check if your preferred hospital is in network",
            "Read the fine print on pre-existing conditions"
        ]
    }


# =============================================================================
# TOOL 6: INVESTMENT FRAUD DETECTOR
# =============================================================================

def detect_investment_fraud(message: str) -> dict:
    """
    Detects investment scams including Ponzi schemes, fake crypto platforms,
    forex fraud, and get-rich-quick schemes.
    
    Args:
        message: The investment offer to analyze.
    
    Returns:
        dict: Detection result with fraud indicators and SEBI warning.
    """
    message_lower = message.lower()
    
    SCAM_INDICATORS = [
        'guaranteed returns', 'risk-free investment', 'double your money',
        'triple your money', '100% profit', 'fixed return', 'no loss possible',
        'sure profit', 'assured income', 'money back guarantee investment'
    ]
    
    RED_FLAGS = [
        'referral bonus', 'mlm', 'network marketing', 'recruit members',
        'joining fee', 'registration fee', 'crypto trading group',
        'forex signal', 'binary options', 'daily profit', 'weekly returns',
        'monthly guaranteed', 'whatsapp trading'
    ]
    
    UNREALISTIC_RETURNS = [
        'daily 1%', 'daily 2%', 'weekly 10%', 'monthly 15%', 'monthly 20%',
        '100% in', '200% in', '500% in'
    ]
    
    scam_hits = [s for s in SCAM_INDICATORS if s in message_lower]
    red_flag_hits = [r for r in RED_FLAGS if r in message_lower]
    unrealistic = [u for u in UNREALISTIC_RETURNS if u in message_lower]
    
    risk_score = 0.0
    if scam_hits:
        risk_score += 0.35 * min(len(scam_hits), 3)
    if red_flag_hits:
        risk_score += 0.25 * min(len(red_flag_hits), 3)
    if unrealistic:
        risk_score = max(risk_score, 0.95)
    
    # Check for percentage claims
    percent_match = re.search(r'(\d+)\s*%\s*(daily|weekly|monthly|per month|per day)', message_lower)
    if percent_match:
        percentage = int(percent_match.group(1))
        if percentage > 5:
            risk_score = max(risk_score, 0.95)
    
    risk_score = min(risk_score, 1.0)
    
    if risk_score >= 0.8:
        threat_level = 'CRITICAL'
        action = '🚨 This is a PONZI SCHEME! Do NOT invest!'
        hindi = '🚨 यह पोंजी स्कीम है! पैसे न लगाएं! SEBI पंजीकरण जांचें: sebi.gov.in'
    elif risk_score >= 0.5:
        threat_level = 'HIGH'
        action = '⚠️ High risk of fraud. Verify SEBI registration before investing.'
        hindi = '⚠️ धोखाधड़ी का खतरा। SEBI पंजीकरण जांचें।'
    else:
        threat_level = 'LOW'
        action = 'Low risk. Still verify with SEBI before investing.'
        hindi = 'कम जोखिम। फिर भी SEBI से जांचें।'
    
    return {
        "status": "success",
        "tool": "investment_fraud_detector",
        "risk_score": risk_score,
        "threat_level": threat_level,
        "scam_indicators": scam_hits,
        "red_flags": red_flag_hits,
        "unrealistic_returns": unrealistic,
        "is_fraud": risk_score >= 0.7,
        "recommendation": action,
        "hindi_warning": hindi,
        "verify_at": {
            "sebi": "https://sebi.gov.in",
            "scores": "1800-227-227"
        },
        "key_facts": [
            "NO investment is 'guaranteed' or 'risk-free'",
            "Returns over 12-15% annually are suspicious",
            "If you need to recruit others, it's likely a pyramid scheme",
            "Legitimate investments are SEBI registered",
            "Never invest based on WhatsApp messages"
        ]
    }


# =============================================================================
# TOOL 7: EMERGENCY CONTACTS
# =============================================================================

def get_emergency_contacts() -> dict:
    """
    Returns emergency contact numbers and websites for reporting cyber fraud in India.
    
    Returns:
        dict: Complete list of helplines and portals for different fraud types.
    """
    return {
        "status": "success",
        "tool": "emergency_contacts",
        "national_helplines": {
            "cyber_crime": {
                "number": "1930",
                "description": "National Cyber Crime Helpline (24x7)"
            },
            "women_helpline": {
                "number": "1091",
                "description": "Women Helpline"
            },
            "senior_citizen": {
                "number": "14567",
                "description": "Elderline for Senior Citizens"
            }
        },
        "online_portals": {
            "cyber_crime": "https://cybercrime.gov.in",
            "rbi_sachet": "https://sachet.rbi.org.in",
            "sebi_scores": "https://scores.gov.in",
            "irdai": "https://igms.irda.gov.in"
        },
        "bank_helplines": {
            "sbi": "1800-11-2211",
            "hdfc": "1800-202-6161",
            "icici": "1800-102-4242",
            "axis": "1800-419-5555"
        },
        "immediate_actions": [
            "Call 1930 immediately if you've shared OTP/PIN",
            "Block your cards via bank app",
            "File FIR at nearest police station",
            "Report on cybercrime.gov.in within 24 hours"
        ],
        "hindi": "साइबर अपराध हेल्पलाइन: 1930 | पोर्टल: cybercrime.gov.in"
    }


# =============================================================================
# ADK ROOT AGENT - FINANCIAL BODYGUARD
# =============================================================================

root_agent = Agent(
    name="financial_bodyguard",
    model="gemini-2.0-flash",
    description="""Scalar Financial Bodyguard - Multi-agent protection system for Indians aged 35-80+
    
Protects against:
- UPI/Payment fraud
- KYC phishing attacks  
- Police impersonation scams
- Investment fraud
- Hidden loan/insurance terms""",
    
    instruction="""You are the Financial Bodyguard - India's most trusted AI protector against financial fraud.

Your mission: Protect Indians aged 35-80+ from financial scams using specialized detection tools.

## YOUR TOOLS:
1. **detect_upi_scam** - Analyze UPI collect requests, prize scams, QR fraud
2. **detect_kyc_phishing** - Detect fake KYC SMS, APK malware, fake bank links
3. **detect_police_impersonation** - Catch fake CBI/Police calls, digital arrest scams
4. **decode_loan_agreement** - Find hidden fees and unfair loan terms
5. **decode_insurance_policy** - Identify exclusions and coverage gaps
6. **detect_investment_fraud** - Spot Ponzi schemes and crypto scams
7. **get_emergency_contacts** - Provide helpline numbers

## HOW TO RESPOND:

When user shares a suspicious message:
1. Identify the fraud type (UPI, KYC, Police, Investment, etc.)
2. Use the appropriate detection tool
3. Present findings in this format:

**Risk Score:** X.XX (0.00=safe, 1.00=critical)
**Fraud Type:** [Specific scam name]
**Threat Level:** [SAFE/LOW/MEDIUM/HIGH/CRITICAL]

**Analysis:**
[Explain what the scam is and how it works in simple terms]

**Red Flags Found:**
• [List each warning sign]

**Recommendation:**
[Clear action - what user should do]

**हिंदी में:**
[Hindi translation of key warning and action]

**Emergency:** Call 1930 if you've shared any details

## GOLDEN RULES:
- ALWAYS err on the side of caution
- For elderly users (60+), be extra protective and use simpler language
- ALWAYS include Hindi translation
- For CRITICAL threats, strongly urge user to call 1930
- Never make user feel stupid - scammers are sophisticated
- Explain scams in simple, non-technical terms

Remember: Your warnings can save someone's life savings!""",
    
    tools=[
        detect_upi_scam,
        detect_kyc_phishing,
        detect_police_impersonation,
        decode_loan_agreement,
        decode_insurance_policy,
        detect_investment_fraud,
        get_emergency_contacts
    ]
)
