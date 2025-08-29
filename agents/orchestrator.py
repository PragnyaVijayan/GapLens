"""
Orchestrator Agent - Coordinates the workflow between different specialist agents
"""

from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory
from .base_agent import BaseAgent
from .perception import perceive_input
from .analysis import analyze_facts
from .decision import DecisionAgent

ORCHESTRATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Orchestrator for GapLens Skills Analysis System.

Your task is to coordinate the workflow between specialist agents for skills analysis.

Given the current state, determine the next step:
- analysis: Run analysis if no analysis exists yet or if analysis is incomplete
- decision: Run decision if analysis exists and is complete, but no decision exists
- done: Workflow complete if both analysis and decision exist

## Rules
- Keep responses concise and focused
- Base analysis on provided information only
- Do not add any other text to the response

Workflow progression:
1. perception → analysis (if no analysis)
2. analysis → decision (if analysis exists but no decision)
3. decision → done (if both analysis and decision exist)

Current state:
- intent: {intent}
- entities: {entities}
- analysis: {analysis}
- decision: {decision}

Output ONLY one word: analysis|decision|done"""),
    ("human", "What is the next step?")


])

class OrchestratorAgent(BaseAgent):
    """Coordinates the skills analysis workflow across perception, analysis, and decision agents."""

    def __init__(self):
        super().__init__(
            name="Orchestrator",
            reasoning_pattern=ReasoningPattern.AGENT,
            prompt_template=ORCHESTRATOR_PROMPT
        )

    def process(self, state: dict, llm) -> str:
        """Determine the next step in the workflow based on current state."""
        # Simple logic-based decision making
        if not state.get("analysis"):
            return "analysis"
        if not state.get("decision"):
            return "decision"
        return "done"

    def run_workflow(self, user_question: str, llm, session_memory: SessionMemory) -> Dict[str, Any]:
        """Run the complete perception-analysis-decision workflow."""
        print("🔁 Orchestrator running full workflow...")
        
        # Step 1: Perception
        print("\n👁️ Starting Perception Phase...")
        perception_result = perceive_input(user_question, llm, session_memory)
        print(f"✅ Perception completed: {perception_result['intent']}")
        
        # Initialize state with perception output
        state = {
            "intent": perception_result.get("intent"),
            "entities": perception_result.get("entities", []),
            "normalized_question": perception_result.get("normalized_question"),
            "context": perception_result.get("context"),
            "perception_output": perception_result,
            "analysis": None,
            "decision": None
        }
        
        # Step 2: Analysis
        print("\n🧠 Starting Analysis Phase...")
        analysis_result = analyze_facts(
            state["normalized_question"], 
            llm, 
            session_memory
        )
        state["analysis"] = analysis_result
        print(f"✅ Analysis completed: {len(analysis_result)} characters")
        
        # Step 3: Decision
        print("\n🎯 Starting Decision Phase...")
        decision_agent = DecisionAgent()
        decision_result = decision_agent.process(
            state["normalized_question"], 
            analysis_result, 
            llm, 
            session_memory
        )
        state["decision"] = decision_result
        print(f"✅ Decision completed: {len(decision_result)} characters")
        
        # Final workflow result
        workflow_result = {
            "intent": state["intent"],
            "entities": state["entities"],
            "normalized_question": state["normalized_question"],
            "context": state["context"],
            "perception_output": state["perception_output"],
            "analysis": state["analysis"],
            "decision": state["decision"],
            "workflow_status": "completed"
        }
        
        print("\n🎉 Workflow completed successfully!")
        return workflow_result

    def validate_workflow_state(self, state: dict) -> Dict[str, Any]:
        """Validate the current workflow state and return validation results."""
        validation = {
            "perception_complete": bool(state.get("intent") and state.get("entities")),
            "analysis_complete": bool(state.get("analysis")),
            "decision_complete": bool(state.get("decision")),
            "workflow_complete": bool(state.get("analysis") and state.get("decision")),
            "missing_components": []
        }
        
        if not validation["perception_complete"]:
            validation["missing_components"].append("perception")
        if not validation["analysis_complete"]:
            validation["missing_components"].append("analysis")
        if not validation["decision_complete"]:
            validation["missing_components"].append("decision")
            
        return validation

# Legacy function for backward compatibility
def decide_next_step(state: dict, llm) -> str:
    """Decide which agent should run next based on current state."""
    agent = OrchestratorAgent()
    return agent.process(state, llm)
