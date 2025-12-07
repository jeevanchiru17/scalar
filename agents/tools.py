"""
Financial Bodyguard - Agent Tools
Specialized tools that agents can use for fraud detection and document analysis
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import json


class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ToolResult:
    """Standard result from any tool"""
    success: bool
    tool_name: str
    result: Dict[str, Any]
    risk_level: RiskLevel
    confidence: float
    explanation: str
    hindi_explanation: Optional[str] = None


# =============================================================================
# TOOL 1: UPI Scam Detector
# =============================================================================

class UPIScamDetector:
    """
    Tool for detecting UPI/BHIM payment scams
    Common patterns: Fake collect requests, prize scams, refund scams
    """
    
    NAME = "upi_scam_detector"
    DESCRIPTION = "Analyzes UPI transaction messages for fraud patterns"
    
    # Known scam patterns with risk weights
    SCAM_PATTERNS = {
        "collect_request_scam": {
            "keywords": ["collect", "request", "pay", "receive", "claim"],
            "indicators": ["won", "lottery", "prize", "cashback", "refund", "reward"],
            "risk": 0.9,
            "hindi": "कलेक्ट रिक्वेस्ट धोखाधड़ी"
        },
        "fake_cashback": {
            "keywords": ["cashback", "bonus", "reward", "credit"],
            "indicators": ["click", "link", "verify", "otp"],
            "risk": 0.85,
            "hindi": "नकली कैशबैक"
        },
        "refund_scam": {
            "keywords": ["refund", "reversal", "failed", "pending"],
            "indicators": ["upi pin", "enter", "confirm", "process"],
            "risk": 0.88,
            "hindi": "रिफंड धोखाधड़ी"
        },
        "qr_code_scam": {
            "keywords": ["scan", "qr", "code", "payment"],
            "indicators": ["receive", "get", "credit", "money"],
            "risk": 0.92,
            "hindi": "QR कोड धोखाधड़ी"
        }
    }
    
    # Suspicious amount patterns
    ODD_AMOUNTS = [1, 10, 49999, 50000, 99999, 100000]
    
    def analyze(self, message: str, amount: Optional[float] = None) -> ToolResult:
        """Analyze a UPI-related message for scam indicators"""
        message_lower = message.lower()
        
        detected_patterns = []
        total_risk = 0.0
        evidence = []
        
        for pattern_name, pattern_data in self.SCAM_PATTERNS.items():
            keyword_matches = sum(1 for kw in pattern_data["keywords"] if kw in message_lower)
            indicator_matches = sum(1 for ind in pattern_data["indicators"] if ind in message_lower)
            
            if keyword_matches > 0 and indicator_matches > 0:
                pattern_risk = pattern_data["risk"] * (0.5 + 0.25 * keyword_matches + 0.25 * indicator_matches)
                pattern_risk = min(pattern_risk, 1.0)
                
                detected_patterns.append({
                    "pattern": pattern_name,
                    "risk": pattern_risk,
                    "hindi": pattern_data["hindi"]
                })
                total_risk = max(total_risk, pattern_risk)
                evidence.append(f"Matched pattern: {pattern_name}")
        
        # Check for urgency language
        urgency_words = ["urgent", "immediately", "now", "hurry", "fast", "quick", "limited", "expire"]
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        if urgency_count > 0:
            total_risk = min(total_risk + 0.1 * urgency_count, 1.0)
            evidence.append(f"Urgency language detected ({urgency_count} indicators)")
        
        # Check suspicious amount
        if amount and amount in self.ODD_AMOUNTS:
            total_risk = min(total_risk + 0.15, 1.0)
            evidence.append(f"Suspicious round amount: ₹{amount}")
        
        # Determine risk level
        if total_risk >= 0.9:
            risk_level = RiskLevel.CRITICAL
        elif total_risk >= 0.7:
            risk_level = RiskLevel.HIGH
        elif total_risk >= 0.4:
            risk_level = RiskLevel.MEDIUM
        elif total_risk > 0:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE
        
        # Generate explanation
        if detected_patterns:
            explanation = f"⚠️ SCAM DETECTED: {detected_patterns[0]['pattern'].replace('_', ' ').title()}. DO NOT proceed with this transaction."
            hindi = f"🚨 धोखाधड़ी: {detected_patterns[0]['hindi']}। इस लेनदेन को आगे न बढ़ाएं!"
        else:
            explanation = "No known UPI scam patterns detected. Exercise normal caution."
            hindi = "कोई ज्ञात धोखाधड़ी पैटर्न नहीं मिला।"
        
        return ToolResult(
            success=True,
            tool_name=self.NAME,
            result={
                "risk_score": total_risk,
                "patterns_detected": detected_patterns,
                "evidence": evidence,
                "is_scam": total_risk >= 0.7
            },
            risk_level=risk_level,
            confidence=0.85 if detected_patterns else 0.6,
            explanation=explanation,
            hindi_explanation=hindi
        )


# =============================================================================
# TOOL 2: KYC Phishing Detector
# =============================================================================

class KYCPhishingDetector:
    """
    Tool for detecting fake KYC update scams
    Common patterns: APK downloads, fake bank links, account blocking threats
    """
    
    NAME = "kyc_phishing_detector"
    DESCRIPTION = "Identifies fake KYC/bank verification scams"
    
    PHISHING_INDICATORS = {
        "apk_download": {
            "patterns": [r"\.apk", r"download.*app", r"install.*app"],
            "risk": 0.98,
            "explanation": "APK download request - NEVER download apps from links"
        },
        "shortened_url": {
            "patterns": [r"bit\.ly", r"tinyurl", r"goo\.gl", r"shorturl", r"t\.co"],
            "risk": 0.85,
            "explanation": "Shortened URL detected - may hide malicious destination"
        },
        "fake_bank_url": {
            "patterns": [r"sbi.*secure", r"hdfc.*update", r"icici.*kyc", r"bank.*verify"],
            "risk": 0.9,
            "explanation": "Suspicious bank-related URL pattern"
        },
        "blocking_threat": {
            "patterns": [r"block.*account", r"suspend.*account", r"freeze.*account", r"deactivate"],
            "risk": 0.8,
            "explanation": "Account blocking threat - common scare tactic"
        },
        "time_pressure": {
            "patterns": [r"\d+\s*hour", r"\d+\s*hr", r"24\s*hour", r"48\s*hour", r"today", r"midnight"],
            "risk": 0.75,
            "explanation": "Artificial time pressure - real banks give adequate time"
        }
    }
    
    def analyze(self, message: str) -> ToolResult:
        """Analyze message for KYC phishing indicators"""
        message_lower = message.lower()
        
        detected = []
        max_risk = 0.0
        evidence = []
        
        for indicator_name, data in self.PHISHING_INDICATORS.items():
            for pattern in data["patterns"]:
                if re.search(pattern, message_lower):
                    detected.append({
                        "indicator": indicator_name,
                        "risk": data["risk"],
                        "explanation": data["explanation"]
                    })
                    max_risk = max(max_risk, data["risk"])
                    evidence.append(data["explanation"])
                    break
        
        # Check for OTP/PIN requests
        if re.search(r"otp|pin|password|cvv", message_lower):
            max_risk = max(max_risk, 0.95)
            evidence.append("Request for sensitive credentials (OTP/PIN/CVV)")
        
        # Determine risk level
        if max_risk >= 0.9:
            risk_level = RiskLevel.CRITICAL
            explanation = "🚨 CRITICAL: This is a KYC phishing scam. Banks NEVER send links for KYC updates."
            hindi = "🚨 खतरा: यह KYC फ़िशिंग धोखाधड़ी है। बैंक कभी भी KYC के लिए लिंक नहीं भेजते!"
        elif max_risk >= 0.7:
            risk_level = RiskLevel.HIGH
            explanation = "⚠️ HIGH RISK: Multiple phishing indicators found. Do not click any links."
            hindi = "⚠️ उच्च जोखिम: कई फ़िशिंग संकेत मिले। किसी भी लिंक पर क्लिक न करें।"
        elif max_risk >= 0.4:
            risk_level = RiskLevel.MEDIUM
            explanation = "⚡ CAUTION: Some suspicious elements detected. Verify with your bank directly."
            hindi = "⚡ सावधान: कुछ संदिग्ध तत्व मिले। सीधे बैंक से संपर्क करें।"
        else:
            risk_level = RiskLevel.SAFE
            explanation = "No phishing indicators detected."
            hindi = "कोई फ़िशिंग संकेत नहीं मिला।"
        
        return ToolResult(
            success=True,
            tool_name=self.NAME,
            result={
                "risk_score": max_risk,
                "indicators": detected,
                "evidence": evidence,
                "is_phishing": max_risk >= 0.7
            },
            risk_level=risk_level,
            confidence=0.9 if detected else 0.7,
            explanation=explanation,
            hindi_explanation=hindi
        )


# =============================================================================
# TOOL 3: Police Impersonation Detector
# =============================================================================

class PoliceImpersonationDetector:
    """
    Tool for detecting fake police/CBI/ED calls and messages
    """
    
    NAME = "police_impersonation_detector"
    DESCRIPTION = "Detects fake law enforcement impersonation scams"
    
    AUTHORITY_KEYWORDS = [
        "police", "cbi", "ed", "enforcement", "crime branch", "cyber cell",
        "income tax", "customs", "narcotics", "interpol", "fir", "warrant",
        "arrest", "jail", "court", "legal action", "investigation"
    ]
    
    THREAT_PATTERNS = [
        "arrest", "custody", "jail", "prison", "warrant", "case against",
        "money laundering", "illegal", "suspicious activity", "linked to",
        "aadhaar", "pan", "bank account"
    ]
    
    def analyze(self, message: str) -> ToolResult:
        """Analyze for police impersonation scam"""
        message_lower = message.lower()
        
        authority_matches = [kw for kw in self.AUTHORITY_KEYWORDS if kw in message_lower]
        threat_matches = [pt for pt in self.THREAT_PATTERNS if pt in message_lower]
        
        # Calculate risk based on combination
        risk_score = 0.0
        evidence = []
        
        if authority_matches:
            risk_score += 0.3 * min(len(authority_matches), 3)
            evidence.append(f"Authority claims: {', '.join(authority_matches[:3])}")
        
        if threat_matches:
            risk_score += 0.25 * min(len(threat_matches), 3)
            evidence.append(f"Threat language: {', '.join(threat_matches[:3])}")
        
        # Money demand is critical indicator
        if re.search(r"pay|transfer|₹|rs\.?|rupee|fine|penalty|fee", message_lower):
            risk_score += 0.35
            evidence.append("Monetary demand detected")
        
        # Time pressure
        if re.search(r"immediate|now|today|urgent", message_lower):
            risk_score += 0.15
            evidence.append("Immediate action demanded")
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
            explanation = "🚨 FAKE POLICE CALL: Real police NEVER demand money over phone. Hang up immediately!"
            hindi = "🚨 नकली पुलिस कॉल: असली पुलिस कभी फोन पर पैसे नहीं मांगती। तुरंत फोन काटें! साइबर क्राइम हेल्पलाइन: 1930"
        elif risk_score >= 0.5:
            risk_level = RiskLevel.HIGH
            explanation = "⚠️ Possible impersonation attempt. Verify by calling 100 or visiting local police station."
            hindi = "⚠️ संभावित प्रतिरूपण प्रयास। 100 पर कॉल करके या स्थानीय थाने जाकर सत्यापित करें।"
        else:
            risk_level = RiskLevel.LOW
            explanation = "Low risk of impersonation detected."
            hindi = "कम जोखिम।"
        
        return ToolResult(
            success=True,
            tool_name=self.NAME,
            result={
                "risk_score": risk_score,
                "authority_claims": authority_matches,
                "threats": threat_matches,
                "evidence": evidence,
                "is_impersonation": risk_score >= 0.7
            },
            risk_level=risk_level,
            confidence=0.88,
            explanation=explanation,
            hindi_explanation=hindi
        )


# =============================================================================
# TOOL 4: Loan Agreement Decoder
# =============================================================================

class LoanAgreementDecoder:
    """
    Tool for decoding complex loan and EMI agreements
    Finds hidden fees, foreclosure penalties, and unfair terms
    """
    
    NAME = "loan_agreement_decoder"
    DESCRIPTION = "Analyzes loan documents for hidden terms and risks"
    
    # Dangerous clauses to detect
    DANGER_TERMS = {
        "floating_rate": {
            "patterns": [r"floating", r"variable.*rate", r"linked.*to.*repo", r"subject.*to.*change"],
            "risk": "MEDIUM",
            "explanation": "Interest rate can change, increasing your EMI"
        },
        "foreclosure_penalty": {
            "patterns": [r"foreclosure.*charge", r"prepayment.*penalty", r"early.*closure.*fee", r"\d+%.*prepay"],
            "risk": "HIGH",
            "explanation": "You'll be charged for paying off loan early"
        },
        "processing_fee": {
            "patterns": [r"processing.*fee.*\d+%", r"processing.*charge"],
            "risk": "MEDIUM",
            "explanation": "Upfront fee charged on loan amount"
        },
        "hidden_insurance": {
            "patterns": [r"mandatory.*insurance", r"credit.*protect", r"loan.*cover", r"insurance.*premium"],
            "risk": "HIGH",
            "explanation": "Forced insurance bundled with loan"
        },
        "penal_interest": {
            "patterns": [r"penal.*interest", r"default.*charge", r"late.*payment.*\d+%", r"penalty.*rate"],
            "risk": "HIGH",
            "explanation": "Extra charges for missed payments"
        },
        "arbitration_clause": {
            "patterns": [r"arbitration", r"dispute.*resolution", r"no.*court"],
            "risk": "MEDIUM",
            "explanation": "Limited legal recourse if issues arise"
        }
    }
    
    def analyze(self, document_text: str) -> ToolResult:
        """Analyze loan document for hidden terms"""
        text_lower = document_text.lower()
        
        found_terms = []
        max_risk = "LOW"
        total_risks = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for term_name, data in self.DANGER_TERMS.items():
            for pattern in data["patterns"]:
                if re.search(pattern, text_lower):
                    found_terms.append({
                        "term": term_name.replace("_", " ").title(),
                        "risk": data["risk"],
                        "explanation": data["explanation"]
                    })
                    total_risks[data["risk"]] += 1
                    if data["risk"] == "HIGH":
                        max_risk = "HIGH"
                    elif data["risk"] == "MEDIUM" and max_risk != "HIGH":
                        max_risk = "MEDIUM"
                    break
        
        # Extract interest rate if mentioned
        rate_match = re.search(r"(\d+\.?\d*)\s*%\s*(p\.?a\.?|per\s*annum|annual)", text_lower)
        interest_rate = float(rate_match.group(1)) if rate_match else None
        
        # Calculate effective annual rate warning
        if interest_rate and interest_rate > 15:
            found_terms.append({
                "term": "High Interest Rate",
                "risk": "HIGH",
                "explanation": f"Interest rate of {interest_rate}% is above market average"
            })
            max_risk = "HIGH"
        
        # Generate summary
        if max_risk == "HIGH":
            risk_level = RiskLevel.HIGH
            explanation = f"⚠️ CAUTION: Found {total_risks['HIGH']} high-risk clauses. Review carefully before signing."
            hindi = f"⚠️ सावधान: {total_risks['HIGH']} उच्च जोखिम वाली शर्तें मिलीं। हस्ताक्षर करने से पहले सावधानी से पढ़ें।"
        elif max_risk == "MEDIUM":
            risk_level = RiskLevel.MEDIUM
            explanation = f"⚡ Some concerns found. {total_risks['MEDIUM']} terms need attention."
            hindi = f"⚡ कुछ चिंताएं मिलीं। {total_risks['MEDIUM']} शर्तों पर ध्यान दें।"
        else:
            risk_level = RiskLevel.LOW
            explanation = "Document appears standard. Still recommended to read fully."
            hindi = "दस्तावेज़ सामान्य लगता है। फिर भी पूरा पढ़ने की सलाह है।"
        
        return ToolResult(
            success=True,
            tool_name=self.NAME,
            result={
                "found_terms": found_terms,
                "risk_summary": total_risks,
                "interest_rate": interest_rate,
                "max_risk": max_risk
            },
            risk_level=risk_level,
            confidence=0.75,
            explanation=explanation,
            hindi_explanation=hindi
        )


# =============================================================================
# TOOL 5: Insurance Policy Decoder
# =============================================================================

class InsurancePolicyDecoder:
    """
    Tool for decoding complex insurance policies
    Identifies exclusions, waiting periods, and claim limitations
    """
    
    NAME = "insurance_policy_decoder"
    DESCRIPTION = "Analyzes insurance policies for hidden terms and exclusions"
    
    CRITICAL_EXCLUSIONS = {
        "pre_existing": {
            "patterns": [r"pre-?existing", r"prior.*condition", r"existing.*disease"],
            "explanation": "Conditions you have before policy start may not be covered"
        },
        "waiting_period": {
            "patterns": [r"waiting.*period", r"\d+.*days?.*wait", r"\d+.*months?.*wait"],
            "explanation": "You cannot claim for certain period after policy starts"
        },
        "sub_limits": {
            "patterns": [r"sub-?limit", r"room.*rent.*cap", r"maximum.*per.*day"],
            "explanation": "Caps on specific expenses within your total coverage"
        },
        "co_payment": {
            "patterns": [r"co-?pay", r"co-?insurance", r"\d+%.*borne.*by"],
            "explanation": "You pay a percentage of every claim"
        },
        "disease_exclusion": {
            "patterns": [r"not.*cover.*cancer", r"exclud.*mental", r"exclud.*maternity", r"no.*claim.*chronic"],
            "explanation": "Specific diseases or conditions are not covered"
        },
        "claim_limit": {
            "patterns": [r"maximum.*claims?.*per.*year", r"limit.*of.*\d+.*claims?"],
            "explanation": "Restriction on number of claims you can make"
        }
    }
    
    def analyze(self, policy_text: str) -> ToolResult:
        """Analyze insurance policy for exclusions and limitations"""
        text_lower = policy_text.lower()
        
        exclusions_found = []
        
        for exclusion_name, data in self.CRITICAL_EXCLUSIONS.items():
            for pattern in data["patterns"]:
                if re.search(pattern, text_lower):
                    exclusions_found.append({
                        "type": exclusion_name.replace("_", " ").title(),
                        "explanation": data["explanation"]
                    })
                    break
        
        # Extract waiting period if mentioned
        waiting_match = re.search(r"(\d+)\s*(days?|months?|years?).*waiting", text_lower)
        waiting_period = f"{waiting_match.group(1)} {waiting_match.group(2)}" if waiting_match else None
        
        # Generate analysis
        if len(exclusions_found) >= 3:
            risk_level = RiskLevel.HIGH
            explanation = f"⚠️ Policy has {len(exclusions_found)} significant limitations. Compare with other policies."
            hindi = f"⚠️ पॉलिसी में {len(exclusions_found)} महत्वपूर्ण सीमाएं हैं। अन्य पॉलिसियों से तुलना करें।"
        elif exclusions_found:
            risk_level = RiskLevel.MEDIUM
            explanation = f"Found {len(exclusions_found)} limitations to be aware of."
            hindi = f"{len(exclusions_found)} सीमाओं के बारे में जानकारी रखें।"
        else:
            risk_level = RiskLevel.LOW
            explanation = "No major exclusions detected in analyzed text."
            hindi = "कोई बड़ी सीमाएं नहीं मिलीं।"
        
        return ToolResult(
            success=True,
            tool_name=self.NAME,
            result={
                "exclusions": exclusions_found,
                "waiting_period": waiting_period,
                "exclusion_count": len(exclusions_found)
            },
            risk_level=risk_level,
            confidence=0.7,
            explanation=explanation,
            hindi_explanation=hindi
        )


# =============================================================================
# TOOL REGISTRY - Available tools for agents
# =============================================================================

AVAILABLE_TOOLS = {
    "upi_scam_detector": UPIScamDetector(),
    "kyc_phishing_detector": KYCPhishingDetector(),
    "police_impersonation_detector": PoliceImpersonationDetector(),
    "loan_agreement_decoder": LoanAgreementDecoder(),
    "insurance_policy_decoder": InsurancePolicyDecoder(),
}


def get_tool(tool_name: str):
    """Get a tool by name"""
    return AVAILABLE_TOOLS.get(tool_name)


def list_tools() -> List[Dict[str, str]]:
    """List all available tools"""
    return [
        {"name": name, "description": tool.DESCRIPTION}
        for name, tool in AVAILABLE_TOOLS.items()
    ]
