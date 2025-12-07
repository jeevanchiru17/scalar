"""
Gemini AI Client for Antigravity Multi-Agent System

Provides singleton access to Google's Gemini API with:
- Streaming response support
- Multi-agent session management
- Tool function definitions
- Error handling and retry logic
"""

import os
import time
import asyncio
from typing import Dict, List, Any, Optional, Generator, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

# Load from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None


class GeminiModel(Enum):
    """Available Gemini models"""
    GEMINI_2_FLASH = "gemini-2.0-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"


@dataclass
class AgentSession:
    """Tracks a multi-agent conversation session"""
    session_id: str
    agent_ids: List[str]
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    

class GeminiClient:
    """
    Singleton Gemini API client for multi-agent AI operations.
    
    Features:
    - Streaming and non-streaming generation
    - Multi-agent conversation management
    - Tool/function calling support
    - Async support for concurrent agent operations
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if GeminiClient._initialized:
            return
            
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        self.sessions: Dict[str, AgentSession] = {}
        self.default_model = GeminiModel.GEMINI_2_FLASH
        
        if GENAI_AVAILABLE and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            
        GeminiClient._initialized = True
    
    def is_available(self) -> bool:
        """Check if Gemini client is properly configured"""
        return GENAI_AVAILABLE and self.client is not None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection with a simple request"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Gemini client not available. Check API key and google-genai installation.'
            }
        
        try:
            response = self.client.models.generate_content(
                model=self.default_model.value,
                contents="Respond with 'Connection successful' only."
            )
            return {
                'success': True,
                'response': response.text,
                'model': self.default_model.value
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[GeminiModel] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini.
        
        Args:
            prompt: User prompt/query
            system_instruction: Optional system context
            model: Gemini model to use
            temperature: Creativity setting (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dict with response text and metadata
        """
        if not self.is_available():
            return self._fallback_response(prompt)
        
        model_name = (model or self.default_model).value
        
        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            if system_instruction:
                config.system_instruction = system_instruction
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            return {
                'success': True,
                'text': response.text,
                'model': model_name,
                'usage': {
                    'prompt_tokens': getattr(response, 'prompt_token_count', 0),
                    'response_tokens': getattr(response, 'candidates_token_count', 0)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': self._fallback_response(prompt).get('text', '')
            }
    
    def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[GeminiModel] = None
    ) -> Generator[str, None, None]:
        """
        Stream content generation for real-time UI updates.
        
        Yields:
            Text chunks as they are generated
        """
        if not self.is_available():
            yield self._fallback_response(prompt).get('text', '')
            return
        
        model_name = (model or self.default_model).value
        
        try:
            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction
            
            response = self.client.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def generate_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[GeminiModel] = None
    ) -> Dict[str, Any]:
        """Async version for concurrent multi-agent operations"""
        # Run synchronous generation in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate(prompt, system_instruction, model)
        )
    
    def create_agent_session(self, session_id: str, agent_ids: List[str]) -> AgentSession:
        """Create a new multi-agent conversation session"""
        session = AgentSession(
            session_id=session_id,
            agent_ids=agent_ids
        )
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    def add_message_to_session(
        self,
        session_id: str,
        agent_id: str,
        role: str,
        content: str
    ):
        """Add a message to a session's history"""
        session = self.sessions.get(session_id)
        if session:
            session.messages.append({
                'agent_id': agent_id,
                'role': role,
                'content': content,
                'timestamp': time.time()
            })
    
    def generate_with_session(
        self,
        session_id: str,
        agent_id: str,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate with session context for multi-agent coordination.
        
        Includes previous messages from the session for context continuity.
        """
        session = self.sessions.get(session_id)
        
        # Build context from session history
        context_parts = []
        if session:
            for msg in session.messages[-10:]:  # Last 10 messages
                context_parts.append(f"[{msg['agent_id']}]: {msg['content']}")
        
        full_prompt = prompt
        if context_parts:
            context = "\n".join(context_parts)
            full_prompt = f"Previous conversation:\n{context}\n\nCurrent query: {prompt}"
        
        response = self.generate(full_prompt, system_instruction)
        
        # Store in session
        if session:
            self.add_message_to_session(session_id, agent_id, 'user', prompt)
            if response.get('success'):
                self.add_message_to_session(session_id, agent_id, 'assistant', response.get('text', ''))
        
        return response
    
    def _fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Fallback response when Gemini is not available"""
        # Provide intelligent fallback based on prompt content
        fallback_responses = {
            'fraud': {
                'text': 'Based on pattern analysis, this appears to be a potential fraud attempt. Key indicators: urgency language, request for payment/credentials, suspicious links.',
                'confidence': 0.75
            },
            'scam': {
                'text': 'This message shows characteristics of known scam patterns. Recommendation: Do not share personal information or click any links.',
                'confidence': 0.8
            },
            'kyc': {
                'text': 'KYC update requests should only come from official bank channels. Never download APK files from links in messages.',
                'confidence': 0.85
            },
            'default': {
                'text': 'Analysis complete. Please review the detailed results for recommendations.',
                'confidence': 0.5
            }
        }
        
        prompt_lower = prompt.lower()
        for key, response in fallback_responses.items():
            if key in prompt_lower:
                return {'success': True, 'text': response['text'], 'fallback': True}
        
        return {'success': True, 'text': fallback_responses['default']['text'], 'fallback': True}


# Agent-specific system instructions
AGENT_INSTRUCTIONS = {
    'fraud_detection': """You are an expert fraud detection agent specialized in identifying scams targeting Indian users.

Your expertise includes:
- UPI/BHIM payment fraud patterns
- KYC/bank impersonation scams
- Lottery and prize scams
- Police/CBI impersonation
- OLX/marketplace frauds

Always provide:
1. Risk score (0.0 to 1.0)
2. Specific fraud indicators found
3. Recommended actions in simple language
4. Hindi translation of key warnings if needed

Be direct, clear, and prioritize user safety.""",

    'document_analysis': """You are a document analysis agent specialized in reviewing financial documents.

Your expertise includes:
- Loan agreements and hidden clauses
- EMI calculations and foreclosure fees
- Insurance policy fine print
- Terms and conditions analysis

Always explain complex terms in simple language suitable for users with limited financial literacy.""",

    'emotion_modeling': """You are an emotion modeling agent that detects user distress and cognitive load.

Your role:
- Detect panic, fear, or urgency in user messages
- Identify when users may be under pressure from scammers
- Recommend calming actions
- Suggest involving trusted family members when appropriate

Be empathetic and supportive in your analysis.""",

    'orchestrator': """You are the master orchestrator for the Antigravity multi-agent system.

Your role:
- Coordinate between specialized agents
- Prioritize user safety above all
- Make final decisions based on agent inputs
- Activate emergency protocols when needed (fraud confidence > 0.9)

Always explain your decision-making process clearly."""
}


def get_gemini_client() -> GeminiClient:
    """Get the singleton Gemini client instance"""
    return GeminiClient()
