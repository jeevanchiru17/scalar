"""
Financial Bodyguard - Main Orchestrator
Coordinates all specialist agents to protect users from financial fraud

Uses Google ADK multi-agent patterns:
- Hierarchical delegation
- Parallel agent execution
- Agent-to-Agent communication
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from core.adk_core import (
    BaseAgent, AgentRole, Task, TaskResult, TaskStatus,
    AgentContext, MultiAgentOrchestrator, ToolRegistry
)
from agents.specialists import (
    UPIFraudAgent,
    PhishingAgent,
    ImpersonationAgent,
    DocumentAnalystAgent,
    InvestmentFraudAgent
)

# Load trajectories for context
TRAJECTORIES_PATH = Path(__file__).parent.parent / 'data' / 'fraud_trajectories.json'


@dataclass
class ProtectionResult:
    """Result from Financial Bodyguard analysis"""
    threat_level: str  # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float
    primary_threat: Optional[str]
    summary: str
    hindi_summary: str
    recommendations: List[str]
    agent_findings: List[Dict]
    matched_trajectory: Optional[Dict]
    emergency_action: bool
    timestamp: str


class FinancialBodyguardOrchestrator(BaseAgent):
    """
    Main orchestrator that coordinates all specialist agents
    
    Multi-Agent Architecture:
    
    ┌──────────────────────────────────────────────────────┐
    │           FINANCIAL BODYGUARD ORCHESTRATOR           │
    │                   (Root Agent)                       │
    ├──────────────────────────────────────────────────────┤
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
    │  │   UPI   │  │Phishing │  │Imperson │  │Document │ │
    │  │  Agent  │  │  Agent  │  │  Agent  │  │  Agent  │ │
    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
    │                    ┌─────────┐                      │
    │                    │Invest   │                      │
    │                    │ Agent   │                      │
    │                    └─────────┘                      │
    └──────────────────────────────────────────────────────┘
    """
    
    def __init__(self):
        super().__init__(
            agent_id="financial_bodyguard",
            name="Financial Bodyguard",
            role=AgentRole.ORCHESTRATOR,
            description="Protects users 35+ from financial fraud in India"
        )
        
        # Initialize specialist agents
        self.specialists = {
            'upi': UPIFraudAgent(),
            'phishing': PhishingAgent(),
            'impersonation': ImpersonationAgent(),
            'document': DocumentAnalystAgent(),
            'investment': InvestmentFraudAgent()
        }
        
        # Register as sub-agents
        for agent in self.specialists.values():
            self.register_sub_agent(agent)
        
        # Load fraud trajectories
        self.trajectories = self._load_trajectories()
        
        # Stats
        self.stats = {
            'total_analyses': 0,
            'threats_detected': 0,
            'critical_blocks': 0
        }
    
    def _load_trajectories(self) -> List[Dict]:
        """Load fraud trajectory database"""
        if TRAJECTORIES_PATH.exists():
            with open(TRAJECTORIES_PATH) as f:
                data = json.load(f)
                return data.get('fraud_trajectories', [])
        return []
    
    @property
    def system_instruction(self) -> str:
        return """You are the Financial Bodyguard - the master protector of Indians aged 35+ from financial fraud.

You coordinate specialist agents:
1. UPI Fraud Agent - Payment/collect scams
2. Phishing Agent - Fake KYC, malicious links
3. Impersonation Agent - Fake police/CBI calls
4. Document Agent - Loan/insurance analysis
5. Investment Agent - Ponzi schemes, fake trading

Your job:
1. Receive user input (message, call, document)
2. Route to appropriate specialist(s)
3. Aggregate findings
4. Provide clear, actionable advice in English and Hindi

