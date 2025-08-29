"""
Analysis Agent - Analyzes skill gaps and recommends solutions
"""

from typing import Dict, List, Any
from langchain.prompts import ChatPromptTemplate
from .router import get_router
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
import json

# Get memory logger
_, memory_logger = get_memory_system()

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Analysis Agent for GapLens Skills Analysis System.

CRITICAL: You must return ONLY a valid JSON object. NO additional text, explanations, or verbose output.

## Output Format:
Return ONLY this exact JSON structure with NO additional text:

{{
  "skill_gaps": ["<skill1>", "<skill2>"],
  "upskilling": [
    {{
      "employee": "<Full Name>",
      "skill_to_learn": "<skill name>",
      "timeline_weeks": <number>,
      "confidence": "high|medium|low",
      "reason": "<brief reason>"
    }}
  ],
  "internal_transfers": [
    {{
      "employee": "<Full Name>",
      "current_team": "<team name>",
      "skills_brought": ["<skill1>", "<skill2>"],
      "availability": "immediate|2_weeks|1_month",
      "reason": "<brief reason>"
    }}
  ],
  "hiring": [
    {{
      "role": "<job title>",
      "required_skills": ["<skill1>", "<skill2>"],
      "urgency": "critical|high|medium",
      "estimated_cost": "<salary range>"
    }}
  ],
  "timeline_assessment": "<brief timeline analysis>",
  "risk_factors": ["<risk1>", "<risk2>"],
  "success_probability": "high|medium|low"
}}

