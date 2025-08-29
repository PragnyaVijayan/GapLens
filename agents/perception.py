"""
Perception Agent - Perceives and understands user input and context
"""

from typing import List, Dict, Any
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
import json

# Get memory logger
_, memory_logger = get_memory_system()

PERCEPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Perception Agent for GapLens Skills Analysis System.

CRITICAL: You must return ONLY a valid JSON object. NO additional text, explanations, or verbose output.

## Output Format:
Return ONLY this exact JSON structure with NO additional text:

{{
  "intent": "skill_gap_analysis|team_optimization|upskilling_plan|project_readiness",
  "entities": {{
    "skills": ["<skill1>", "<skill2>"],
    "projects": ["<project1>"],
    "teams": ["<team1>"],
    "people": ["<person1>"],
    "timelines": ["<timeline1>"]
  }},
  "normalized_question": "<clear, specific question>",
  "context": {{
    "constraints": ["<constraint1>"],
    "urgency": "high|medium|low",
    "scope": "department|team|company|project"
  }},
  "analysis_focus": "<specific aspect to analyze>"
}}

## STRICT RULES:
- Return ONLY the JSON object above
- NO explanations, NO verbose text, NO additional information
- Extract only explicitly mentioned information
- Keep all text fields brief and focused
- If no data available for a section, use empty arrays []
- Validate JSON before returning
"""),
    ("human", "{user_input}")
])

def perceive_input(user_input: str, llm, session_memory: SessionMemory = None) -> Dict[str, Any]:
    """Interpret user input to extract structured intent, entities, and context."""

    # Handle invalid input
    if not user_input:
        error_result = {
            "intent": "unknown",
            "entities": [],
            "normalized_question": "No input provided",
            "context": "Error: No user input provided"
        }
        
        if session_memory:
            session_memory.add_entry(
                agent="perception",
                content=error_result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error: No user input provided"],
                confidence=0.1,
                metadata={"error": "No user input", "user_input": str(user_input)}
            )
            session_memory.update_session_data("intent", "unknown")
            session_memory.update_session_data("entities", [])
            session_memory.update_session_data("normalized_question", "No input provided")
            session_memory.update_session_data("research_facts", [])
        
        return error_result

    print(f"\n👁️ PERCEPTION AGENT - Processing: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
    print("=" * 60)
    print("🧠 Using reasoning pattern: REACT")
    
    try:
        # Format perception prompt
        messages = PERCEPTION_PROMPT.format_messages(user_input=user_input)
        response = llm.invoke(messages)
        content = getattr(response, "content", str(response)).strip()

        print(f"📥 LLM Perception Response: {content[:200]}{'...' if len(content) > 200 else ''}")

        # Attempt to parse the JSON response
        perception = json.loads(content)

        # Validation and fallback
        entities = perception.get("entities", [])
        intent = perception.get("intent", "unknown")
        normalized_question = perception.get("normalized_question", user_input)
        context = perception.get("context", "")

        result = {
            "intent": intent,
            "entities": entities,
            "normalized_question": normalized_question,
            "context": context
        }

        # Log to memory if available
        if session_memory:
            reasoning_steps = [
                "Interpreted user request using structured prompt.",
                "Extracted intent and entities using LLM.",
                "Validated response and normalized user query."
            ]
            
            session_memory.add_entry(
                agent="perception",
                content=result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=reasoning_steps,
                metadata={"user_input": user_input}
            )
            
            # Update session data
            session_memory.update_session_data("intent", intent)
            session_memory.update_session_data("entities", entities)
            session_memory.update_session_data("normalized_question", normalized_question)
            session_memory.update_session_data("research_facts", [])

        # Log reasoning pattern usage
        memory_logger.log_agent_reasoning("perception", ReasoningPattern.REACT, reasoning_steps)
        print("✅ Perception completed")
        print("=" * 60)
        return result

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error during perception: {str(e)}")
        error_result = {
            "intent": "unknown",
            "entities": [],
            "normalized_question": user_input,
            "context": "Error: Invalid JSON response from LLM"
        }

        if session_memory:
            session_memory.add_entry(
                agent="perception",
                content=error_result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["JSON parsing error occurred during perception phase"],
                confidence=0.1,
                metadata={"error": str(e), "user_input": user_input}
            )
            session_memory.update_session_data("intent", "unknown")
            session_memory.update_session_data("entities", [])
            session_memory.update_session_data("normalized_question", user_input)
            session_memory.update_session_data("research_facts", [])

        return error_result

    except Exception as e:
        print(f"❌ Error during perception: {str(e)}")
        error_result = {
            "intent": "unknown",
            "entities": [],
            "normalized_question": user_input,
            "context": f"Error during perception: {str(e)}"
        }

        if session_memory:
            session_memory.add_entry(
                agent="perception",
                content=error_result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error occurred during perception phase"],
                confidence=0.1,
                metadata={"error": str(e), "user_input": user_input}
            )
            session_memory.update_session_data("intent", "unknown")
            session_memory.update_session_data("entities", [])
            session_memory.update_session_data("normalized_question", user_input)
            session_memory.update_session_data("research_facts", [])

        return error_result
