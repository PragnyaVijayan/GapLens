"""
Perception Agent - Perceives and understands user input and context
"""

from typing import List, Dict, Any
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system

# Get memory logger
_, memory_logger = get_memory_system()

PERCEPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Perception Agent for GapLens Skills Analysis System.

Your task is to perceive and understand:
1. User intent and goals
2. Key entities and skills mentioned
3. Context and constraints
4. Implicit requirements

Analyze the input and provide:
- Normalized question/request
- Extracted entities (skills, roles, projects)
- Identified intent
- Context understanding

Format as a clear, structured perception."""),
    ("human", "User Input: {user_input}")
])

def perceive_input(user_input: str, llm, session_memory: SessionMemory = None) -> Dict[str, Any]:
    """Perceive and understand user input to extract intent and entities."""
    
    print(f"\n👁️ PERCEPTION AGENT - Processing: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
    print("=" * 60)
    
    # This agent uses REACT reasoning
    print("🧠 Using reasoning pattern: REACT")
    
    print("🔍 Analyzing user input...")
    
    try:
        # Use LLM to analyze the input
        messages = PERCEPTION_PROMPT.format_messages(user_input=user_input)
        
        response = llm.invoke(messages)
        perception = getattr(response, "content", str(response)).strip()
        
        # Extract reasoning steps if available
        reasoning_steps = getattr(response, "reasoning_steps", [])
        
        print(f"📥 LLM Perception Response: {perception[:200]}{'...' if len(perception) > 200 else ''}")
        
        if reasoning_steps:
            print("🧠 LLM Reasoning Steps:")
            for i, step in enumerate(reasoning_steps, 1):
                print(f"   {i}. {step}")
        
        # Basic entity extraction (simplified)
        entities = []
        intent = "skill_analysis"
        
        # Simple keyword-based entity extraction
        skill_keywords = ["python", "java", "react", "aws", "docker", "kubernetes", "machine learning", "ai"]
        for skill in skill_keywords:
            if skill.lower() in user_input.lower():
                entities.append(skill)
        
        # Create perception result
        perception_result = {
            "normalized_question": user_input,
            "entities": entities,
            "intent": intent,
            "perception": perception,
            "confidence": 0.8
        }
        
        # Log to memory if available
        if session_memory:
            if not reasoning_steps:
                reasoning_steps = [
                    "Reason: Understanding user input and context",
                    "Evaluate: Identifying key entities and intent",
                    "Act: Extracting relevant information",
                    "Check: Validating extracted entities",
                    "Think: Refining perception understanding"
                ]
            
            session_memory.add_entry(
                agent="perception",
                content=perception_result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=reasoning_steps,
                confidence=0.8,
                metadata={
                    "user_input": user_input,
                    "entities_count": len(entities)
                }
            )
            
            # Update session data
            session_memory.update_session_data("intent", intent)
            session_memory.update_session_data("entities", entities)
            session_memory.update_session_data("normalized_question", user_input)
        
        # Log reasoning pattern usage
        memory_logger.log_agent_reasoning("perception", ReasoningPattern.REACT, reasoning_steps)
        
        print("✅ Perception completed")
        print("=" * 60)
        
        return perception_result
        
    except Exception as e:
        error_result = {
            "normalized_question": user_input,
            "entities": [],
            "intent": "unknown",
            "perception": f"Error during perception: {str(e)}",
            "confidence": 0.1
        }
        
        # Log error to memory if available
        if session_memory:
            session_memory.add_entry(
                agent="perception",
                content=error_result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error occurred during perception phase"],
                confidence=0.1,
                metadata={"error": str(e), "user_input": user_input}
            )
        
        print(f"❌ Error during perception: {str(e)}")
        return error_result
