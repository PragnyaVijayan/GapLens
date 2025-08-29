"""
Decision Agent - Makes final recommendations for skills gap solutions
"""

from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory
from .base_agent import BaseAgent

DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Decision Agent for GapLens Skills Analysis System.

CRITICAL: You must return ONLY a valid JSON object. NO additional text, explanations, or verbose output.

## Output Format:
Return ONLY this exact JSON structure with NO additional text:

{{
  "decision_summary": "<one sentence summary>",
  "primary_strategy": "upskill|transfer|hire",
  "action_plan": {{
    "immediate_actions": ["<action1>", "<action2>"],
    "timeline_weeks": <number>,
    "key_milestones": ["<milestone1>", "<milestone2>"]
  }},
  "team_assignment": {{
    "primary_owner": "<Full Name>",
    "support_team": ["<Name1>", "<Name2>"],
    "responsibilities": {{
      "<Name1>": "<specific responsibility>",
      "<Name2>": "<specific responsibility>"
    }}
  }},
  "risk_management": {{
    "primary_risks": ["<risk1>", "<risk2>"],
    "mitigation_strategies": ["<strategy1>", "<strategy2>"],
    "contingency_plan": "<brief contingency>"
  }},
  "success_criteria": {{
    "quantitative": ["<metric1>", "<metric2>"],
    "qualitative": ["<outcome1>", "<outcome2>"]
  }},
  "next_review_date": "<when to reassess>"
}}

## STRICT RULES:
- Return ONLY the JSON object above
- NO explanations, NO verbose text, NO additional information
- Use full employee names from the data
- Keep all text fields brief and focused
- If no data available for a section, use empty arrays []
- Validate JSON before returning
"""),
    ("human", "Question: {question}\n\nAnalysis: {analysis}")
])

class DecisionAgent(BaseAgent):
    """Agent for making final actionable recommendations."""
    
    def __init__(self):
        super().__init__(
            name="Decision",
            reasoning_pattern=ReasoningPattern.TOT,  # Tree of Thoughts reasoning
            prompt_template=DECISION_PROMPT
        )
    
    def process(self, question: str, analysis: str, llm, session_memory: SessionMemory = None) -> str:
        """Make a final decision using the decision agent."""
        print(f"📋 Analysis input length: {len(analysis)} characters")
        print("🤖 Sending decision request to LLM...")
        
        try:
            # Format messages
            messages = self.format_messages(
                question=question,
                analysis=analysis
            )
            
            # Invoke LLM with proper logging
            decision = self.invoke_llm(llm, messages, session_memory)
            print(f"🎯 Decision Output: {decision}")
            
            # Update session data if available
            if session_memory:
                session_memory.update_session_data("decision", decision)
                session_memory.update_session_data("current_step", "completed")
            
            return decision
            
        except Exception as e:
            error_msg = f"Error during decision making: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Log error to memory if available
            if session_memory:
                session_memory.add_entry(
                    agent="decision",
                    content=error_msg,
                    reasoning_pattern=ReasoningPattern.TOT,
                    reasoning_steps=["Error occurred during decision phase"],
                    confidence=0.1,
                    metadata={"error": str(e), "question": question, "analysis": analysis}
                )
            
            return error_msg

# Legacy function for backward compatibility
def make_decision(question: str, analysis: str, llm, session_memory: SessionMemory = None) -> str:
    """Make a final decision using the decision agent."""
    agent = DecisionAgent()
    return agent.process(question, analysis, llm, session_memory) 