"""
GapLens Agents Package

This package contains specialized agents for skills gap analysis:
- Perception Agent: Understands user input and extracts intent
- Analysis Agent: Analyzes skill gaps and recommends solutions
- Decision Agent: Makes final actionable recommendations
- Orchestrator Agent: Coordinates the workflow between agents
- Router Agent: Accesses external data sources
"""

from .base_agent import BaseAgent
from .perception import perceive_input
from .analysis import analyze_facts
from .decision import DecisionAgent, make_decision
from .orchestrator import OrchestratorAgent, decide_next_step
from .router import DataRouter, get_router

__all__ = [
    # Base classes
    "BaseAgent",
    
    # Agent functions
    "perceive_input",
    "analyze_facts",
    "make_decision",
    "decide_next_step",
    
    # Agent classes
    "DecisionAgent",
    "OrchestratorAgent",
    "DataRouter",
    
    # Utilities
    "get_router"
]

# Version information
__version__ = "1.0.0"
