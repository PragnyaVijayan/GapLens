"""
Base Agent Class - Common functionality for all agents
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict
from langchain.prompts import ChatPromptTemplate
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
import json
import re
import yaml
from langchain_core.utils.json import parse_json_markdown
from config import AGENT_VERBOSE_OUTPUT, AGENT_SHOW_JSON_VALIDATION
from .schemas import (
    validate_perception_output, 
    validate_analysis_output, 
    validate_decision_output,
    PerceptionOutput,
    AnalysisOutput,
    DecisionOutput
)

class BaseAgent(ABC):
    """Base class for all agents with common functionality."""
    
    def __init__(self, name: str, reasoning_pattern: ReasoningPattern, prompt_template: ChatPromptTemplate):
        self.name = name
        self.reasoning_pattern = reasoning_pattern
        self.prompt_template = prompt_template
        
        # Get memory logger
        _, self.memory_logger = get_memory_system()
    
    @abstractmethod
    def process(self, **kwargs) -> Any:
        """Process the agent's task. Must be implemented by subclasses."""
        pass
    
    def invoke_llm(self, llm, messages: List[Any], session_memory: Optional[SessionMemory] = None, **kwargs) -> Any:
        """Invoke the LLM with proper reasoning pattern and logging."""
        try:
            # Set the reasoning pattern on the LLM
            if hasattr(llm, 'set_reasoning_pattern'):
                llm.set_reasoning_pattern(self.reasoning_pattern)
            
            # Invoke LLM
            response = llm.invoke(messages)
            content = getattr(response, "content", str(response))
            reasoning_steps = getattr(response, "reasoning_steps", [])
            
            # Validate JSON output for agents that should return JSON
            if self.name.lower() in ['perception', 'analysis', 'decision']:
                content = self._validate_and_clean_json(content)
            
            # Log to memory if available
            if session_memory:
                self._log_to_memory(session_memory, content, reasoning_steps, **kwargs)
            
            # Log reasoning pattern usage
            self.memory_logger.log_agent_reasoning(self.name, self.reasoning_pattern, reasoning_steps)
            
            return content
            
        except Exception as e:
            error_msg = f"Error in {self.name} LLM invocation: {str(e)}"
            
            # Log error to memory if available
            if session_memory:
                self._log_error_to_memory(session_memory, error_msg, **kwargs)
            
            raise
    
    def _validate_and_clean_json(self, content: str) -> str:
        """Validate and clean JSON output from LLM with Pydantic schema validation."""
        try:
            print(f"🔍 Validating JSON for {self.name} agent...")
            print(f"   Input: {content[:200]}...")
            
            # Enhanced JSON cleaning
            content = self._clean_json_string(content)
            print(f"   After cleaning: {content[:200]}...")
            
            # Try to parse the cleaned JSON
            parsed_json = json.loads(content)
            print(f"   ✅ JSON parsing successful")
            
            # Validate with Pydantic schema based on agent type
            try:
                if self.name.lower() == 'perception':
                    validated_data = validate_perception_output(parsed_json)
                    print(f"   ✅ Perception schema validation passed")
                elif self.name.lower() == 'analysis':
                    validated_data = validate_analysis_output(parsed_json)
                    print(f"   ✅ Analysis schema validation passed")
                elif self.name.lower() == 'decision':
                    validated_data = validate_decision_output(parsed_json)
                    print(f"   ✅ Decision schema validation passed")
                else:
                    # For other agents, just validate JSON structure
                    print(f"   ✅ JSON structure validation passed")
            except Exception as schema_error:
                print(f"   ⚠️ Schema validation failed: {schema_error}")
                print(f"   📋 Using raw JSON without schema validation")
                # Continue with the raw JSON instead of failing
            
            print(f"   ✅ Valid JSON found after cleaning and schema validation")
            return content
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing failed after cleaning: {e}")
            print(f"   📋 Cleaned content: {content[:200]}...")
            
            # Try additional cleaning strategies
            cleaned_content = self._additional_json_cleaning(content)
            if cleaned_content:
                try:
                    json.loads(cleaned_content)
                    print("   ✅ Additional cleaning successful")
                    return cleaned_content
                except json.JSONDecodeError:
                    print("   ❌ Additional cleaning also failed")
                    pass
            
            # Return empty JSON structure if validation fails
            print(f"   🔄 Returning fallback JSON for {self.name}")
            return self._get_fallback_json()
            
        except Exception as e:
            print(f"   ❌ Schema validation failed: {e}")
            print(f"   📋 Parsed content: {content[:200]}...")
            
            # Return empty JSON structure if validation fails
            print(f"   🔄 Returning fallback JSON for {self.name}")
            return self._get_fallback_json()
    
    def _clean_json_string(self, content: str) -> str:
        """Clean and normalize JSON string from LLM output using multiple strategies."""
        if not content:
            return self._get_fallback_json()
        
        original_content = content.strip()
        
        # Strategy 1: Try LangChain's parse_json_markdown first
        try:
            parsed = parse_json_markdown(original_content)
            if parsed:
                print("   ✅ LangChain parse_json_markdown successful")
                return json.dumps(parsed)
        except Exception as e:
            print(f"   ⚠️ LangChain parse_json_markdown failed: {e}")
        
        # Strategy 2: Try YAML parsing (sometimes LLMs output YAML-like structures)
        try:
            # Look for YAML-like content
            yaml_match = re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*:\s*$', original_content, re.MULTILINE)
            if yaml_match or ':' in original_content and '{' not in original_content:
                # Try to parse as YAML
                yaml_content = original_content
                # Convert YAML-like structure to JSON
                parsed_yaml = yaml.safe_load(yaml_content)
                if parsed_yaml:
                    print("   ✅ YAML parsing successful")
                    return json.dumps(parsed_yaml)
        except Exception as e:
            print(f"   ⚠️ YAML parsing failed: {e}")
        
        # Strategy 3: Enhanced markdown and text removal
        content = original_content
        
        # Remove markdown headers and explanations
        content = re.sub(r'^#+.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^##+.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^###+.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^Step \d+:.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^### Reason.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^### Evaluate.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^### Act.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^### Check.*?\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^### Think.*?\n', '', content, flags=re.MULTILINE)
        
        # Remove any leading text before the first {
        if '{' in content:
            content = content[content.find('{'):]
        
        # Remove any trailing text after the last }
        if '}' in content:
            content = content[:content.rfind('}') + 1]
        
        # If no braces found, return fallback
        if not content.startswith('{') or not content.endswith('}'):
            return self._get_fallback_json()
        
        # Strategy 4: Enhanced JSON cleaning
        content = content.replace('\\"', '"')     # Unescape quotes
        content = content.replace("\\'", "'")     # Unescape single quotes
        
        return content
    
    def _additional_json_cleaning(self, content: str) -> str:
        """Additional JSON cleaning strategies."""
        if not content:
            return ""
        
        # Remove any text before the first {
        start_idx = content.find('{')
        if start_idx > 0:
            content = content[start_idx:]
        
        # Remove any text after the last }
        end_idx = content.rfind('}')
        if end_idx != -1 and end_idx < len(content) - 1:
            content = content[:end_idx + 1]
        
        # Fix common JSON issues
        content = content.replace('\\"', '"')  # Unescape quotes
        content = content.replace("\\'", "'")  # Unescape single quotes
        content = re.sub(r',(\s*[}\]])', r'\1', content)  # Remove trailing commas
        
        return content.strip()
    
    def _get_fallback_json(self) -> str:
        """Get fallback JSON structure for the agent."""
        if self.name.lower() == 'perception':
            return '{"intent": "skill_gap_analysis", "entities": {"skills": [], "projects": [], "teams": [], "people": [], "timelines": []}, "normalized_question": "General skills analysis", "context": {"constraints": [], "urgency": "medium", "scope": "company"}, "analysis_focus": "General skills analysis"}'
        elif self.name.lower() == 'analysis':
            return '{"skill_gaps": [], "upskilling": [], "internal_transfers": [], "hiring": [], "timeline_assessment": "Analysis pending", "risk_factors": [], "success_probability": "low"}'
        elif self.name.lower() == 'decision':
            return '{"natural_language_summary": "Decision pending", "selected_strategy": {"strategy_name": "TBD", "strategy_type": "mixed", "confidence": "low", "rationale": "Analysis pending"}, "strategy_details": {"primary_action": "TBD", "target_skill": "TBD", "timeline_weeks": 4, "success_probability": "low", "cost_estimate": "low", "risk_level": "high"}, "implementation_plan": {"primary_owner": "TBD", "support_team": [], "timeline_weeks": 4, "key_milestones": [], "success_metrics": [], "budget_estimate": "TBD", "resource_requirements": []}, "risk_mitigation": {"primary_risks": [], "mitigation_strategies": [], "contingency_plan": "TBD", "monitoring_points": []}, "review_schedule": {"next_review_date": "TBD", "review_frequency": "TBD", "success_criteria": []}, "alternative_strategies": []}'
        else:
            return '{"error": "Unknown agent type"}'
    
    def _log_to_memory(self, session_memory: SessionMemory, content: Any, reasoning_steps: List[str], **kwargs):
        """Log agent activity to session memory."""
        metadata = {
            "agent_name": self.name,
            "reasoning_pattern": self.reasoning_pattern.value,
            **kwargs
        }
        
        session_memory.add_entry(
            agent=self.name,
            content=content,
            reasoning_pattern=self.reasoning_pattern,
            reasoning_steps=reasoning_steps,
            confidence=0.8,
            metadata=metadata
        )
    
    def _log_error_to_memory(self, session_memory: SessionMemory, error_msg: str, **kwargs):
        """Log agent error to session memory."""
        metadata = {
            "agent_name": self.name,
            "reasoning_pattern": self.reasoning_pattern.value,
            "error": True,
            **kwargs
        }
        
        session_memory.add_entry(
            agent=self.name,
            content=error_msg,
            reasoning_pattern=self.reasoning_pattern,
            reasoning_steps=[f"Error occurred: {error_msg}"],
            confidence=0.1,
            metadata=metadata
        )
    
    def format_messages(self, **kwargs) -> List[Any]:
        """Format messages using the agent's prompt template."""
        return self.prompt_template.format_messages(**kwargs)
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters. Override in subclasses for specific validation."""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.name,
            "reasoning_pattern": self.reasoning_pattern.value,
            "status": "ready"
        }
