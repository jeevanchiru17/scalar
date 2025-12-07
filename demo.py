#!/usr/bin/env python3
"""
Scalar Financial Bodyguard - Demo Script
Demonstrates multi-agent fraud detection
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.financial_bodyguard import get_bodyguard, analyze
from agents.specialists import DocumentAnalystAgent


def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_result(result):
    print(f"\n🎯 Threat Level: {result.threat_level}")
    print(f"📊 Risk Score: {result.risk_score:.2f}")
    print(f"👮 Primary Agent: {result.primary_threat or 'N/A'}")
    print(f"\n📝 Summary:\n{result.summary}")
    print(f"\n🇮🇳 हिंदी:\n{result.hindi_summary}")
    print("\n📋 Recommendations:")
    for rec in result.recommendations:
        print(f"   {rec}")
    
    if result.matched_trajectory:
        print(f"\n🔍 Matched Scam Pattern: {result.matched_trajectory.get('name')}")


def demo_upi_scam():
    print_header("SCENARIO 1: UPI Collect Request Scam")
    message = """
    Congratulations! You have won Rs 50,000 in our lucky draw!
    To claim your prize, accept the UPI collect request from 9876543210.
    Prize valid for 24 hours only. Hurry!
    """
    print(f"📱 Input Message:\n{message.strip()}")
    result = analyze(message, user_age=55)
    print_result(result)


def demo_digital_arrest():
    print_header("SCENARIO 2: Digital Arrest Scam")
    message = """
    This is Officer Sharma from CBI.
    Your Aadhaar is linked to money laundering case.
    FIR has been registered. Warrant has been issued.
    Pay Rs 1,50,000 fine to avoid arrest.
    Do not disconnect. Do not tell anyone.
    """
    print(f"📞 Call Transcript:\n{message.strip()}")
    result = analyze(message, user_age=68)
    print_result(result)


def demo_kyc_phishing():
    print_header("SCENARIO 3: Fake KYC APK Scam")
    message = """
    Dear SBI Customer,
    Your KYC has expired. Account will be blocked in 24 hours.
    Update now: bit.ly/sbi-kyc-update
    Or download: sbi-update.apk
    """
    print(f"📱 Input Message:\n{message.strip()}")
    result = analyze(message, user_age=52)
    print_result(result)


def demo_investment_scam():
    print_header("SCENARIO 4: Crypto Investment Scam")
    message = """
    Join our crypto trading platform!
    ★ Guaranteed 15% monthly returns
    ★ No risk investment
    ★ Daily profits credited
    Join now with Rs 10,000!
    """
    print(f"📱 Investment Offer:\n{message.strip()}")
    result = analyze(message, user_age=45)
    print_result(result)


def demo_loan_document():
    print_header("SCENARIO 5: Loan Agreement Analysis")
    document = """
    Interest Rate: 18% p.a. (floating)
    Processing Fee: 2% of loan amount
    Foreclosure Charges: 4% of outstanding
    Late Payment Penalty: 2% per month
    """
    print(f"📄 Loan Document:\n{document.strip()}")
    
    doc_agent = DocumentAnalystAgent()
    result = doc_agent.analyze(document, 'loan')
    
    print(f"\n📊 Risk Score: {result['risk_score']:.2f}")
    print(f"⚠️ Issues Found: {result['issue_count']}")
    for issue in result['issues_found']:
        print(f"   • {issue['issue']} ({issue['risk']})")


def show_stats():
    print_header("SYSTEM STATISTICS")
    bodyguard = get_bodyguard()
    stats = bodyguard.get_stats()
    
    print(f"📊 Total Analyses: {stats['total_analyses']}")
    print(f"🚨 Threats Detected: {stats['threats_detected']}")
    print(f"⛔ Critical Blocks: {stats['critical_blocks']}")
    print(f"🤖 Agents: {stats['agents_registered']}")
    print(f"📋 Trajectories: {stats['trajectories_loaded']}")


def main():
    print("\n🛡️" * 20)
    print("\n  SCALAR FINANCIAL BODYGUARD")
    print("  Multi-Agent Fraud Detection System")
    print("\n🛡️" * 20)
    
    demo_upi_scam()
    demo_digital_arrest()
    demo_kyc_phishing()
    demo_investment_scam()
    demo_loan_document()
    show_stats()
    
    print("\n" + "=" * 60)
    print("  ✅ Demo Complete!")
    print("  📞 Report scams: 1930")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
