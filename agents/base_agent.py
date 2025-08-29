"""
Base Agent Class - Common functionality for all agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system

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
        print(f"\n🤖 {self.name.upper()} - Processing with {self.reasoning_pattern.value.upper()} reasoning")
        print("=" * 60)
        
        # Set the reasoning pattern on the LLM
        if hasattr(llm, 'set_reasoning_pattern'):
            llm.set_reasoning_pattern(self.reasoning_pattern)
        
        # Invoke LLM
        response = llm.invoke(messages)
        content = getattr(response, "content", str(response))
        reasoning_steps = getattr(response, "reasoning_steps", [])
        
        # Log to memory if available
        if session_memory:
            self._log_to_memory(session_memory, content, reasoning_steps, **kwargs)
        
        # Log reasoning pattern usage
        self.memory_logger.log_agent_reasoning(self.name, self.reasoning_pattern, reasoning_steps)
        
        print(f"✅ {self.name} completed")
        print("=" * 60)
        
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
    
    def format_messages(self, **kwargs) -> List[Any]:
        """Format messages using the agent's prompt template."""
        return self.prompt_template.format_messages(**kwargs)
