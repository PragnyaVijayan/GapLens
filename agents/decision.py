"""
Decision Agent - Makes final recommendations for skills gap solutions
"""

from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory
from .base_agent import BaseAgent
from .schemas import validate_decision_output, DecisionOutput
import json

DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the Decision Agent for GapLens Skills Analysis System.

CRITICAL: You must return ONLY a valid JSON object. NO additional text, explanations, or verbose output.
If you cannot format as JSON, you may use YAML format instead, but JSON is preferred.

## Your Role:
Make specific, actionable recommendations with detailed reasoning. For example:
- "Move Alexa to this project over Kim because she has 5 years of AWS experience vs Kim's 2 years"
- "Upskill John in React over hiring because he already knows JavaScript and can be productive in 3 weeks"
- "Transfer Sarah from the backend team because she has the exact Kubernetes skills needed"

## Output Format:
Return ONLY this exact JSON structure with NO additional text:

{{
  "natural_language_summary": "<comprehensive recommendation summary in natural language>",
  "selected_strategy": {{
    "strategy_name": "<strategy name>",
    "strategy_type": "upskill|transfer|hire|mixed",
    "confidence": "high|medium|low",
    "rationale": "<why this strategy was selected>",
    "specific_people": ["<Person1>", "<Person2>"],
    "specific_skills": ["<skill1>", "<skill2>"],
    "comparison_details": "<detailed comparison between options>",
    "experience_years": {{"<Person1>": <years>, "<Person2>": <years>}}
  }},
  "strategy_details": {{
    "primary_action": "<main action to take>",
    "target_skill": "<skill to focus on>",
    "timeline_weeks": <number>,
    "success_probability": "high|medium|low",
    "cost_estimate": "low|medium|high",
    "risk_level": "low|medium|high",
    "specific_recommendations": ["<specific rec1>", "<specific rec2>"],
    "why_not_alternatives": ["<reason1>", "<reason2>"],
    "immediate_actions": ["<action1>", "<action2>"]
  }},
  "implementation_plan": {{
    "primary_owner": "<Full Name>",
    "support_team": ["<Name1>", "<Name2>"],
    "timeline_weeks": <number>,
    "key_milestones": ["<milestone1>", "<milestone2>"],
    "success_metrics": ["<metric1>", "<metric2>"],
    "budget_estimate": "<cost estimate>",
    "resource_requirements": ["<requirement1>", "<requirement2>"],
    "team_assignments": {{"<Person1>": "<role1>", "<Person2>": "<role2>"}},
    "skill_development_plan": {{"<Person1>": "<plan1>", "<Person2>": "<plan2>"}}
  }},
  "risk_mitigation": {{
    "primary_risks": ["<risk1>", "<risk2>"],
    "mitigation_strategies": ["<strategy1>", "<strategy2>"],
    "contingency_plan": "<brief contingency>",
    "monitoring_points": ["<point1>", "<point2>"]
  }},
  "review_schedule": {{
    "next_review_date": "<when to reassess>",
    "review_frequency": "<how often>",
    "success_criteria": ["<criteria1>", "<criteria2>"]
  }},
  "alternative_strategies": [
    {{
      "strategy_name": "<alternative strategy name>",
      "approach": "<brief description>",
      "selection_reason": "<why not selected>",
      "confidence_score": <number>
    }}
  ],
  "specific_people_recommendations": {{"<Person1>": "<role and reason>", "<Person2>": "<role and reason>"}},
  "skill_comparisons": {{"<Person1>": {{"aws": 5, "python": 3}}, "<Person2>": {{"aws": 2, "python": 4}}}},
  "project_impact": {{"<Project1>": "<impact description>", "<Project2>": "<impact description>"}},
  "success_factors": ["<factor1>", "<factor2>"],
  "potential_obstacles": ["<obstacle1>", "<obstacle2>"]
}}

