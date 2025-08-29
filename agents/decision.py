"""
Decision Agent - Makes final recommendations for skills gap solutions
"""

from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern
from .base_agent import BaseAgent

DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Decision Agent for GapLens Skills Analysis System.

Your task is to provide a final, actionable recommendation based on the analysis.

Provide:
1. Primary recommendation (upskill/transfer/hire)
2. Specific team member(s) and timeline
3. Risk assessment
4. Alternative options
5. Implementation steps
6. Success metrics

Format as a clear, structured decision with actionable next steps."""),
    ("human", "Project Context: {question}\nAnalysis: {analysis}")
])

class DecisionAgent(BaseAgent):
    """Agent for making final actionable recommendations."""
    
    def __init__(self):
        super().__init__(
            name="Decision",
            reasoning_pattern=ReasoningPattern.TOT,  # Tree of Thoughts reasoning
            prompt_template=DECISION_PROMPT
        )
    
    def process(self, question: str, analysis: str, llm, session_memory=None) -> str:
        """Make a final decision using the decision agent."""
        print(f"📋 Analysis input length: {len(analysis)} characters")
        print("🤖 Sending decision request to LLM...")
        
        # Format messages
        messages = self.format_messages(
            question=question,
            analysis=analysis
        )
        
        # Invoke LLM with proper logging
        decision = self.invoke_llm(llm, messages, session_memory)
        
        # Update session data if available
        if session_memory:
            session_memory.update_session_data("decision", decision)
            session_memory.update_session_data("current_step", "completed")
        
        return decision

# Legacy function for backward compatibility
def make_decision(question: str, analysis: str, llm, session_memory=None) -> str:
    """Make a final decision using the decision agent."""
    agent = DecisionAgent()
    return agent.process(question, analysis, llm, session_memory) 