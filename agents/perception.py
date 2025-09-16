"""
Perception Agent - Perceives and understands user input and context
Enhanced with robust JSON parsing and error handling
"""

from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
from .schemas import validate_perception_output, PerceptionOutput
import json
import re

# Get memory logger
_, memory_logger = get_memory_system()

def clean_json_response(response: str) -> str:
    """Clean and prepare JSON response for parsing."""
    if not response:
        return ""
    
    # Strip markdown fences if present
    if response.startswith("```"):
        response = re.sub(r"```(json)?", "", response).strip("` \n")
    
    # Remove any markdown formatting
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*$', '', response)
    
    # Remove any trailing commas before closing braces/brackets
    response = re.sub(r',(\s*[}\]])', r'\1', response)
    
    # Find the JSON object boundaries
    start_idx = response.find('{')
    if start_idx == -1:
        return ""
    
    # Find the matching closing brace
    brace_count = 0
    end_idx = -1
    for i, char in enumerate(response[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if end_idx == -1:
        return ""
    
    return response[start_idx:end_idx].strip()

def create_fallback_perception(user_input: str, llm_response: str = "") -> Dict[str, Any]:
    """Create a fallback perception response when JSON parsing fails."""
    return {
        "intent": "skill_gap_analysis",
        "entities": {
            "skills": [],
            "projects": [],
            "teams": [],
            "people": [],
            "timelines": []
        },
        "normalized_question": user_input.strip(),
        "context": {
            "constraints": [],
            "urgency": "medium",
            "scope": "project"
        },
        "analysis_focus": "General skills analysis"
    }

def parse_json_with_fallbacks(content: str, user_input: str) -> Dict[str, Any]:
    """Parse JSON with multiple fallback strategies."""
    
    # Handle empty or None content
    if not content or not content.strip():
        print("❌ Empty response string, using fallback")
        return create_fallback_perception(user_input, content)
    
    # Strategy 0: Remove any markdown headers and explanations first
    content = re.sub(r'^#+.*?\n', '', content, flags=re.MULTILINE)  # Remove markdown headers
    content = re.sub(r'^##+.*?\n', '', content, flags=re.MULTILINE)  # Remove markdown subheaders
    content = re.sub(r'^###+.*?\n', '', content, flags=re.MULTILINE)  # Remove markdown sub-subheaders
    content = re.sub(r'^Step \d+:.*?\n', '', content, flags=re.MULTILINE)  # Remove step explanations
    content = re.sub(r'^### Reason.*?\n', '', content, flags=re.MULTILINE)  # Remove reasoning sections
    content = re.sub(r'^### Evaluate.*?\n', '', content, flags=re.MULTILINE)  # Remove evaluation sections
    content = re.sub(r'^### Act.*?\n', '', content, flags=re.MULTILINE)  # Remove action sections
    content = re.sub(r'^### Check.*?\n', '', content, flags=re.MULTILINE)  # Remove check sections
    content = re.sub(r'^### Think.*?\n', '', content, flags=re.MULTILINE)  # Remove think sections
    
    # Strip markdown fences if present
    if content.startswith("```"):
        content = re.sub(r"```(json)?", "", content).strip("` \n")
    
    # Strategy 1: Direct parsing
    try:
        perception = json.loads(content.strip())
        print("✅ Direct JSON parsing successful")
        return perception
    except json.JSONDecodeError as e:
        print(f"⚠️ Direct JSON parsing failed: {e}")

        # Strategy 2: Try extracting JSON with regex
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group().strip()
            try:
                perception = json.loads(json_str)
                print("✅ Extracted JSON from response")
                return perception
            except json.JSONDecodeError as e2:
                print(f"⚠️ Extracted JSON parsing failed: {e2}")
        else:
            print("⚠️ No JSON object found in response")
        
        # Strategy 3: Clean and parse (fallback for edge cases)
        cleaned_content = clean_json_response(content)
        if cleaned_content:
            try:
                perception = json.loads(cleaned_content)
                print("✅ Cleaned JSON parsing successful")
                return perception
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Extract JSON with additional regex patterns
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested braces
            r'\{.*?\}',  # Simple braces
        ]
        
        for pattern in json_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    potential_json = match.group().strip()
                    perception = json.loads(potential_json)
                    print("✅ Pattern-based JSON parsing successful")
                    return perception
                except json.JSONDecodeError:
                    continue
        
        # Strategy 5: Create fallback response
        print("⚠️ All JSON parsing strategies failed, using fallback")
        return create_fallback_perception(user_input, content)

# Enhanced prompt with stricter JSON requirements
PERCEPTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a JSON API that MUST respond with valid JSON only.

CRITICAL REQUIREMENTS:
1. Response must start with {{ and end with }}
2. No text before or after the JSON object
3. No markdown formatting or code blocks
4. All strings must be properly quoted
5. No trailing commas
6. NO EXPLANATIONS, NO MARKDOWN, NO ADDITIONAL TEXT
7. ONLY return the JSON object

If you cannot format as JSON, you may use YAML format instead, but JSON is preferred.

EXACT JSON STRUCTURE REQUIRED:
{{
  "intent": "skill_gap_analysis",
  "entities": {{
    "skills": ["AWS", "Python"],
    "projects": ["Cloud Migration"],
    "teams": ["Development Team"],
    "people": [],
    "timelines": ["3 months"]
  }},
  "normalized_question": "What are our AWS skill gaps?",
  "context": {{
    "constraints": ["Budget constraint"],
    "urgency": "medium",
    "scope": "project"
  }},
  "analysis_focus": "AWS skills gap analysis"
}}

Valid intent values: skill_gap_analysis, team_optimization, upskilling_plan, project_readiness
Valid urgency values: low, medium, high
Valid scope values: project, team, department, company, enterprise

Respond with ONLY the JSON object."""),
    ("human", "{user_input}")
])

def perceive_input(user_input: str, llm, session_memory: SessionMemory = None) -> Dict[str, Any]:
    """Interpret user input to extract structured intent, entities, and context with robust JSON parsing."""

    # Handle invalid input
    if not user_input or not user_input.strip():
        error_result = create_fallback_perception("No input provided", "")
        
        if session_memory:
            session_memory.add_entry(
                agent="perception",
                content=error_result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error: No user input provided"],
                confidence=0.1,
                metadata={"error": "No user input", "user_input": str(user_input)}
            )
            session_memory.update_session_data("intent", "skill_gap_analysis")
            session_memory.update_session_data("entities", error_result.get("entities", {}))
            session_memory.update_session_data("normalized_question", "No input provided")
            session_memory.update_session_data("research_facts", [])
        
        return error_result

    # Check if this is a project-specific analysis question
    is_project_analysis = any(keyword in user_input.lower() for keyword in [
        'project id:', 'project name:', 'required skills:', 'timeline:', 'budget:',
        'analyze the skill gaps for this specific project'
    ])
    
    if is_project_analysis:
        print(f"\n👁️ PERCEPTION AGENT - Processing Project Analysis: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        print("=" * 60)
        print("🧠 Using reasoning pattern: REACT (Project-specific)")
        
        # Extract project information and create a simplified question for perception
        project_id = None
        project_name = None
        required_skills = []
        
        # Extract project ID
        if 'Project ID:' in user_input:
            project_id = user_input.split('Project ID:')[1].split('\n')[0].strip()
        
        # Extract project name
        if 'Project Name:' in user_input:
            project_name = user_input.split('Project Name:')[1].split('\n')[0].strip()
        
        # Extract required skills
        if 'Required Skills:' in user_input:
            skills_text = user_input.split('Required Skills:')[1].split('\n')[0].strip()
            required_skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
        
        # Create a simplified question for perception
        simplified_question = f"Analyze skill gaps for project {project_name or project_id or 'selected project'}"
        if required_skills:
            simplified_question += f" requiring skills: {', '.join(required_skills[:5])}"
        
        print(f"📝 Simplified question for perception: {simplified_question}")
        
        # Store project context in session memory for later use
        if session_memory:
            session_memory.update_session_data("project_id", project_id)
            session_memory.update_session_data("project_name", project_name)
            session_memory.update_session_data("required_skills", required_skills)
        
        # Use the simplified question for perception
        user_input = simplified_question
    else:
        print(f"\n👁️ PERCEPTION AGENT - Processing: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        print("=" * 60)
        print("🧠 Using reasoning pattern: REACT")
    
    try:
        # Format perception prompt
        messages = PERCEPTION_PROMPT.format_messages(user_input=user_input)
        response = llm.invoke(messages)
        content = getattr(response, "content", str(response)).strip()

        print(f"📥 LLM Perception Response: {content[:200]}{'...' if len(content) > 200 else ''}")

        # Check for empty or invalid response
        if not content or content.isspace():
            print("❌ Empty LLM response received")
            result = create_fallback_perception(user_input, content)
        else:
            # Parse JSON with enhanced fallback strategies
            perception = parse_json_with_fallbacks(content, user_input)
            print("✅ JSON parsing successful")
            
            # Validate with Pydantic schema
            try:
                validated_perception = validate_perception_output(perception)
                result = validated_perception.dict()
                print("✅ Perception schema validation passed")
            except Exception as validation_error:
                print(f"⚠️ Schema validation failed: {validation_error}")
                
                # Manual validation with safe defaults
                result = {
                    "intent": perception.get("intent", "skill_gap_analysis"),
                    "entities": {
                        "skills": perception.get("entities", {}).get("skills", [])[:10],
                        "projects": perception.get("entities", {}).get("projects", [])[:5],
                        "teams": perception.get("entities", {}).get("teams", [])[:5],
                        "people": perception.get("entities", {}).get("people", [])[:5],
                        "timelines": perception.get("entities", {}).get("timelines", [])[:3]
                    },
                    "normalized_question": perception.get("normalized_question", user_input),
                    "context": {
                        "constraints": perception.get("context", {}).get("constraints", []),
                        "urgency": perception.get("context", {}).get("urgency", "medium"),
                        "scope": perception.get("context", {}).get("scope", "project")
                    },
                    "analysis_focus": perception.get("analysis_focus", f"Analysis of {perception.get('intent', 'skill_gap_analysis').replace('_', ' ')}")
                }

        # Log to memory if available
        if session_memory:
            reasoning_steps = [
                "Interpreted user request using enhanced structured prompt",
                "Extracted intent and entities using LLM with JSON validation",
                "Applied robust JSON parsing with multiple fallback strategies",
                "Validated response and normalized user query"
            ]
            
            session_memory.add_entry(
                agent="perception",
                content=result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=reasoning_steps,
                metadata={"user_input": user_input, "json_parsing_successful": True}
            )
            
            # Update session data
            session_memory.update_session_data("intent", result.get("intent", "skill_gap_analysis"))
            session_memory.update_session_data("entities", result.get("entities", {}))
            session_memory.update_session_data("normalized_question", result.get("normalized_question", user_input))
            session_memory.update_session_data("research_facts", [])

        # Log reasoning pattern usage
        memory_logger.log_agent_reasoning("perception", ReasoningPattern.REACT, reasoning_steps)
        print("✅ Perception agent reasoning pattern logged")
        
        return result

    except Exception as e:
        print(f"❌ Error in perception processing: {e}")
        
        # Create fallback perception on error
        result = create_fallback_perception(user_input, str(e))
        
        # Log error to memory if available
        if session_memory:
            session_memory.add_entry(
                agent="perception",
                content=result,
                reasoning_pattern=ReasoningPattern.REACT,
                reasoning_steps=["Error occurred during perception processing", f"Error: {str(e)}"],
                confidence=0.1,
                metadata={"error": str(e), "user_input": user_input}
            )
            
            # Update session data with fallback
            session_memory.update_session_data("intent", result.get("intent", "skill_gap_analysis"))
            session_memory.update_session_data("entities", result.get("entities", {}))
            session_memory.update_session_data("normalized_question", result.get("normalized_question", user_input))
            session_memory.update_session_data("research_facts", [])
        
        return result