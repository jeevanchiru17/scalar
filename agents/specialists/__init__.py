"""
Scalar Specialist Agents
Individual agents for specific fraud detection domains
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.adk_core import (
    BaseAgent, AgentRole, Task, TaskResult, TaskStatus,
    ToolRegistry
)


# Load fraud trajectories
TRAJECTORIES_PATH = Path(__file__).parent.parent.parent / 'data' / 'fraud_trajectories.json'

def load_trajectories() -> Dict:
    """Load fraud trajectory database"""
    if TRAJECTORIES_PATH.exists():
        with open(TRAJECTORIES_PATH) as f:
            return json.load(f)
    return {"fraud_trajectories": []}

FRAUD_DATA = load_trajectories()


# =============================================================================
# UPI FRAUD SPECIALIST
# =============================================================================

class UPIFraudAgent(BaseAgent):
    """
    Specialist agent for UPI/payment fraud detection
    
    Handles:
    - Collect request scams
    - QR code fraud
    - Fake cashback/refund
    - Marketplace payment scams
    """
    
    def __init__(self, agent_id: str = "upi_fraud_agent"):
        super().__init__(
            agent_id=agent_id,
            name="UPI Fraud Specialist",
            role=AgentRole.SPECIALIST,
            description="Detects UPI payment fraud and collect request scams"
        )
        
        # Load relevant trajectories
        self.trajectories = [
            t for t in FRAUD_DATA.get('fraud_trajectories', [])
            if t.get('detection_agent') in ['upi_fraud_agent', 'marketplace_agent']
        ]
        
        # Pattern database
        self.patterns = {
            'collect_scam': {
                'keywords': ['collect', 'request', 'claim', 'receive', 'accepting'],
                'indicators': ['won', 'lottery', 'prize', 'cashback', 'reward', 'refund'],
                'risk': 0.95
            },
            'qr_fraud': {
                'keywords': ['scan', 'qr', 'code'],
                'indicators': ['receive', 'payment', 'money', 'credit'],
                'risk': 0.92
            },
            'fake_refund': {
                'keywords': ['refund', 'reversal', 'pending', 'failed'],
                'indicators': ['upi pin', 'enter', 'verify', 'confirm'],
                'risk': 0.90
            },
            'marketplace': {
                'keywords': ['army', 'crpf', 'posting', 'buyer', 'seller'],
                'indicators': ['qr', 'link', 'pay', 'receive'],
                'risk': 0.88
            }
        }
    
    @property
    def system_instruction(self) -> str:
        return """You are a UPI Fraud Detection Specialist protecting Indian users from payment scams.

