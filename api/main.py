"""
Scalar API - Financial Bodyguard Multi-Agent Service
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
sys.path.insert(0, '/app')

from antigravity.agents.financial_bodyguard import get_bodyguard, analyze
from antigravity.agents.specialists import (
    UPIFraudAgent, PhishingAgent, ImpersonationAgent,
    DocumentAnalystAgent, InvestmentFraudAgent
)

app = FastAPI(
    title="Scalar - Financial Bodyguard API",
    description="Multi-Agent Protection System for Users 35+",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: List[WebSocket] = []


class AnalyzeRequest(BaseModel):
    message: str
    user_age: int = 45
    language: str = "en"


class DocumentRequest(BaseModel):
    document_text: str
    document_type: str = "loan"


class TrajectoryResponse(BaseModel):
    trajectories: List[Dict]
    count: int


@app.get("/health")
async def health():
    bodyguard = get_bodyguard()
    return {
        "status": "healthy",
        "service": "scalar-financial-bodyguard",
        "version": "2.0.0",
        "stats": bodyguard.get_stats(),
        "agents": list(bodyguard.specialists.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/agents")
async def list_agents():
    """List all specialist agents"""
    bodyguard = get_bodyguard()
    return {
        "orchestrator": {
            "id": bodyguard.agent_id,
            "name": bodyguard.name,
            "role": bodyguard.role.value
        },
        "specialists": [
            {
                "id": a.agent_id,
                "name": a.name,
                "role": a.role.value,
                "description": a.description
            }
            for a in bodyguard.specialists.values()
        ]
    }


@app.get("/trajectories")
async def get_trajectories():
    """Get fraud trajectory database"""
    bodyguard = get_bodyguard()
    return {
        "trajectories": bodyguard.trajectories,
        "count": len(bodyguard.trajectories)
    }


@app.post("/analyze")
async def analyze_message(request: AnalyzeRequest):
    """Analyze message using multi-agent system"""
    result = analyze(request.message, request.user_age)
    
    # Broadcast to WebSocket
    await broadcast({
        "type": "analysis",
        "threat_level": result.threat_level,
        "risk_score": result.risk_score
    })
    
    return {
        "success": True,
        "threat_level": result.threat_level,
        "risk_score": result.risk_score,
        "primary_threat": result.primary_threat,
        "summary": result.summary,
        "hindi_summary": result.hindi_summary,
        "recommendations": result.recommendations,
        "agent_findings": result.agent_findings,
        "matched_trajectory": result.matched_trajectory,
        "emergency_action": result.emergency_action,
        "timestamp": result.timestamp
    }


@app.post("/analyze/quick")
async def quick_analyze(message: str, user_age: int = 45):
    """Quick analysis endpoint"""
    result = analyze(message, user_age)
    return {
        "threat_level": result.threat_level,
        "risk_score": result.risk_score,
        "summary": result.summary,
        "hindi": result.hindi_summary,
        "action": result.recommendations[0] if result.recommendations else "Stay safe"
    }


@app.post("/analyze/document")
async def analyze_document(request: DocumentRequest):
    """Analyze loan or insurance document"""
    doc_agent = DocumentAnalystAgent()
    result = doc_agent.analyze(request.document_text, request.document_type)
    return {
        "success": True,
        "document_type": request.document_type,
        **result
    }


@app.post("/agent/{agent_id}/analyze")
async def use_specific_agent(agent_id: str, message: str):
    """Use a specific specialist agent"""
    bodyguard = get_bodyguard()
    agent = bodyguard.specialists.get(agent_id)
    
    if not agent:
        raise HTTPException(404, f"Agent {agent_id} not found")
    
    result = agent.analyze(message)
    return {
        "agent": agent_id,
        "agent_name": agent.name,
        **result
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    
    bodyguard = get_bodyguard()
    
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to Financial Bodyguard",
        "stats": bodyguard.get_stats()
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "analyze":
                result = analyze(
                    msg.get("message", ""),
                    msg.get("user_age", 45)
                )
                await websocket.send_json({
                    "type": "result",
                    "threat_level": result.threat_level,
                    "risk_score": result.risk_score,
                    "summary": result.summary,
                    "hindi": result.hindi_summary,
                    "recommendations": result.recommendations
                })
    except WebSocketDisconnect:
        connections.remove(websocket)


async def broadcast(event: Dict):
    for conn in connections:
        try:
            await conn.send_json(event)
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