## STRICT RULES:
- Return ONLY the JSON object above
- NO explanations, NO verbose text, NO additional information
- Use full employee names from the data
- Keep all text fields brief and focused
- If no data available for a section, use empty arrays []
- Validate JSON before returning
"""),
    ("human", "Question: {question}\n\nContext Data:\n{context}")
])

router = get_router()

def get_information_for_project(project_id: str, session_memory: SessionMemory = None) -> tuple:
    """Get information for a specific project from the router."""
    # Get project-specific skill gap analysis
    project_analysis = router.get_project_skill_gaps_sync(project_id)
    
    # Get employee skills (filtered to relevant employees)
    employee_skills = router.get_employee_skills_sync()
    
    # Get team composition
    team_composition = router.get_team_composition_sync()
    
    # Get skill market data
    skill_market_data = router.get_skill_market_data_sync()
    
    return project_analysis, employee_skills, team_composition, skill_market_data

def get_information(question: str, llm, session_memory: SessionMemory = None) -> tuple:
    """Get information from the router."""
    return (
        router.get_employee_skills_sync(),
        router.get_project_requirements_sync(),
        router.get_team_composition_sync(),
        router.get_skill_market_data_sync()
    )

def analyze_facts(normalized_question: str, llm, session_memory: SessionMemory = None, project_id: str = None, scope: str = "company") -> str:
    """Fetches facts from the router, analyzes them, and provides skill gap recommendations."""

    # Handle invalid input
    if not normalized_question or not normalized_question.strip():
        error_msg = "Error: No question provided for analysis"
        print(f"❌ {error_msg}")
        
        # Log error to memory if available
        if session_memory:
            session_memory.add_entry(
                agent="analysis",
                content=error_msg,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error: No question provided for analysis"],
                confidence=0.1,
                metadata={"error": "No question provided", "question": normalized_question}
            )
        
        return error_msg

    print(f"\n🧠 ANALYSIS AGENT - Processing: {normalized_question}")
    print("=" * 60)
    print("🧠 Using reasoning pattern: REACT")

    try:
        # Step 1: Get facts from router - use project-specific data if available
        if project_id:
            print(f"🔍 Using project-specific analysis for project ID: {project_id}")
            employee_skills, project_requirements, team_composition, skill_market_data = get_information_for_project(
                project_id, session_memory
            )
        else:
            print("🔍 Using general analysis (all projects)")
            employee_skills, project_requirements, team_composition, skill_market_data = get_information(
                normalized_question, llm, session_memory
            )

        # Step 2: Format data into context for the LLM
        context = f"""
        ### Employee Skills
        {json.dumps(employee_skills, indent=2)}

        ### Project Requirements
        {json.dumps(project_requirements, indent=2)}

        ### Team Composition
        {json.dumps(team_composition, indent=2)}

        ### Skill Market Data
        {json.dumps(skill_market_data, indent=2)}
        """

        print(context)
        print('--------------------------------')
        print('normalized_question', normalized_question)
        print('--------------------------------')
        
        # Update the question to be more specific about project focus
        if project_id:
            normalized_question = f'Analyze ONLY the skill gaps for the specific project (ID: {project_id}) and provide recommendations for the best way to fill the skill gaps. Focus on this project only, not all projects.'
        else:
            normalized_question = 'Consider all the employees and their skills and the project requirements and the team composition and the skill market data and provide a recommendation for the best way to fill the skill gaps.'

        # Step 3: Format messages using the prompt
        messages = ANALYSIS_PROMPT.format_messages(
            question=normalized_question,
            context=context
        )

        print("🤖 Sending analysis request to LLM...")

        # Step 4: Call LLM
        response = llm.invoke(messages)
        analysis = getattr(response, "content", str(response)).strip()
        reasoning_steps = getattr(response, "reasoning_steps", [])

        print(f"📥 LLM Analysis Response: {analysis[:200]}{'...' if len(analysis) > 200 else ''}")

        if reasoning_steps:
            print("🧠 LLM Reasoning Steps:")
            for i, step in enumerate(reasoning_steps, 1):
                print(f"   {i}. {step}")
        
        # Step 5: Log to memory if available
        if session_memory:
            if not reasoning_steps:
                reasoning_steps = [
                    "Reason: Understanding the question and the data provided",
                    "Evaluate: Assessing skill gaps and team capabilities",
                    "Act: Generating recommendations based on analysis. Make sure to return a valid and compact JSON object and say the person names you used in the recommendations using the following strict structure: {{'upskilling': ['<short actionable recommendation>', '...'], 'internal_transfers': ['<short actionable recommendation>', '...'], 'hiring': ['<short actionable recommendation>', '...'], 'rationale': '<short paragraph justifying the above choices, focusing on trade-offs and logic>}}",
                    "Check: Validating recommendations against constraints",
                    "Think: Refining the final analysis"
                ]

            session_memory.add_entry(
                agent="analysis",
                content=analysis,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=reasoning_steps,
                metadata={
                    "question": normalized_question,
                    "context": context,
                    "project_id": project_id,
                    "scope": scope
                }
            )
            session_memory.update_session_data("analysis", analysis)

            # Log reasoning pattern usage
            memory_logger.log_agent_reasoning("analysis", ReasoningPattern.REACT, reasoning_steps)

        print("✅ Analysis completed and logged to memory")
        print("=" * 60)

        return analysis

    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Log error to memory if available
        if session_memory:
            session_memory.add_entry(
                agent="analysis",
                content=error_msg,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error occurred during analysis phase"],
                confidence=0.1,
                metadata={"error": str(e), "question": normalized_question, "project_id": project_id, "scope": scope}
            )
        
        return error_msg

def analyze_project_facts(project_id: str, llm, session_memory: SessionMemory = None) -> str:
    """Analyze facts for a specific project and provide skill gap recommendations."""
    
    print(f"\n🧠 ANALYSIS AGENT - Processing Project ID: {project_id}")
    print("=" * 60)
    print("🧠 Using reasoning pattern: REACT")

    try:
        # Step 1: Get project-specific information
        project_analysis, employee_skills, team_composition, skill_market_data = get_information_for_project(
            project_id, session_memory
        )
        
        if "error" in project_analysis:
            return f"Error: {project_analysis['error']}"

        # Step 2: Format data into context for the LLM
        context = f"""
        ### Project Analysis
        {json.dumps(project_analysis, indent=2)}

        ### Employee Skills
        {json.dumps(employee_skills, indent=2)}

        ### Team Composition
        {json.dumps(team_composition, indent=2)}

        ### Skill Market Data
        {json.dumps(skill_market_data, indent=2)}
        """

        # Step 3: Create focused analysis question
        analysis_question = f"""Analyze ONLY the skill gaps for this specific project and provide structured recommendations.

Project: {project_analysis.get('project', {}).get('name', 'Unknown')}
Required Skills: {', '.join(project_analysis.get('required_skills', []))}
Missing Skills: {', '.join(project_analysis.get('missing_skills', []))}
Covered Skills: {', '.join(project_analysis.get('covered_skills', []))}

Return ONLY a JSON object with upskilling, transfer, and hiring recommendations for this specific project. Focus on actionable solutions with timelines and success probabilities."""

        # Step 4: Format messages using the prompt
        messages = ANALYSIS_PROMPT.format_messages(
            question=analysis_question,
            context=context
        )

        # Step 5: Call LLM
        response = llm.invoke(messages)
        analysis = getattr(response, "content", str(response)).strip()

        # Step 6: Log to memory if available
        if session_memory:
            session_memory.add_entry(
                agent="analysis",
                content=analysis,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Project-specific analysis completed"],
                metadata={
                    "project_id": project_id,
                    "question": analysis_question,
                    "context": context
                }
            )
            session_memory.update_session_data("analysis", analysis)

        return analysis

    except Exception as e:
        error_msg = f"Error during project analysis: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

