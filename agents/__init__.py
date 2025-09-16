"""
GapLens Agents Package

This package contains specialized agents for skills gap analysis:
- Perception Agent: Understands user input and extracts intent
- Analysis Agent: Analyzes skill gaps and recommends solutions
- Decision Agent: Makes final actionable recommendations
- Orchestrator Agent: Coordinates the workflow between agents

Note: Data access is handled by core/data_client.py (MCP pattern)
"""

# Import functions only to avoid circular imports
from .perception import perceive_input
from .analysis import analyze_facts
from .decision import make_decision
from .orchestrator import decide_next_step

__all__ = [
    # Agent functions
    "perceive_input",
    "analyze_facts", 
    "make_decision",
    "decide_next_step"
]

# Version information
__version__ = "1.0.0"
