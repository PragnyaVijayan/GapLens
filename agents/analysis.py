"""
Analysis Agent - Analyzes skill gaps and recommends solutions
"""

from typing import Dict, List, Any
from langchain.prompts import ChatPromptTemplate
from agents.router import get_router
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
import json
# Get memory logger
_, memory_logger = get_memory_system()

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Analysis Agent for GapLens Skills Analysis System.

Your task is to analyze the research data and provide intelligent recommendations for:
1. Upskilling opportunities (highest priority)
2. Internal transfers (medium priority) 
3. New hiring needs (last resort)

Consider:
- Time available before project starts
- Team member learning capacity
- Skill transferability
- Risk levels
- Cost implications

Provide a structured analysis with clear recommendations and rationale."""),
    ("human", "Project Context: {question}\nResearch Facts: {research_facts}")
])

def analyze_facts(question: str, research_facts: List[str], llm, session_memory: SessionMemory = None) -> str:
    """Analyze research facts and provide skill gap recommendations."""
    
    print(f"\n🧠 ANALYSIS AGENT - Processing: {question}")
    print("=" * 60)
    
    # This agent uses REACT reasoning
    print("🧠 Using reasoning pattern: REACT")
    
    print(f"📊 Analyzing {len(research_facts)} research facts...")
    
    # Get additional data from router for comprehensive analysis
    router = get_router()
    
    # Get market data for skills
    print("💰 Fetching skill market data...")
    try:
        market_data = router.get_skill_market_data_sync()
        skill_costs = market_data.get("skill_costs", {}) if "error" not in market_data else {}
        if skill_costs:
            print(f"✅ Market data available for {len(skill_costs)} skills")
        else:
            print("⚠️  No market data available")
    except:
        skill_costs = {}
        print("❌ Error fetching market data")
    
    # Prepare context for LLM analysis
    context = f"""
Project Context: {question}

Research Facts:
{chr(10).join(research_facts)}

Additional Market Data:
{json.dumps(skill_costs, indent=2)}
"""
    
    print("🤖 Sending analysis request to LLM...")
    
    # Use LLM to analyze the data
    messages = ANALYSIS_PROMPT.format_messages(
        question=question,
        research_facts=context
    )
    
    response = llm.invoke(messages)
    analysis = getattr(response, "content", str(response)).strip()
    
    # Extract reasoning steps if available
    reasoning_steps = getattr(response, "reasoning_steps", [])
    
    print(f"📥 LLM Analysis Response: {analysis[:200]}{'...' if len(analysis) > 200 else ''}")
    
    if reasoning_steps:
        print("🧠 LLM Reasoning Steps:")
        for i, step in enumerate(reasoning_steps, 1):
            print(f"   {i}. {step}")
    
    # Log to memory if available
    if session_memory:
        if not reasoning_steps:
            reasoning_steps = [
                "Reason: Understanding the project context and research data",
                "Evaluate: Assessing skill gaps and team capabilities",
                "Act: Generating recommendations based on analysis",
                "Check: Validating recommendations against constraints",
                "Think: Refining the final analysis"
            ]
        
        session_memory.add_entry(
            agent="analysis",
            content=analysis,
            reasoning_pattern=ReasoningPattern.REACT,
            reasoning_steps=reasoning_steps,
            confidence=0.8,
            metadata={
                "question": question,
                "research_facts_count": len(research_facts),
                "market_data_available": bool(skill_costs)
            }
        )
        
        # Update session data
        session_memory.update_session_data("analysis", analysis)
    
    # Log reasoning pattern usage
    memory_logger.log_agent_reasoning("analysis", ReasoningPattern.REACT, reasoning_steps)
    
    print("✅ Analysis completed and logged to memory")
    print("=" * 60)
    
    return analysis
