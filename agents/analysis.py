"""
Analysis Agent - Analyzes skill gaps and recommends solutions
FIXED VERSION with improved error handling and simplified prompts
"""

from typing import Dict, List, Any
from langchain.prompts import ChatPromptTemplate
from core.data_client import get_data_client
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
from .schemas import validate_analysis_output, AnalysisOutput
from .base_agent import BaseAgent
import json

# Get memory logger
_, memory_logger = get_memory_system()

class AnalysisAgent(BaseAgent):
    """Analysis Agent with improved error handling and simplified prompts."""
    
    def __init__(self):
        # Simplified prompt for better LLM compliance
        self.ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
            ("system", """You are an expert skills analyst. Analyze the provided data and return ONLY a valid JSON object.

CRITICAL: Return ONLY the JSON object. No explanations, no markdown, no additional text.
If you cannot format as JSON, you may use YAML format instead, but JSON is preferred.

Return this exact JSON structure:
{{
  "skill_gaps": ["skill1", "skill2"],
  "upskilling": [
    {{
      "employee": "Full Name",
      "skill_to_learn": "skill name", 
      "timeline_weeks": 8,
      "confidence": "high",
      "reason": "brief reason"
    }}
  ],
  "internal_transfers": [
    {{
      "employee": "Full Name",
      "current_team": "team name",
      "skills_brought": ["skill1", "skill2"],
      "availability": "immediate",
      "reason": "brief reason"
    }}
  ],
  "hiring": [
    {{
      "role": "job title",
      "required_skills": ["skill1", "skill2"],
      "urgency": "high", 
      "estimated_cost": "salary range"
    }}
  ],
  "timeline_assessment": "brief timeline analysis",
  "risk_factors": ["risk1", "risk2"],
  "success_probability": "high"
}}

CRITICAL: Return ONLY the JSON object. No explanations, no markdown, no additional text."""),
            ("human", "Question: {question}\n\nData: {context}")
        ])
        
        super().__init__(
            name="Analysis",
            reasoning_pattern=ReasoningPattern.REACT,
            prompt_template=self.ANALYSIS_PROMPT
        )
        
        self.data_client = get_data_client()
    
    def process(self, question: str, llm, session_memory: SessionMemory = None, project_id: str = None, scope: str = "company") -> str:
        """Process analysis with improved error handling."""
        
        if not question or not question.strip():
            return self._get_error_response("No question provided for analysis")
        
        print(f"\n🧠 ANALYSIS AGENT - Processing: {question}")
        print("=" * 60)
        
        try:
            # Get data with fallback handling
            data = self._get_analysis_data(project_id, scope)
            print(f"📊 Data retrieved: {type(data)} with keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            if "error" in data:
                print(f"❌ Data retrieval error: {data['error']}")
                return self._get_error_response(f"Data retrieval failed: {data['error']}")
            
            # Format context more simply
            context = self._format_context(data)
            print(f"📝 Context formatted: {len(context)} characters")
            print(f"📋 Context preview: {context[:200]}...")
            
            # Format messages
            messages = self.format_messages(question=question, context=context)
            
            # Invoke LLM with proper error handling
            analysis = self.invoke_llm(llm, messages, session_memory, 
                                     question=question, project_id=project_id, scope=scope)
            
            print(f"🤖 LLM Response: {len(analysis)} characters")
            print(f"📋 LLM Response preview: {analysis[:300]}...")
            
            # Validate that we got a valid JSON response
            if analysis and analysis.strip():
                try:
                    # Try to parse the response to ensure it's valid JSON
                    parsed_analysis = json.loads(analysis)
                    print("✅ Analysis completed with valid JSON")
                    print(f"📊 Parsed analysis keys: {list(parsed_analysis.keys()) if isinstance(parsed_analysis, dict) else 'N/A'}")
                except json.JSONDecodeError as e:
                    print(f"⚠️ Analysis response is not valid JSON: {e}")
                    print(f"📋 Raw response: {analysis}")
                    # Return a structured error response instead of invalid JSON
                    return self._get_error_response(f"Analysis produced invalid JSON: {str(e)}")
            else:
                print("❌ Empty analysis response received")
                return self._get_error_response("Empty analysis response received")
            
            return analysis
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            print(f"❌ {error_msg}")
            return self._get_error_response(error_msg)
    
    def _get_analysis_data(self, project_id: str = None, scope: str = "company") -> Dict[str, Any]:
        """Get analysis data with improved error handling."""
        try:
            if project_id:
                # Project-specific analysis
                project_analysis = self.data_client.get_project_skill_gaps_sync(project_id)
                employee_skills = self.data_client.get_employee_skills_sync()
                team_composition = self.data_client.get_team_composition_sync()
                skill_market_data = self.data_client.get_skill_market_data_sync()
                
                return {
                    "project_analysis": project_analysis,
                    "employee_skills": employee_skills,
                    "team_composition": team_composition,
                    "skill_market_data": skill_market_data,
                    "project_id": project_id,
                    "scope": scope
                }
            else:
                # General analysis
                employee_skills = self.data_client.get_employee_skills_sync()
                project_requirements = self.data_client.get_project_requirements_sync()
                team_composition = self.data_client.get_team_composition_sync()
                skill_market_data = self.data_client.get_skill_market_data_sync()
                
                return {
                    "employee_skills": employee_skills,
                    "project_requirements": project_requirements,
                    "team_composition": team_composition,
                    "skill_market_data": skill_market_data,
                    "scope": scope
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def _format_context(self, data: Dict[str, Any]) -> str:
        """Format data into context for the LLM."""
        context_parts = []
        
        if "project_analysis" in data:
            context_parts.append(f"Project Analysis: {json.dumps(data['project_analysis'], indent=2)}")
        
        if "employee_skills" in data:
            context_parts.append(f"Employee Skills: {json.dumps(data['employee_skills'], indent=2)}")
        
        if "project_requirements" in data:
            context_parts.append(f"Project Requirements: {json.dumps(data['project_requirements'], indent=2)}")
        
        if "team_composition" in data:
            context_parts.append(f"Team Composition: {json.dumps(data['team_composition'], indent=2)}")
        
        if "skill_market_data" in data:
            context_parts.append(f"Skill Market Data: {json.dumps(data['skill_market_data'], indent=2)}")
        
        return "\n\n".join(context_parts)
    
    def _get_error_response(self, error_msg: str) -> str:
        """Get error response in proper format."""
        error_analysis = {
            "skill_gaps": [],
            "upskilling": [],
            "internal_transfers": [],
            "hiring": [],
            "timeline_assessment": f"Analysis failed: {error_msg}",
            "risk_factors": ["Analysis error occurred"],
            "success_probability": "low"
        }
        return json.dumps(error_analysis, indent=2)

# Legacy function wrappers for backward compatibility
def analyze_facts(normalized_question: str, llm, session_memory: SessionMemory = None, project_id: str = None, scope: str = "company") -> str:
    """Analyze facts using the improved agent."""
    agent = AnalysisAgent()
    return agent.process(normalized_question, llm, session_memory, project_id, scope)

def analyze_project_facts(project_id: str, llm, session_memory: SessionMemory = None) -> str:
    """Analyze project facts using the improved agent."""
    agent = AnalysisAgent()
    return agent.process(f"Analyze skill gaps for project {project_id}", llm, session_memory, project_id, "project")

def get_information_for_project(project_id: str, session_memory: SessionMemory = None) -> tuple:
    """Get information for a specific project from the data client."""
    data_client = get_data_client()
    project_analysis = data_client.get_project_skill_gaps_sync(project_id)
    employee_skills = data_client.get_employee_skills_sync()
    team_composition = data_client.get_team_composition_sync()
    skill_market_data = data_client.get_skill_market_data_sync()
    
    return project_analysis, employee_skills, team_composition, skill_market_data

def get_information(question: str, llm, session_memory: SessionMemory = None) -> tuple:
    """Get information from the data client."""
    data_client = get_data_client()
    return (
        data_client.get_employee_skills_sync(),
        data_client.get_project_requirements_sync(),
        data_client.get_team_composition_sync(),
        data_client.get_skill_market_data_sync()
    )
