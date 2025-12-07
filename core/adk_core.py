"""
Scalar Multi-Agent System - Core ADK Architecture
Based on Google Agent Development Kit patterns

This module implements:
- Agent base class with ADK-compatible interface
- Multi-agent orchestration (sequential, parallel, hierarchical)
- Agent-to-Agent (A2A) communication
- Tool function definitions
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import time

# Load environment
from dotenv import load_dotenv
load_dotenv()

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None


# =============================================================================
# CORE TYPES
# =============================================================================

class AgentRole(Enum):
    """Agent roles in multi-agent hierarchy"""
    ORCHESTRATOR = "orchestrator"  # Coordinates other agents
    SPECIALIST = "specialist"       # Domain expertise
    WORKER = "worker"               # Executes specific tasks
    CRITIC = "critic"               # Reviews and validates


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


@dataclass
class AgentContext:
    """Shared context across agents"""
    session_id: str
    user_id: Optional[str] = None
    user_age_group: str = "35+"
    language: str = "en"
    risk_tolerance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task to be executed by an agent"""
    task_id: str
    task_type: str
    content: str
    context: AgentContext
    priority: int = 1
    parent_task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    """Result from agent task execution"""
    task_id: str
    agent_id: str
    status: TaskStatus
    result: Any
    confidence: float
    reasoning: str
    sub_results: List['TaskResult'] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# TOOL DEFINITIONS (ADK Compatible)
# =============================================================================