Your expertise:
- UPI collect request scams (NEVER need to pay to receive money)
- QR code fraud (scanning QR debits money, doesn't credit)
- Fake cashback and refund schemes
- Marketplace payment scams (OLX, Facebook)

For any message, identify:
1. Scam type from known patterns
2. Risk score (0.0 to 1.0)
3. Red flags present
4. Clear action for user

Always respond in format:
**Risk: X.XX**
**Type:** [Scam type]
**Red Flags:** [List]
**Action:** [What user should do]
**हिंदी:** [Hindi warning]

Key rules:
- Collect request = ALWAYS suspicious (money debits, not credits)
- QR scanning = debits money from scanner
- Any "pay to receive" = 100% scam"""
    
    @property
    def tools(self) -> List[str]:
        return ['upi_pattern_matcher', 'risk_calculator']
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content for UPI fraud"""
        content_lower = content.lower()
        
        detected_patterns = []
        max_risk = 0.0
        red_flags = []
        
        for pattern_name, pattern_data in self.patterns.items():
            keyword_hits = sum(1 for kw in pattern_data['keywords'] if kw in content_lower)
            indicator_hits = sum(1 for ind in pattern_data['indicators'] if ind in content_lower)
            
            if keyword_hits > 0 and indicator_hits > 0:
                risk = pattern_data['risk'] * (0.7 + 0.15 * keyword_hits + 0.15 * indicator_hits)
                risk = min(risk, 1.0)
                
                detected_patterns.append({
                    'name': pattern_name,
                    'risk': risk,
                    'keywords': keyword_hits,
                    'indicators': indicator_hits
                })
                
                max_risk = max(max_risk, risk)
                red_flags.extend([kw for kw in pattern_data['keywords'] if kw in content_lower])
                red_flags.extend([ind for ind in pattern_data['indicators'] if ind in content_lower])
        
        # Check for urgency amplifiers
        urgency_words = ['urgent', 'immediately', 'now', 'hurry', 'fast', 'limited', 'expire', 'last chance']
        urgency_hits = sum(1 for w in urgency_words if w in content_lower)
        if urgency_hits > 0:
            max_risk = min(max_risk + 0.05 * urgency_hits, 1.0)
            red_flags.append('urgency_pressure')
        
        # Determine threat level
        if max_risk >= 0.9:
            threat_level = 'CRITICAL'
            action = 'DO NOT proceed. This is a scam!'
            hindi = 'धोखाधड़ी! आगे न बढ़ें!'
        elif max_risk >= 0.7:
            threat_level = 'HIGH'
            action = 'High risk of fraud. Do not accept or pay.'
            hindi = 'उच्च जोखिम! स्वीकार न करें!'
        elif max_risk >= 0.4:
            threat_level = 'MEDIUM'
            action = 'Exercise caution. Verify before proceeding.'
            hindi = 'सावधान! पहले जाँच करें.'
        else:
            threat_level = 'LOW'
            action = 'Appears safe, but stay vigilant.'
            hindi = 'सुरक्षित लगता है.'
        
        return {
            'agent': self.agent_id,
            'risk_score': max_risk,
            'threat_level': threat_level,
            'patterns_detected': detected_patterns,
            'red_flags': list(set(red_flags)),
            'action': action,
            'hindi': hindi,
            'matched_trajectories': [
                t['id'] for t in self.trajectories 
                if any(rf in t.get('red_flags', []) for rf in red_flags)
            ]
        }
    
    def _generate_response(self, task: Task) -> Dict[str, Any]:
        """Override to use pattern matching first, then AI"""
        # First use local pattern matching
        local_result = self.analyze(task.content)
        
        # If AI available and high risk, enhance with AI
        if self._client and local_result['risk_score'] > 0.5:
            try:
                from google.genai import types
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=f"Analyze for UPI fraud: {task.content}",
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        temperature=0.7
                    )
                )
                local_result['ai_analysis'] = response.text
            except:
                pass
        
        return local_result


# =============================================================================
# PHISHING SPECIALIST
# =============================================================================