## STRICT RULES:
- Return ONLY the JSON object above
- NO explanations, NO verbose text, NO additional information
- Use full employee names from the data
- Keep all text fields brief and focused
- If no data available for a section, use empty arrays []
- Validate JSON before returning
- DO NOT use markdown formatting, bullet points, or any other text formatting
- Start your response with {{ and end with }}"""),
    ("human", "Question: {question}\n\nAnalysis: {analysis}")
])

class DecisionAgent(BaseAgent):
    """Agent for making final actionable recommendations."""
    
    def __init__(self):
        super().__init__(
            name="Decision",
            reasoning_pattern=ReasoningPattern.TOT,  # Tree of Thoughts reasoning
            prompt_template=DECISION_PROMPT
        )
    
    def process(self, question: str, analysis: str, llm, session_memory: SessionMemory = None) -> str:
        """Make a final decision using the decision agent."""
        print(f"📋 Analysis input length: {len(analysis)} characters")
        print("🤖 Sending decision request to LLM...")
        
        try:
            # Format messages
            messages = self.format_messages(
                question=question,
                analysis=analysis
            )
            
            # Invoke LLM with proper logging
            decision = self.invoke_llm(llm, messages, session_memory)
            
            # Extract JSON from decision output if it contains narrative text
            decision = self._extract_json_from_response(decision)
            
            # Validate decision output with Pydantic schema
            try:
                decision_json = json.loads(decision)
                validated_decision = validate_decision_output(decision_json)
                print("✅ Decision schema validation passed")
                # Convert back to JSON string for consistency
                decision = json.dumps(validated_decision.dict(), indent=2)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}")
                # Try to create a fallback decision from the narrative
                decision = self._create_fallback_decision(decision, question, analysis)
            except Exception as validation_error:
                print(f"⚠️ Schema validation failed: {validation_error}")
                # Try to create a fallback decision from the narrative
                decision = self._create_fallback_decision(decision, question, analysis)
            
            print(f"🎯 Decision Output: {decision}")
            
            # Update session data if available
            if session_memory:
                session_memory.update_session_data("decision", decision)
                session_memory.update_session_data("current_step", "completed")
            
            return decision
            
        except Exception as e:
            error_msg = f"Error during decision making: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Log error to memory if available
            if session_memory:
                session_memory.add_entry(
                    agent="decision",
                    content=error_msg,
                    reasoning_pattern=ReasoningPattern.TOT,
                    reasoning_steps=["Error occurred during decision phase"],
                    confidence=0.1,
                    metadata={"error": str(e), "question": question, "analysis": analysis}
                )
            
            return error_msg
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response that may contain narrative text."""
        if not response:
            return self._get_fallback_json()
        
        # Look for JSON object in the response
        response = response.strip()
        
        # If response starts and ends with braces, it's likely JSON
        if response.startswith('{') and response.endswith('}'):
            return response
        
        # Look for JSON object within the response
        start_idx = response.find('{')
        if start_idx != -1:
            # Find the matching closing brace
            brace_count = 0
            end_idx = start_idx
            for i, char in enumerate(response[start_idx:], start_idx):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break
            
            if brace_count == 0:
                return response[start_idx:end_idx + 1]
        
        # If no JSON found, return fallback
        return self._get_fallback_json()
    
    def _create_fallback_decision(self, narrative: str, question: str, analysis: str) -> str:
        """Create a fallback decision from narrative text."""
        # Extract key information from narrative using simple text processing
        strategy_name = "Upskilling Strategy"
        strategy_type = "upskill"
        primary_action = "Upskill team members"
        target_skill = "Required skills"
        
        # Look for specific skills mentioned
        if "kubernetes" in narrative.lower():
            target_skill = "Kubernetes"
        elif "aws" in narrative.lower():
            target_skill = "AWS"
        elif "terraform" in narrative.lower():
            target_skill = "Terraform"
        
        # Look for employee names
        primary_owner = "Team Lead"
        if "michael chen" in narrative.lower():
            primary_owner = "Michael Chen"
        elif "david kim" in narrative.lower():
            primary_owner = "David Kim"
        
        # Create fallback decision
        fallback = {
            "natural_language_summary": f"Based on the analysis, we recommend {strategy_name.lower()} to address the skill gaps identified.",
            "selected_strategy": {
                "strategy_name": strategy_name,
                "strategy_type": strategy_type,
                "confidence": "medium",
                "rationale": "Cost-effective approach to build internal capability"
            },
            "strategy_details": {
                "primary_action": primary_action,
                "target_skill": target_skill,
                "timeline_weeks": 8,
                "success_probability": "medium",
                "cost_estimate": "low",
                "risk_level": "medium"
            },
            "implementation_plan": {
                "primary_owner": primary_owner,
                "support_team": [],
                "timeline_weeks": 8,
                "key_milestones": ["Week 2: Training start", "Week 6: Practice", "Week 8: Implementation"],
                "success_metrics": ["Skill demonstration", "Project completion"],
                "budget_estimate": "$2,000-$5,000",
                "resource_requirements": ["Training materials", "Mentor time"]
            },
            "risk_mitigation": {
                "primary_risks": ["Learning curve", "Timeline pressure"],
                "mitigation_strategies": ["Dedicated time", "Mentorship"],
                "contingency_plan": "External consultant if needed",
                "monitoring_points": ["Weekly reviews", "Progress assessments"]
            },
            "review_schedule": {
                "next_review_date": "2024-03-01",
                "review_frequency": "Weekly",
                "success_criteria": ["Skill demonstration", "Project success"]
            },
            "alternative_strategies": [
                {
                    "strategy_name": "Hiring Strategy",
                    "approach": "Recruit experienced professionals",
                    "selection_reason": "Higher cost and longer timeline",
                    "confidence_score": 0.6
                }
            ]
        }
        
        return json.dumps(fallback, indent=2)

# Legacy function for backward compatibility
def make_decision(question: str, analysis: str, llm, session_memory: SessionMemory = None) -> str:
    """Make a final decision using the decision agent."""
    agent = DecisionAgent()
    return agent.process(question, analysis, llm, session_memory) 