Golden rules:
- Err on the side of caution (protect user)
- For elderly users (60+), be extra protective
- Always provide Hindi translation
- Give emergency number (1930) for critical threats"""
    
    def analyze(self, content: str, user_age: int = 45) -> ProtectionResult:
        """
        Main analysis method - coordinates all specialists
        
        Uses parallel execution for speed, then aggregates results
        """
        self.stats['total_analyses'] += 1
        
        # Determine which agents to consult based on content
        agents_to_use = self._route_to_agents(content)
        
        # Run selected agents (simulated parallel)
        agent_results = []
        for agent_id in agents_to_use:
            agent = self.specialists.get(agent_id)
            if agent:
                result = agent.analyze(content)
                agent_results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_results(agent_results)
        
        # Find matching trajectory
        matched_trajectory = self._match_trajectory(content, aggregated)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            aggregated['threat_level'],
            aggregated['risk_score'],
            user_age
        )
        
        # Generate summaries
        summary, hindi = self._generate_summaries(aggregated, matched_trajectory)
        
        # Update stats
        if aggregated['threat_level'] in ['HIGH', 'CRITICAL']:
            self.stats['threats_detected'] += 1
        if aggregated['threat_level'] == 'CRITICAL':
            self.stats['critical_blocks'] += 1
        
        return ProtectionResult(
            threat_level=aggregated['threat_level'],
            risk_score=aggregated['risk_score'],
            primary_threat=aggregated.get('primary_threat'),
            summary=summary,
            hindi_summary=hindi,
            recommendations=recommendations,
            agent_findings=agent_results,
            matched_trajectory=matched_trajectory,
            emergency_action=aggregated['threat_level'] == 'CRITICAL',
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def analyze_async(self, content: str, user_age: int = 45) -> ProtectionResult:
        """Async version with true parallel execution"""
        self.stats['total_analyses'] += 1
        
        agents_to_use = self._route_to_agents(content)
        
        # Create tasks for parallel execution
        tasks = []
        for agent_id in agents_to_use:
            agent = self.specialists.get(agent_id)
            if agent:
                task = Task(
                    task_id=f"analysis_{agent_id}",
                    task_type="fraud_detection",
                    content=content,
                    context=AgentContext(
                        session_id="live",
                        user_age_group=f"{user_age}+"
                    )
                )
                tasks.append(agent.execute_async(task))
        
        # Execute in parallel
        results = await asyncio.gather(*tasks)
        
        # Convert to agent results
        agent_results = [r.result for r in results]
        
        # Rest same as sync version
        aggregated = self._aggregate_results(agent_results)
        matched_trajectory = self._match_trajectory(content, aggregated)
        recommendations = self._generate_recommendations(
            aggregated['threat_level'],
            aggregated['risk_score'],
            user_age
        )
        summary, hindi = self._generate_summaries(aggregated, matched_trajectory)
        
        return ProtectionResult(
            threat_level=aggregated['threat_level'],
            risk_score=aggregated['risk_score'],
            primary_threat=aggregated.get('primary_threat'),
            summary=summary,
            hindi_summary=hindi,
            recommendations=recommendations,
            agent_findings=agent_results,
            matched_trajectory=matched_trajectory,
            emergency_action=aggregated['threat_level'] == 'CRITICAL',
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _route_to_agents(self, content: str) -> List[str]:
        """
        Smart routing - determine which agents should analyze content
        
        Uses keyword matching for speed, AI for complex cases
        """
        content_lower = content.lower()
        agents = []
        
        # UPI agent triggers
        if any(kw in content_lower for kw in ['upi', 'collect', 'pay', 'gpay', 'phonepe', 'paytm', 'qr', '₹', 'rs']):
            agents.append('upi')
        
        # Phishing agent triggers
        if any(kw in content_lower for kw in ['kyc', 'update', 'verify', 'bank', 'apk', 'download', 'link', 'click']):
            agents.append('phishing')
        
        # Impersonation agent triggers
        if any(kw in content_lower for kw in ['police', 'cbi', 'ed', 'arrest', 'warrant', 'customs', 'parcel']):
            agents.append('impersonation')
        
        # Document agent triggers
        if any(kw in content_lower for kw in ['loan', 'emi', 'insurance', 'policy', 'premium', 'interest rate']):
            agents.append('document')
        
        # Investment agent triggers
        if any(kw in content_lower for kw in ['invest', 'return', 'profit', 'trading', 'crypto', 'forex', 'double']):
            agents.append('investment')
        
        # If no specific match, use core fraud detection agents
        if not agents:
            agents = ['upi', 'phishing', 'impersonation']
        
        return agents
    
    def _aggregate_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""
        if not results:
            return {
                'threat_level': 'SAFE',
                'risk_score': 0.0,
                'primary_threat': None
            }
        
        # Find highest risk
        max_risk = max(r.get('risk_score', 0) for r in results)
        
        # Get primary threat from highest risk agent
        primary_threat = None
        for r in results:
            if r.get('risk_score', 0) == max_risk:
                primary_threat = r.get('agent', 'unknown')
                break
        
        # Determine threat level
        if max_risk >= 0.9:
            threat_level = 'CRITICAL'
        elif max_risk >= 0.7:
            threat_level = 'HIGH'
        elif max_risk >= 0.4:
            threat_level = 'MEDIUM'
        elif max_risk > 0.1:
            threat_level = 'LOW'
        else:
            threat_level = 'SAFE'
        
        return {
            'threat_level': threat_level,
            'risk_score': max_risk,
            'primary_threat': primary_threat,
            'agent_count': len(results),
            'all_risks': [r.get('risk_score', 0) for r in results]
        }
    
    def _match_trajectory(self, content: str, aggregated: Dict) -> Optional[Dict]:
        """Match content against known fraud trajectories"""
        content_lower = content.lower()
        
        best_match = None
        best_score = 0
        
        for trajectory in self.trajectories:
            red_flags = trajectory.get('red_flags', [])
            matches = sum(1 for rf in red_flags if rf.lower() in content_lower)
            
            if matches > best_score:
                best_score = matches
                best_match = trajectory
        
        return best_match if best_score >= 2 else None
    
    def _generate_recommendations(
        self, 
        threat_level: str, 
        risk_score: float,
        user_age: int
    ) -> List[str]:
        """Generate age-appropriate recommendations"""
        
        # Adjust for elderly users
        is_elderly = user_age >= 60
        
        if threat_level == 'CRITICAL':
            recs = [
                "🚨 STOP! Do NOT proceed with this transaction!",
                "🚫 Do NOT share any OTP, PIN, or password",
                "📞 Call Cyber Crime Helpline: 1930",
                "👨‍👩‍👧 Inform a trusted family member immediately",
                "🏦 If you've shared any details, call your bank NOW"
            ]
            if is_elderly:
                recs.insert(0, "👴 Please show this to a younger family member")
        
        elif threat_level == 'HIGH':
            recs = [
                "⚠️ This appears to be a scam - do not proceed",
                "🔒 Do not click any links in this message",
                "📱 Verify sender through official channels only",
                "⏰ Take time to verify - genuine matters can wait"
            ]
        
        elif threat_level == 'MEDIUM':
            recs = [
                "⚡ Exercise caution before proceeding",
                "🔍 Verify the sender's identity",
                "📞 Contact official helpline to confirm"
            ]
        
        else:
            recs = [
                "✅ No immediate threat detected",
                "🔒 Always protect your OTP and PIN",
                "👀 Stay alert for future suspicious messages"
            ]
        
        return recs
    
    def _generate_summaries(
        self, 
        aggregated: Dict, 
        trajectory: Optional[Dict]
    ) -> tuple:
        """Generate English and Hindi summaries"""
        
        threat_level = aggregated['threat_level']
        
        if threat_level == 'CRITICAL':
            summary = "🚨 CRITICAL THREAT! This is almost certainly a scam. Do NOT proceed!"
            hindi = "🚨 गंभीर खतरा! यह निश्चित रूप से धोखाधड़ी है! आगे न बढ़ें! हेल्पलाइन: 1930"
        elif threat_level == 'HIGH':
            summary = "⚠️ HIGH RISK detected. Strong indicators of fraud found."
            hindi = "⚠️ उच्च जोखिम! धोखाधड़ी के संकेत मिले।"
        elif threat_level == 'MEDIUM':
            summary = "⚡ CAUTION advised. Some suspicious elements found."
            hindi = "⚡ सावधान! कुछ संदिग्ध तत्व मिले।"
        else:
            summary = "✅ LOW RISK. No major threats detected."
            hindi = "✅ कम जोखिम। कोई बड़ा खतरा नहीं।"
        
        # Add trajectory info if matched
        if trajectory:
            summary += f"\n\nMatched scam pattern: {trajectory.get('name', 'Unknown')}"
            if trajectory.get('hindi_warning'):
                hindi += f"\n\n{trajectory.get('hindi_warning')}"
        
        return summary, hindi
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return {
            **self.stats,
            'agents_registered': len(self.specialists),
            'trajectories_loaded': len(self.trajectories)
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_bodyguard: Optional[FinancialBodyguardOrchestrator] = None

def get_bodyguard() -> FinancialBodyguardOrchestrator:
    """Get singleton Financial Bodyguard instance"""
    global _bodyguard
    if _bodyguard is None:
        _bodyguard = FinancialBodyguardOrchestrator()
    return _bodyguard


def analyze(content: str, user_age: int = 45) -> ProtectionResult:
    """Quick analyze function"""
    return get_bodyguard().analyze(content, user_age)


async def analyze_async(content: str, user_age: int = 45) -> ProtectionResult:
    """Async analyze function"""
    return await get_bodyguard().analyze_async(content, user_age)