class PhishingAgent(BaseAgent):
    """
    Specialist agent for phishing detection
    
    Handles:
    - Fake KYC updates
    - Malicious APK downloads
    - Fake customer care numbers
    - Fraudulent bank links
    """
    
    def __init__(self, agent_id: str = "phishing_agent"):
        super().__init__(
            agent_id=agent_id,
            name="Phishing Specialist",
            role=AgentRole.SPECIALIST,
            description="Detects phishing attempts and fake KYC scams"
        )
        
        self.phishing_indicators = {
            'apk_download': {
                'patterns': [r'\.apk', r'download.*app', r'install.*app'],
                'risk': 0.98,
                'message': 'APK download - NEVER install apps from links!'
            },
            'shortened_url': {
                'patterns': [r'bit\.ly', r'tinyurl', r'goo\.gl', r't\.co', r'short\.'],
                'risk': 0.85,
                'message': 'Shortened URL hiding real destination'
            },
            'fake_bank': {
                'patterns': [r'sbi.*update', r'hdfc.*kyc', r'icici.*verify', r'axis.*confirm'],
                'risk': 0.90,
                'message': 'Suspicious bank-related URL'
            },
            'account_threat': {
                'patterns': [r'block.*account', r'suspend', r'freeze', r'deactivate', r'close.*account'],
                'risk': 0.80,
                'message': 'Account blocking threat - scare tactic'
            },
            'screen_share': {
                'patterns': [r'anydesk', r'teamviewer', r'quicksupport', r'screen.*share'],
                'risk': 0.95,
                'message': 'Screen sharing request - DANGER!'
            },
            'otp_request': {
                'patterns': [r'share.*otp', r'enter.*otp', r'send.*otp', r'otp.*verification'],
                'risk': 0.96,
                'message': 'OTP sharing request - NEVER share!'
            }
        }
    
    @property
    def system_instruction(self) -> str:
        return """You are a Phishing Detection Specialist protecting Indians from KYC scams.

Your expertise:
- Fake KYC update SMS (banks NEVER send SMS for KYC)
- APK download scams (malware that steals banking data)
- Fake customer care numbers (Google search SEO fraud)
- Screen sharing scams (AnyDesk/TeamViewer)

Key rules:
- Banks NEVER ask to download APK
- Banks NEVER send clickable links for KYC
- Banks NEVER ask for OTP/PIN via SMS
- If unsure, visit bank website directly or call official number

Response format:
**Risk: X.XX**
**Type:** [Phishing type]
**Indicators:** [List]
**Action:** [Clear guidance]
**हिंदी:** [Hindi warning]"""
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze for phishing indicators"""
        content_lower = content.lower()
        
        detected = []
        max_risk = 0.0
        
        for indicator_name, data in self.phishing_indicators.items():
            for pattern in data['patterns']:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    detected.append({
                        'indicator': indicator_name,
                        'risk': data['risk'],
                        'message': data['message']
                    })
                    max_risk = max(max_risk, data['risk'])
                    break
        
        # Additional checks
        if 'kyc' in content_lower and ('update' in content_lower or 'verify' in content_lower):
            if max_risk < 0.8:
                max_risk = 0.85
                detected.append({
                    'indicator': 'kyc_urgency',
                    'risk': 0.85,
                    'message': 'KYC update request - likely phishing'
                })
        
        # Threat level
        if max_risk >= 0.9:
            threat_level = 'CRITICAL'
            hindi = 'गंभीर खतरा! यह फ़िशिंग है! कुछ भी क्लिक न करें!'
        elif max_risk >= 0.7:
            threat_level = 'HIGH'
            hindi = 'उच्च जोखिम! लिंक पर क्लिक न करें!'
        else:
            threat_level = 'LOW'
            hindi = 'सुरक्षित लगता है.'
        
        return {
            'agent': self.agent_id,
            'risk_score': max_risk,
            'threat_level': threat_level,
            'indicators': detected,
            'is_phishing': max_risk >= 0.7,
            'hindi': hindi
        }
    
    def _generate_response(self, task: Task) -> Dict[str, Any]:
        return self.analyze(task.content)


# =============================================================================
# IMPERSONATION SPECIALIST
# =============================================================================

class ImpersonationAgent(BaseAgent):
    """
    Specialist agent for authority impersonation detection
    
    Handles:
    - Police/CBI/ED impersonation
    - Customs/parcel scams
    - Income tax threats
    """
    
    def __init__(self, agent_id: str = "impersonation_agent"):
        super().__init__(
            agent_id=agent_id,
            name="Impersonation Specialist",
            role=AgentRole.SPECIALIST,
            description="Detects fake police and authority impersonation"
        )
        
        self.authority_keywords = [
            'police', 'cbi', 'ed', 'enforcement directorate', 'crime branch',
            'cyber cell', 'income tax', 'customs', 'narcotics', 'ncb',
            'interpol', 'fir', 'warrant', 'court order', 'legal notice'
        ]
        
        self.threat_indicators = [
            'arrest', 'custody', 'jail', 'prison', 'warrant',
            'case against', 'charges', 'investigation', 'questioning',
            'money laundering', 'illegal', 'suspicious activity'
        ]
        
        self.money_demands = [
            'pay', 'transfer', 'fine', 'penalty', 'fee', 'deposit',
            'security', 'bail', '₹', 'rs', 'rupee', 'lakh', 'crore'
        ]
    
    @property
    def system_instruction(self) -> str:
        return """You are an Authority Impersonation Detection Specialist.

Your expertise:
- Fake Police/CBI/ED phone calls
- Digital arrest scams (keeping victim on video call)
- Customs/parcel scams (fake drugs/currency claims)
- Income tax threats

Critical knowledge:
- Real police NEVER demands money over phone
- Real police will visit in person for serious matters
- No legitimate authority uses WhatsApp/video calls for investigations
- Digital arrest is NOT real - police cannot arrest via video call

Warning signs:
- Call claiming you're involved in crime
- Threats of immediate arrest
- Demand for money to "settle" case
- Long calls keeping you isolated
- Pressure to not tell family

