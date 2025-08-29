"""
Agents Module - Specialized AI agents for skills analysis
"""

from typing import List

# Don't import agent classes directly to avoid circular imports
# They will be imported when needed

__all__ = [
    # Agent Classes
    'PerceptionAgent',
    'ResearchAgent', 
    'AnalysisAgent',
    'DecisionAgent',
    'OrchestratorAgent',
    'DataRouter',
    
    # Legacy Functions (for backward compatibility)
    'extract_intent_and_entities',
    'gather_research',
    'analyze_facts',
    'make_decision',
    'decide_next_step',
    'get_router'
]

# Lazy imports to avoid circular dependencies
def _get_perception_agent():
    from .perception import PerceptionAgent
    return PerceptionAgent

def _get_research_agent():
    from .research import ResearchAgent
    return ResearchAgent

def _get_analysis_agent():
    from .analysis import AnalysisAgent
    return AnalysisAgent

def _get_decision_agent():
    from .decision import DecisionAgent
    return DecisionAgent

def _get_orchestrator_agent():
    from .orchestrator import OrchestratorAgent
    return OrchestratorAgent

def _get_router():
    from .router import DataRouter
    return DataRouter

# Legacy function imports
def extract_intent_and_entities(question: str, llm, session_memory=None):
    """Extract intent and entities from user question using the perception agent."""
    from .perception import extract_intent_and_entities as _extract
    return _extract(question, llm, session_memory)

def gather_research(question: str, entities: List[str], llm, session_memory=None):
    """Gather research using the research agent."""
    from .research import gather_research as _gather
    return _gather(question, entities, llm, session_memory)

def analyze_facts(facts: str, llm, session_memory=None):
    """Analyze facts using the analysis agent."""
    from .analysis import analyze_facts as _analyze
    return _analyze(facts, llm, session_memory)

def make_decision(context: str, llm, session_memory=None):
    """Make decision using the decision agent."""
    from .decision import make_decision as _make
    return _make(context, llm, session_memory)

def decide_next_step(current_state: str, llm, session_memory=None):
    """Decide next step using the orchestrator agent."""
    from .orchestrator import decide_next_step as _decide
    return _decide(current_state, llm, session_memory)

def get_router():
    """Get router instance."""
    from .router import get_router as _get
    return _get()

# Class accessors
def get_perception_agent():
    return _get_perception_agent()()

def get_research_agent():
    return _get_research_agent()()

def get_analysis_agent():
    return _get_analysis_agent()()

def get_decision_agent():
    return _get_decision_agent()()

def get_orchestrator_agent():
    return _get_orchestrator_agent()()

def get_data_router():
    return _get_router()()

# Direct class access (for testing and direct usage)
def PerceptionAgent():
    return _get_perception_agent()()

def ResearchAgent():
    return _get_research_agent()()

def AnalysisAgent():
    return _get_analysis_agent()()

def DecisionAgent():
    return _get_decision_agent()()

def OrchestratorAgent():
    return _get_orchestrator_agent()()

def DataRouter():
    return _get_router()() 