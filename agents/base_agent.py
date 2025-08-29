"""
Base Agent Class - Common functionality for all agents
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
import json
from config import AGENT_VERBOSE_OUTPUT, AGENT_SHOW_JSON_VALIDATION

class BaseAgent(ABC):
    """Base class for all agents with common functionality."""
    
    def __init__(self, name: str, reasoning_pattern: ReasoningPattern, prompt_template: ChatPromptTemplate):
        self.name = name
        self.reasoning_pattern = reasoning_pattern
        self.prompt_template = prompt_template
        
        # Get memory logger
        _, self.memory_logger = get_memory_system()
    
    @abstractmethod
    def process(self, **kwargs) -> Any:
        """Process the agent's task. Must be implemented by subclasses."""
        pass
    
    def invoke_llm(self, llm, messages: List[Any], session_memory: Optional[SessionMemory] = None, **kwargs) -> Any:
        """Invoke the LLM with proper reasoning pattern and logging."""
        try:
            # Set the reasoning pattern on the LLM
            if hasattr(llm, 'set_reasoning_pattern'):
                llm.set_reasoning_pattern(self.reasoning_pattern)
            
            # Invoke LLM
            response = llm.invoke(messages)
            content = getattr(response, "content", str(response))
            reasoning_steps = getattr(response, "reasoning_steps", [])
            
            # Validate JSON output for agents that should return JSON
            if self.name.lower() in ['perception', 'analysis', 'decision']:
                content = self._validate_and_clean_json(content)
            
            # Log to memory if available
            if session_memory:
                self._log_to_memory(session_memory, content, reasoning_steps, **kwargs)
            
            # Log reasoning pattern usage
            self.memory_logger.log_agent_reasoning(self.name, self.reasoning_pattern, reasoning_steps)
            
            return content
            
        except Exception as e:
            error_msg = f"Error in {self.name} LLM invocation: {str(e)}"
            
            # Log error to memory if available
            if session_memory:
                self._log_error_to_memory(session_memory, error_msg, **kwargs)
            
            raise
    
    def _validate_and_clean_json(self, content: str) -> str:
        """Validate and clean JSON output from LLM."""
        try:
            if AGENT_VERBOSE_OUTPUT:
                print(f"🔍 Validating JSON for {self.name} agent...")
                print(f"   Input: {content[:100]}...")
            
            # Try to extract JSON from the content
            content = content.strip()
            
            # If it starts with { and ends with }, it's already JSON
            if content.startswith('{') and content.endswith('}'):
                # Validate JSON
                json.loads(content)
                if AGENT_VERBOSE_OUTPUT:
                    print(f"   ✅ Valid JSON found")
                return content
            
            # Try to find JSON within the content
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx + 1]
                # Validate JSON
                json.loads(json_content)
                if AGENT_VERBOSE_OUTPUT:
                    print(f"   ✅ JSON extracted from content")
                return json_content
            
            # If no valid JSON found, return empty JSON structure
            if AGENT_VERBOSE_OUTPUT:
                print(f"   ⚠️ No valid JSON found, using fallback structure")
            
            if self.name.lower() == 'perception':
                return '{"intent": "unknown", "entities": [], "normalized_question": "", "context": {}, "analysis_focus": ""}'
            elif self.name.lower() == 'analysis':
                return '{"skill_gaps": [], "upskilling": [], "internal_transfers": [], "hiring": [], "timeline_assessment": "", "risk_factors": [], "success_probability": "low"}'
            elif self.name.lower() == 'decision':
                return '{"decision_summary": "", "primary_strategy": "", "action_plan": {}, "team_assignment": {}, "risk_management": {}, "success_criteria": {}, "next_review_date": ""}'
            
            return content
            
        except json.JSONDecodeError:
            if AGENT_VERBOSE_OUTPUT:
                print(f"   ❌ JSON validation failed, using fallback structure")
            
            # Return empty JSON structure if validation fails
            if self.name.lower() == 'perception':
                return '{"intent": "unknown", "entities": [], "normalized_question": "", "context": {}, "analysis_focus": ""}'
            elif self.name.lower() == 'analysis':
                return '{"skill_gaps": [], "upskilling": [], "internal_transfers": [], "hiring": [], "timeline_assessment": "", "risk_factors": [], "success_probability": "low"}'
            elif self.name.lower() == 'decision':
                return '{"decision_summary": "", "primary_strategy": "", "action_plan": {}, "team_assignment": {}, "risk_management": {}, "success_criteria": {}, "next_review_date": ""}'
            
            return content
    
    def _log_to_memory(self, session_memory: SessionMemory, content: Any, reasoning_steps: List[str], **kwargs):
        """Log agent activity to session memory."""
        metadata = {
            "agent_name": self.name,
            "reasoning_pattern": self.reasoning_pattern.value,
            **kwargs
        }
        
        session_memory.add_entry(
            agent=self.name,
            content=content,
            reasoning_pattern=self.reasoning_pattern,
            reasoning_steps=reasoning_steps,
            confidence=0.8,
            metadata=metadata
        )
    
    def _log_error_to_memory(self, session_memory: SessionMemory, error_msg: str, **kwargs):
        """Log agent error to session memory."""
        metadata = {
            "agent_name": self.name,
            "reasoning_pattern": self.reasoning_pattern.value,
            "error": True,
            **kwargs
        }
        
        session_memory.add_entry(
            agent=self.name,
            content=error_msg,
            reasoning_pattern=self.reasoning_pattern,
            reasoning_steps=[f"Error occurred: {error_msg}"],
            confidence=0.1,
            metadata=metadata
        )
    
    def format_messages(self, **kwargs) -> List[Any]:
        """Format messages using the agent's prompt template."""
        return self.prompt_template.format_messages(**kwargs)
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters. Override in subclasses for specific validation."""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.name,
            "reasoning_pattern": self.reasoning_pattern.value,
            "status": "ready"
        }