Response format:
**Risk: X.XX**
**Type:** [Impersonation type]
**Authority claimed:** [What they claim to be]
**Red flags:** [List]
**Action:** HANG UP IMMEDIATELY. Call 1930.
**हिंदी:** [Hindi warning]"""
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze for impersonation"""
        content_lower = content.lower()
        
        authority_hits = [kw for kw in self.authority_keywords if kw in content_lower]
        threat_hits = [t for t in self.threat_indicators if t in content_lower]
        money_hits = [m for m in self.money_demands if m in content_lower]
        
        risk_score = 0.0
        
        if authority_hits:
            risk_score += 0.3 * min(len(authority_hits), 3)
        
        if threat_hits:
            risk_score += 0.25 * min(len(threat_hits), 3)
        
        if money_hits:
            risk_score += 0.35
        
        # Video call / digital arrest indicator
        if any(term in content_lower for term in ['video call', 'whatsapp video', 'online arrest', 'digital arrest']):
            risk_score += 0.25
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.8:
            threat_level = 'CRITICAL'
            action = 'HANG UP IMMEDIATELY! This is impersonation fraud.'
            hindi = '🚨 तुरंत फोन काटें! यह नकली पुलिस है! असली पुलिस फोन पर पैसे नहीं मांगती! हेल्पलाइन: 1930'
        elif risk_score >= 0.5:
            threat_level = 'HIGH'
            action = 'Likely impersonation. Do not share any info or money.'
            hindi = 'संभावित धोखाधड़ी। कोई जानकारी या पैसे न दें।'
        else:
            threat_level = 'LOW'
            action = 'Low risk detected.'
            hindi = 'कम जोखिम।'
        
        return {
            'agent': self.agent_id,
            'risk_score': risk_score,
            'threat_level': threat_level,
            'authority_claims': authority_hits,
            'threats_made': threat_hits,
            'money_demands': money_hits,
            'is_impersonation': risk_score >= 0.7,
            'action': action,
            'hindi': hindi,
            'emergency_number': '1930'
        }
    
    def _generate_response(self, task: Task) -> Dict[str, Any]:
        return self.analyze(task.content)


# =============================================================================
# DOCUMENT SPECIALIST
# =============================================================================

class DocumentAnalystAgent(BaseAgent):
    """
    Specialist agent for financial document analysis
    
    Handles:
    - Loan agreement analysis
    - Insurance policy review
    - Hidden terms and fees
    """
    
    def __init__(self, agent_id: str = "document_agent"):
        super().__init__(
            agent_id=agent_id,
            name="Document Analyst",
            role=AgentRole.SPECIALIST,
            description="Analyzes loan and insurance documents for hidden risks"
        )
        
        self.loan_red_flags = {
            'floating_rate': ['floating', 'variable rate', 'linked to repo', 'subject to change'],
            'foreclosure_penalty': ['foreclosure charge', 'prepayment penalty', 'early closure fee'],
            'hidden_fees': ['processing fee', 'documentation charge', 'verification fee'],
            'forced_insurance': ['mandatory insurance', 'credit protect', 'loan cover'],
            'penal_interest': ['penal interest', 'default charge', 'late payment penalty']
        }
        
        self.insurance_red_flags = {
            'pre_existing': ['pre-existing', 'prior condition', 'existing disease'],
            'waiting_period': ['waiting period', 'cooling off', 'dormant period'],
            'sub_limits': ['sub-limit', 'room rent cap', 'per day maximum'],
            'co_payment': ['co-pay', 'co-insurance', 'borne by insured'],
            'exclusions': ['not covered', 'excluded', 'exception', 'does not cover']
        }
    
    @property
    def system_instruction(self) -> str:
        return """You are a Financial Document Analyst protecting users from hidden terms.

Your expertise:
- Loan agreements: processing fees, foreclosure penalties, floating rates
- Insurance policies: exclusions, waiting periods, sub-limits
- Fine print that harms consumers

Analyze documents for:
1. Hidden fees and charges
2. Unfavorable terms buried in fine print
3. Exclusions and limitations
4. Comparison with fair market terms

Provide simple explanations for non-experts.
Always highlight terms user should negotiate or question."""
    
    def analyze(self, content: str, doc_type: str = 'loan') -> Dict[str, Any]:
        """Analyze document for hidden risks"""
        content_lower = content.lower()
        
        red_flags = self.loan_red_flags if doc_type == 'loan' else self.insurance_red_flags
        found_issues = []
        
        for issue_name, keywords in red_flags.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    found_issues.append({
                        'issue': issue_name.replace('_', ' ').title(),
                        'keyword': kw,
                        'risk': 'HIGH' if 'penalty' in kw or 'not covered' in kw else 'MEDIUM'
                    })
                    break
        
        # Extract interest rate if present
        rate_match = re.search(r'(\d+\.?\d*)\s*%\s*(p\.?a\.?|per\s*annum)?', content_lower)
        interest_rate = float(rate_match.group(1)) if rate_match else None
        
        if interest_rate and interest_rate > 15:
            found_issues.append({
                'issue': 'High Interest Rate',
                'keyword': f'{interest_rate}%',
                'risk': 'HIGH'
            })
        
        risk_score = min(len(found_issues) * 0.2, 1.0)
        
        return {
            'agent': self.agent_id,
            'document_type': doc_type,
            'issues_found': found_issues,
            'issue_count': len(found_issues),
            'risk_score': risk_score,
            'interest_rate': interest_rate,
            'recommendation': 'Review highlighted terms carefully before signing.' if found_issues else 'Document appears standard.',
            'hindi': f'{len(found_issues)} समस्याएं मिलीं। हस्ताक्षर से पहले जांचें।' if found_issues else 'दस्तावेज़ सामान्य है।'
        }
    
    def _generate_response(self, task: Task) -> Dict[str, Any]:
        doc_type = task.metadata.get('document_type', 'loan')
        return self.analyze(task.content, doc_type)