@dataclass
class ToolDefinition:
    """ADK-compatible tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    

class ToolRegistry:
    """Registry of available tools for agents"""
    
    _tools: Dict[str, ToolDefinition] = {}
    
    @classmethod
    def register(cls, name: str, description: str, parameters: Dict, function: Callable):
        """Register a tool"""
        cls._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            function=function
        )
    
    @classmethod
    def get(cls, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> List[Dict]:
        """List all tools for ADK"""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in cls._tools.values()
        ]
    
    @classmethod
    def execute(cls, name: str, **kwargs) -> Any:
        """Execute a tool"""
        tool = cls._tools.get(name)
        if tool:
            return tool.function(**kwargs)
        raise ValueError(f"Tool {name} not found")


# =============================================================================
# BASE AGENT (ADK Pattern)
# =============================================================================

class BaseAgent(ABC):
    """
    Base Agent class following Google ADK patterns
    
    Key concepts:
    - Each agent has a specific role and capabilities
    - Agents can use tools and call other agents
    - Supports both sync and async execution
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        description: str,
        model: str = "gemini-2.0-flash"
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.description = description
        self.model = model
        
        # Agent state
        self.is_active = True
        self.task_history: List[TaskResult] = []
        self.sub_agents: Dict[str, 'BaseAgent'] = {}
        
        # Gemini client
        self._client = None
        if GENAI_AVAILABLE:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                self._client = genai.Client(api_key=api_key)
    
    @property
    @abstractmethod
    def system_instruction(self) -> str:
        """System instruction for the agent"""
        pass
    
    @property
    def tools(self) -> List[str]:
        """List of tool names this agent can use"""
        return []
    
    def register_sub_agent(self, agent: 'BaseAgent'):
        """Register a sub-agent that this agent can delegate to"""
        self.sub_agents[agent.agent_id] = agent
    
    def execute(self, task: Task) -> TaskResult:
        """
        Execute a task (sync version)
        
        ADK Pattern:
        1. Analyze task
        2. Decide: use tools, delegate, or respond directly
        3. Execute decision
        4. Verify and return result
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze and plan
            plan = self._plan(task)
            
            # Step 2: Execute plan
            if plan.get('delegate_to'):
                # Delegate to sub-agent
                result = self._delegate(task, plan['delegate_to'])
            elif plan.get('use_tools'):
                # Use tools
                result = self._use_tools(task, plan['use_tools'])
            else:
                # Direct response
                result = self._generate_response(task)
            
            # Step 3: Verify result
            verified_result = self._verify(task, result)
            
            execution_time = time.time() - start_time
            
            task_result = TaskResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                status=TaskStatus.COMPLETED,
                result=verified_result,
                confidence=self._calculate_confidence(verified_result),
                reasoning=plan.get('reasoning', ''),
                execution_time=execution_time
            )
            
            self.task_history.append(task_result)
            return task_result
            
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                status=TaskStatus.FAILED,
                result={"error": str(e)},
                confidence=0.0,
                reasoning=f"Execution failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def execute_async(self, task: Task) -> TaskResult:
        """Async version of execute"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, task)
    
    def _plan(self, task: Task) -> Dict[str, Any]:
        """Plan how to handle the task"""
        content = task.content.lower()
        
        # Check if should delegate
        for agent_id, agent in self.sub_agents.items():
            if self._should_delegate(task, agent):
                return {
                    'action': 'delegate',
                    'delegate_to': agent_id,
                    'reasoning': f"Delegating to {agent.name} for specialized handling"
                }
        
        # Check if should use tools
        tools_to_use = []
        for tool_name in self.tools:
            tool = ToolRegistry.get(tool_name)
            if tool and self._tool_matches(task, tool):
                tools_to_use.append(tool_name)
        
        if tools_to_use:
            return {
                'action': 'use_tools',
                'use_tools': tools_to_use,
                'reasoning': f"Using tools: {', '.join(tools_to_use)}"
            }
        
        # Direct response
        return {
            'action': 'respond',
            'reasoning': 'Generating direct response'
        }
    
    def _should_delegate(self, task: Task, agent: 'BaseAgent') -> bool:
        """Determine if task should be delegated to sub-agent"""
        # Override in subclasses for custom logic
        return False
    
    def _tool_matches(self, task: Task, tool: ToolDefinition) -> bool:
        """Check if tool is relevant for task"""
        return True
    
    def _use_tools(self, task: Task, tool_names: List[str]) -> Dict[str, Any]:
        """Execute tools and aggregate results"""
        results = {}
        for tool_name in tool_names:
            try:
                result = ToolRegistry.execute(tool_name, content=task.content)
                results[tool_name] = result
            except Exception as e:
                results[tool_name] = {"error": str(e)}
        return results
    
    def _delegate(self, task: Task, agent_id: str) -> Dict[str, Any]:
        """Delegate task to sub-agent"""
        agent = self.sub_agents.get(agent_id)
        if agent:
            result = agent.execute(task)
            return result.result
        return {"error": f"Agent {agent_id} not found"}
    
    def _generate_response(self, task: Task) -> Dict[str, Any]:
        """Generate response using Gemini"""
        if self._client:
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=task.content,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        temperature=0.7,
                        max_output_tokens=1024
                    )
                )
                return {"response": response.text}
            except Exception as e:
                return {"error": str(e)}
        return {"response": self._fallback_response(task)}
    
    def _fallback_response(self, task: Task) -> str:
        """Fallback when Gemini not available"""
        return f"[{self.name}] Analyzed: {task.content[:100]}..."
    
    def _verify(self, task: Task, result: Dict) -> Dict[str, Any]:
        """Verify and potentially improve result"""
        # Override in subclasses for custom verification
        return result
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score for result"""
        if "error" in result:
            return 0.0
        return 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent state"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "is_active": self.is_active,
            "sub_agents": list(self.sub_agents.keys()),
            "tools": self.tools,
            "task_count": len(self.task_history)
        }


# =============================================================================
# MULTI-AGENT ORCHESTRATOR
# =============================================================================

class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents following ADK patterns
    
    Supports:
    - Sequential execution
    - Parallel execution
    - Hierarchical delegation
    - Agent-to-Agent communication
    """
    
    def __init__(self, orchestrator_id: str = "main_orchestrator"):
        self.orchestrator_id = orchestrator_id
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_log: List[Dict] = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
    
    def execute_sequential(self, task: Task, agent_order: List[str]) -> List[TaskResult]:
        """Execute task through agents in sequence"""
        results = []
        current_context = task.context
        
        for agent_id in agent_order:
            agent = self.agents.get(agent_id)
            if agent:
                # Create task with updated context
                agent_task = Task(
                    task_id=f"{task.task_id}_{agent_id}",
                    task_type=task.task_type,
                    content=task.content,
                    context=current_context,
                    parent_task_id=task.task_id
                )
                
                result = agent.execute(agent_task)
                results.append(result)
                
                # Pass result to next agent via context
                current_context.metadata['previous_result'] = result.result
                
                self._log_execution(agent_id, result)
        
        return results
    
    async def execute_parallel(self, task: Task, agent_ids: List[str]) -> List[TaskResult]:
        """Execute task across agents in parallel"""
        tasks = []
        
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                agent_task = Task(
                    task_id=f"{task.task_id}_{agent_id}",
                    task_type=task.task_type,
                    content=task.content,
                    context=task.context,
                    parent_task_id=task.task_id
                )
                tasks.append(agent.execute_async(agent_task))
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            self._log_execution(result.agent_id, result)
        
        return list(results)
    
    def execute_hierarchical(self, task: Task, root_agent_id: str) -> TaskResult:
        """Execute with hierarchical delegation"""
        root_agent = self.agents.get(root_agent_id)
        if not root_agent:
            raise ValueError(f"Agent {root_agent_id} not found")
        
        # Root agent decides how to handle and may delegate
        result = root_agent.execute(task)
        self._log_execution(root_agent_id, result)
        
        return result
    
    def aggregate_results(self, results: List[TaskResult]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""
        if not results:
            return {"status": "no_results"}
        
        # Calculate combined confidence
        total_confidence = sum(r.confidence for r in results)
        avg_confidence = total_confidence / len(results)
        
        # Find highest risk/priority result
        max_risk_result = max(results, key=lambda r: 1 - r.confidence)
        
        # Aggregate all findings
        all_findings = []
        for r in results:
            if isinstance(r.result, dict):
                all_findings.append({
                    "agent": r.agent_id,
                    "result": r.result,
                    "confidence": r.confidence
                })
        
        return {
            "status": "aggregated",
            "agent_count": len(results),
            "avg_confidence": avg_confidence,
            "primary_result": max_risk_result.result,
            "all_findings": all_findings,
            "execution_times": [r.execution_time for r in results]
        }
    
    def _log_execution(self, agent_id: str, result: TaskResult):
        """Log execution for audit trail"""
        self.execution_log.append({
            "agent_id": agent_id,
            "task_id": result.task_id,
            "status": result.status.value,
            "confidence": result.confidence,
            "execution_time": result.execution_time,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_execution_log(self) -> List[Dict]:
        """Get execution audit log"""
        return self.execution_log


# =============================================================================
# AGENT FACTORY
# =============================================================================

class AgentFactory:
    """Factory for creating pre-configured agents"""
    
    @staticmethod
    def create_fraud_specialist(agent_id: str, fraud_type: str) -> BaseAgent:
        """Create a fraud detection specialist agent"""
        from antigravity.agents.specialists import FraudSpecialistAgent
        return FraudSpecialistAgent(agent_id, fraud_type)
    
    @staticmethod
    def create_document_analyst(agent_id: str) -> BaseAgent:
        """Create a document analysis agent"""
        from antigravity.agents.specialists import DocumentAnalystAgent
        return DocumentAnalystAgent(agent_id)
    
    @staticmethod
    def create_bodyguard_orchestrator() -> MultiAgentOrchestrator:
        """Create fully configured Financial Bodyguard system"""
        orchestrator = MultiAgentOrchestrator("financial_bodyguard")
        
        # Will register agents when specialists module is created
        return orchestrator
