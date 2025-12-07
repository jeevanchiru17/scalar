#!/usr/bin/env python3
"""
Scalar Financial Bodyguard - Demo with Official Google ADK
Run agents using: adk web OR python demo_adk.py
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    else:
        print("❌ Set GOOGLE_API_KEY in .env file")
        exit(1)

from agents.adk_agents import (
    financial_bodyguard,
    upi_fraud_agent,
    phishing_agent,
    impersonation_agent,
    investment_agent,
    detect_upi_fraud,
    detect_phishing,
    detect_impersonation,
    detect_investment_fraud
)


def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def demo_tools():
    """Demo the fraud detection tools directly"""
    
    print_header("TOOL TEST 1: UPI Collect Scam")
    result = detect_upi_fraud("You won Rs 50,000! Accept UPI collect request to receive prize!")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Threats: {result['threats']}")
    print(f"हिंदी: {result['hindi']}")
    
    print_header("TOOL TEST 2: Fake KYC Phishing")
    result = detect_phishing("Dear Customer, Your KYC expired. Update now: bit.ly/sbi-kyc or download sbi-update.apk")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Indicators: {result['indicators']}")
    print(f"हिंदी: {result['hindi']}")
    
    print_header("TOOL TEST 3: Digital Arrest Scam")
    result = detect_impersonation("This is CBI. Your Aadhaar is linked to money laundering. Warrant issued. Pay Rs 2 lakh fine to avoid arrest. Do not disconnect.")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Authorities Claimed: {result['authority_claims']}")
    print(f"हिंदी: {result['hindi']}")
    
    print_header("TOOL TEST 4: Crypto Investment Scam")
    result = detect_investment_fraud("Join our crypto trading group! Guaranteed 15% monthly return! Risk-free investment!")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Indicators: {result['indicators']}")
    print(f"हिंदी: {result['hindi']}")


def show_agents():
    """Show available ADK agents"""
    print_header("GOOGLE ADK AGENTS")
    
    agents = [
        ("🛡️", financial_bodyguard, "Root Orchestrator"),
        ("📱", upi_fraud_agent, "UPI Specialist"),
        ("🔗", phishing_agent, "Phishing Specialist"),
        ("👮", impersonation_agent, "Impersonation Specialist"),
        ("📈", investment_agent, "Investment Specialist"),
    ]
    
    for emoji, agent, role in agents:
        print(f"\n{emoji} {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Role: {role}")
        print(f"   Tools: {len(agent.tools) if agent.tools else 0}")
        if hasattr(agent, 'sub_agents') and agent.sub_agents:
            print(f"   Sub-agents: {len(agent.sub_agents)}")


def main():
    print("\n🛡️" * 20)
    print("\n  SCALAR FINANCIAL BODYGUARD")
    print("  Official Google ADK Implementation")
    print("\n🛡️" * 20)
    
    # Show agents
    show_agents()
    
    # Demo tools
    demo_tools()
    
    print("\n" + "=" * 60)
    print("  ✅ ADK Demo Complete!")
    print("\n  To run with ADK Web UI:")
    print("  $ adk web agents/")
    print("\n  📞 Report scams: 1930")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