# =============================================================================
# INVESTMENT FRAUD SPECIALIST
# =============================================================================

class InvestmentFraudAgent(BaseAgent):
    """
    Specialist agent for investment fraud detection
    
    Handles:
    - Ponzi schemes
    - Fake trading platforms
    - Crypto scams
    - Get-rich-quick schemes
    """
    
    def __init__(self, agent_id: str = "investment_agent"):
        super().__init__(
            agent_id=agent_id,
            name="Investment Fraud Specialist",
            role=AgentRole.SPECIALIST,
            description="Detects investment scams and Ponzi schemes"
        )
        
        self.scam_indicators = [
            'guaranteed returns', 'risk-free', 'double your money',
            'high returns', '100% profit', 'fixed return',
            'no loss', 'sure profit', 'income guarantee'
        ]
        
        self.red_flag_terms = [
            'referral bonus', 'mlm', 'network marketing',
            'joining fee', 'registration fee', 'crypto trading',
            'forex', 'binary options', 'daily profit'
        ]
    
    @property
    def system_instruction(self) -> str:
        return """You are an Investment Fraud Specialist.

Your expertise:
- Ponzi and pyramid schemes
- Fake cryptocurrency platforms
- Forex/binary options scams
- MLM schemes disguised as investments

Key rules for users:
- NO investment is "guaranteed" or "risk-free"
- Returns over 15% annually are suspicious
- If you need to recruit others, it's likely a pyramid
- Legitimate investments are registered with SEBI

Always warn about unrealistic promises."""
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze for investment scams"""
        content_lower = content.lower()
        
        scam_hits = [s for s in self.scam_indicators if s in content_lower]
        red_flag_hits = [r for r in self.red_flag_terms if r in content_lower]
        
        risk_score = 0.0
        if scam_hits:
            risk_score += 0.4 * min(len(scam_hits), 3)
        if red_flag_hits:
            risk_score += 0.3 * min(len(red_flag_hits), 3)
        
        # Check for unrealistic return claims
        return_match = re.search(r'(\d+)\s*%\s*(daily|weekly|monthly|per month)', content_lower)
        if return_match:
            risk_score = max(risk_score, 0.95)
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.8:
            threat_level = 'CRITICAL'
            hindi = '🚨 यह निवेश धोखाधड़ी है! पैसे न लगाएं!'
        elif risk_score >= 0.5:
            threat_level = 'HIGH'
            hindi = 'संभावित धोखाधड़ी। SEBI पंजीकरण जांचें।'
        else:
            threat_level = 'LOW'
            hindi = 'सामान्य जोखिम।'
        
        return {
            'agent': self.agent_id,
            'risk_score': risk_score,
            'threat_level': threat_level,
            'scam_indicators': scam_hits,
            'red_flags': red_flag_hits,
            'is_fraud': risk_score >= 0.7,
            'hindi': hindi,
            'advice': 'Check SEBI registration before investing. Never invest based on messages.'
        }
    
    def _generate_response(self, task: Task) -> Dict[str, Any]:
        return self.analyze(task.content)


# =============================================================================
# INITIALIZER FOR PACKAGE
# =============================================================================

__all__ = [
    'UPIFraudAgent',
    'PhishingAgent',
    'ImpersonationAgent',
    'DocumentAnalystAgent',
    'InvestmentFraudAgent'
]
