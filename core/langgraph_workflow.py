"""
LangGraph Workflow Implementation for GapLens Multi-Agent System
"""

from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from core.memory_system import SessionMemory, ReasoningPattern
# Import functions directly to avoid circular imports
from agents.perception import perceive_input
from agents.analysis import analyze_facts

# Global LLM instances for the workflow
_perception_llm = None
_reasoner_llm = None

def set_llms(perception_llm, reasoner_llm):
    """Set the LLM instances for the workflow."""
    global _perception_llm, _reasoner_llm
    _perception_llm = perception_llm
    _reasoner_llm = reasoner_llm

class WorkflowState(TypedDict):
    """State for the workflow execution."""
    question: str
    memory: SessionMemory
    intent: str
    entities: List[str]
    normalized_question: str
    analysis: str
    decision: str
    step: str
    project_id: str
    scope: str

def create_workflow(perception_llm, reasoner_llm, display_limit: int = None):
    """Create the LangGraph workflow for the multi-agent system."""
    
    # Set LLMs globally
    set_llms(perception_llm, reasoner_llm)
    
    # Create the workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes for each agent
    workflow.add_node("perception", perception_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("orchestrator", orchestrator_node)
    
    # Set the entry point
    workflow.set_entry_point("perception")
    
    # Add conditional edges based on orchestrator decisions
    workflow.add_conditional_edges(
        "orchestrator",
        route_to_next_step,
        {
            "analysis": "analysis", 
            "decision": "decision",
            "done": END
        }
    )
    
    # Add edges for the workflow
    workflow.add_edge("perception", "orchestrator")
    workflow.add_edge("analysis", "orchestrator")
    workflow.add_edge("decision", "orchestrator")
    
    # Compile the workflow
    return workflow.compile()

def perception_node(state: WorkflowState) -> WorkflowState:
    """Execute the perception agent."""
    print("\n👁️ PERCEPTION NODE - Processing user input...")
    
    try:
        # Get the question from state
        question = state["question"]
        
        # Create session memory if not exists
        if not state.get("memory"):
            state["memory"] = SessionMemory()
        
        # Execute perception
        perception_result = perceive_input(question, _perception_llm, state["memory"])
        
        # Update state with perception results
        state.update({
            "intent": perception_result.get("intent", "skill_analysis"),
            "entities": perception_result.get("entities", []),
            "normalized_question": perception_result.get("normalized_question", question),
            "step": "perception_complete"
        })
        
        print(f"✅ Perception completed: {perception_result['intent']}")
        
    except Exception as e:
        print(f"❌ Error in perception node: {e}")
        # Set default values on error
        state.update({
            "intent": "skill_analysis",
            "entities": [],
            "normalized_question": state["question"],
            "step": "perception_error"
        })
    
    return state

def analysis_node(state: WorkflowState) -> WorkflowState:
    """Execute the analysis agent."""
    print("\n🧠 ANALYSIS NODE - Analyzing skill gaps and generating recommendations...")
    
    try:
        # Get required data from state
        question = state.get("normalized_question", state["question"])
        project_id = state.get("project_id", None)
        scope = state.get("scope", "company")
        
        # Execute analysis using the cleaned analyze_facts function with project-specific parameters
        analysis_result = analyze_facts(question, _reasoner_llm, state["memory"], project_id, scope)
        
        # Update state with analysis results
        state.update({
            "analysis": analysis_result,
            "step": "analysis_complete"
        })
        
        print(f"✅ Analysis completed: {len(analysis_result)} characters generated")
        if project_id:
            print(f"🎯 Project-specific analysis for: {project_id}")
        
    except Exception as e:
        print(f"❌ Error in analysis node: {e}")
        state.update({
            "analysis": f"Error during analysis: {str(e)}",
            "step": "analysis_error"
        })
    
    return state

def decision_node(state: WorkflowState) -> WorkflowState:
    """Execute the decision agent."""
    print("\n🎯 DECISION NODE - Making final actionable recommendations...")
    
    try:
        # Get required data from state
        question = state.get("normalized_question", state["question"])
        analysis = state.get("analysis", "")
        
        # Create and execute decision agent dynamically to avoid circular imports
        from agents.decision import DecisionAgent
        decision_agent = DecisionAgent()
        decision_result = decision_agent.process(question, analysis, _reasoner_llm, state["memory"])
        
        # Update state with decision results
        state.update({
            "decision": decision_result,
            "step": "decision_complete"
        })
        
        print(f"✅ Decision completed: {len(decision_result)} characters generated")
        
    except Exception as e:
        print(f"❌ Error in decision node: {e}")
        state.update({
            "decision": f"Error during decision making: {str(e)}",
            "step": "decision_error"
        })
    
    return state

def orchestrator_node(state: WorkflowState) -> WorkflowState:
    """Execute the orchestrator agent to decide next steps."""
    print("\n🎼 ORCHESTRATOR NODE - Deciding next workflow step...")
    
    try:
        # Create orchestrator agent dynamically to avoid circular imports
        from agents.orchestrator import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        
        # Prepare state for orchestrator
        orchestrator_state = {
            "intent": state.get("intent", ""),
            "entities": state.get("entities", []),
            "analysis": state.get("analysis", ""),
            "decision": state.get("decision", "")
        }
        
        # Get next step from orchestrator
        next_step = orchestrator.process(orchestrator_state, _reasoner_llm)
        
        # Update state with orchestrator decision
        state.update({
            "step": f"orchestrator_decided_{next_step}"
        })
        
        print(f"✅ Orchestrator decided: {next_step}")
        
    except Exception as e:
        print(f"❌ Error in orchestrator node: {e}")
        state.update({
            "step": "orchestrator_error"
        })
    
    return state

def route_to_next_step(state: WorkflowState) -> str:
    """Route to the next step based on orchestrator decision."""
    current_step = state.get("step", "")
    
    # Extract the decision from the step
    if "orchestrator_decided_" in current_step:
        decision = current_step.replace("orchestrator_decided_", "")
        return decision
    
    # Fallback routing logic
    if not state.get("analysis"):
        return "analysis"
    elif not state.get("decision"):
        return "decision"
    else:
        return "done"
