"""
LangGraph Workflow Implementation for GapLens Multi-Agent System
"""

from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from core.memory_system import SessionMemory, ReasoningPattern
import json
# Import functions will be done inside functions to avoid circular imports

# Global LLM instances for the workflow
_perception_llm = None
_research_llm = None
_analysis_llm = None
_decision_llm = None
_orchestrator_llm = None
def set_llms(perception_llm, research_llm, analysis_llm, decision_llm, orchestrator_llm):
    """Set the LLM instances for the workflow."""
    global _perception_llm, _research_llm, _analysis_llm, _decision_llm, _orchestrator_llm
    _perception_llm = perception_llm
    _research_llm = research_llm
    _analysis_llm = analysis_llm
    _decision_llm = decision_llm
    _orchestrator_llm = orchestrator_llm

class WorkflowState(TypedDict):
    """State for the workflow execution."""
    question: str
    memory: SessionMemory
    intent: str
    entities: List[str]
    normalized_question: str
    research_facts: List[str]
    analysis: str
    decision: str
    step: str
    project_id: str
    scope: str

def create_workflow(perception_llm, research_llm, analysis_llm, decision_llm, orchestrator_llm, display_limit: int = None):
    """Create the LangGraph workflow for the multi-agent system."""
    
    # Set LLMs globally
    set_llms(perception_llm, research_llm, analysis_llm, decision_llm, orchestrator_llm)
    
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
        # Import here to avoid circular imports
        from agents.perception import perceive_input
        
        # Get the question from state
        question = state["question"]
        
        # Create session memory if not exists
        if not state.get("memory"):
            state["memory"] = SessionMemory()
        
        # Execute perception
        perception_result = perceive_input(question, _perception_llm, state["memory"])
        
        # Update state with perception results
        entities = perception_result.get("entities", {})
        # Convert entities dict to list if needed for compatibility
        if isinstance(entities, dict):
            entities_list = []
            for key, value in entities.items():
                if isinstance(value, list):
                    entities_list.extend(value)
                else:
                    entities_list.append(value)
        else:
            entities_list = entities if isinstance(entities, list) else []
            
        state.update({
            "intent": perception_result.get("intent", "skill_analysis"),
            "entities": entities_list,
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
        # Import here to avoid circular imports
        from agents.analysis import analyze_facts
        
        # Get required data from state
        question = state.get("normalized_question", state["question"])
        project_id = state.get("project_id", None)
        scope = state.get("scope", "company")
        
        # Execute analysis using the cleaned analyze_facts function with project-specific parameters
        analysis_result = analyze_facts(question, _analysis_llm, state["memory"], project_id, scope)
        
        # Parse analysis result to count strategies
        try:
            import json
            parsed_analysis = json.loads(analysis_result)
            if isinstance(parsed_analysis, list):
                strategy_count = len(parsed_analysis)
                print(f"📊 Analysis generated {strategy_count} recommendation strategies")
            else:
                print("📊 Analysis generated single recommendation strategy")
        except json.JSONDecodeError:
            print("📊 Analysis result is not in JSON format")
        
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
        error_json = [
            {
                "strategy_name": "Error Recovery Strategy",
                "strategy_type": "mixed",
                "skill_gaps": [],
                "upskilling": [],
                "internal_transfers": [],
                "hiring": [],
                "timeline_assessment": f"Analysis failed: {str(e)}",
                "risk_factors": ["Analysis error occurred"],
                "success_probability": "low",
                "estimated_cost": "Unknown",
                "pros": ["Error recovery approach"],
                "cons": ["Analysis failed", "Limited data available"]
            }
        ]
        state.update({
            "analysis": json.dumps(error_json),
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
        decision_result = decision_agent.process(question, analysis, _decision_llm, state["memory"])
        
        # Update state with decision results
        state.update({
            "decision": decision_result,
            "step": "decision_complete"
        })
        
        print(f"✅ Decision completed: {len(decision_result)} characters generated")
        
    except Exception as e:
        print(f"❌ Error in decision node: {e}")
        error_json = {
            "website_message": f"Decision making failed: {str(e)}. Please try again or contact support.",
            "selected_strategy": {
                "strategy_name": "Error Recovery",
                "approach": "unknown",
                "selection_reason": f"Decision process failed: {str(e)}",
                "confidence_score": 0
            },
            "strategy_details": {
                "primary_action": "Resolve technical error and retry analysis",
                "target_skill": "Error resolution",
                "timeline_weeks": 0,
                "success_probability": "low",
                "cost_estimate": "low",
                "risk_level": "high"
            },
            "implementation_plan": {
                "primary_owner": "System Administrator",
                "support_team": ["Technical Support"],
                "key_milestones": ["Resolve error", "Retry analysis"],
                "success_metrics": ["Error resolved", "Analysis completed"],
                "budget_estimate": "No additional cost",
                "resource_requirements": ["Technical support"]
            },
            "risk_mitigation": {
                "primary_risks": ["Analysis failure", "Decision delay"],
                "mitigation_strategies": ["Retry with different parameters", "Contact technical support"],
                "contingency_plan": "Manual analysis and decision making",
                "monitoring_points": ["Error resolution", "System stability"]
            },
            "review_schedule": {
                "next_review_date": "Immediate",
                "review_frequency": "As needed",
                "success_criteria": ["Error resolved", "Analysis successful"]
            }
        }
        state.update({
            "decision": json.dumps(error_json),
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
        next_step = orchestrator.process(orchestrator_state, _orchestrator_llm)
        
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
