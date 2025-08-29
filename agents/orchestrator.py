"""
Orchestrator Agent - Coordinates the workflow between different specialist agents
"""

from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern
from .base_agent import BaseAgent

ORCHESTRATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Orchestrator for GapLens Skills Analysis System.

Your task is to coordinate the workflow between specialist agents for skills analysis.

Given the current state, determine the next step:
- analysis: Analyze skill gaps and generate recommendations  
- decision: Make final actionable recommendations
- done: Workflow complete

Consider the flow: perception → analysis → decision → done

Output ONLY one word: analysis|decision|done."""),
    ("human", "intent={intent}\nentities={entities}\nanalysis={analysis}\ndecision={decision}")
])

class OrchestratorAgent(BaseAgent):
    """Agent for coordinating workflow between specialist agents."""
    
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            reasoning_pattern=ReasoningPattern.AGENT,  # Multi-agent reasoning
            prompt_template=ORCHESTRATOR_PROMPT
        )
    
    def process(self, state: dict, llm) -> str:
        """Decide which agent should run next based on current state."""
        # Format messages
        messages = self.format_messages(
            intent=state.get("intent"),
            entities=state.get("entities"),
            analysis=state.get("analysis"),
            decision=state.get("decision"),
        )
        
        # Invoke LLM with proper logging
        step = self.invoke_llm(llm, messages)
        step = step.strip().lower()
        
        # Simple validation - let the LLM make the decision, only fallback for invalid responses
        if step not in {"analysis", "decision", "done"}:
            # Let the LLM try again with a clearer prompt
            step = "analysis"  # Default to starting with analysis
        
        return step

# Legacy function for backward compatibility
def decide_next_step(state: dict, llm) -> str:
    """Decide which agent should run next based on current state."""
    agent = OrchestratorAgent()
    return agent.process(state, llm) 