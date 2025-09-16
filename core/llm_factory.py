"""
LLM Factory - Creates and configures language models for different purposes with reasoning patterns
"""

import os
from typing import Any, Dict, List
from core.memory_system import ReasoningPattern, SessionMemory, MemoryLogger, get_memory_system
from config import LLM_OUTPUT_VERBOSE, LLM_OUTPUT_SHOW_PATTERNS, LLM_OUTPUT_SHOW_RESPONSES

# Get memory logger
_, memory_logger = get_memory_system()

# Configuration
BACKEND = os.getenv("BACKEND", "anthropic").lower()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

class FakeLLM:
    """Mock LLM for testing and development with reasoning pattern support."""
    
    def __init__(self, name: str = "fake", temperature: float = 0.0):
        self.name = name
        self.temperature = temperature
        self.reasoning_pattern = ReasoningPattern.COT  # Default to Chain of Thought
    
    def set_reasoning_pattern(self, pattern: ReasoningPattern):
        """Set the reasoning pattern for this LLM."""
        self.reasoning_pattern = pattern
    
    def invoke(self, messages: list) -> Any:
        """Mock response for testing with reasoning steps."""
        class MockResponse:
            def __init__(self, content: str, reasoning_steps: List[str] = None):
                self.content = content
                self.reasoning_steps = reasoning_steps or []
        
        # Generate reasoning steps based on pattern
        reasoning_steps = self._generate_reasoning_steps()
        
        # Print reasoning steps to terminal if verbose output is enabled
        if LLM_OUTPUT_VERBOSE and LLM_OUTPUT_SHOW_PATTERNS:
            print(f"\n🤖 {self.name.upper()} REASONING ({self.reasoning_pattern.value.upper()}):")
            print("=" * 60)
            for i, step in enumerate(reasoning_steps, 1):
                print(f"   {i}. {step}")
            print("=" * 60)
        
        # Log the reasoning pattern usage
        memory_logger.log_agent_reasoning("FakeLLM", self.reasoning_pattern, reasoning_steps)
        
        # Simple mock responses based on the first message content
        messages_str = str(messages).lower()
        print(f"🔍 DEBUG: FakeLLM checking messages: {messages_str[:200]}...")
        
        if "perception" in messages_str or "json api" in messages_str:
            response_content = '''{
  "intent": "skill_gap_analysis",
  "entities": {
    "skills": ["AWS", "Terraform", "Kubernetes", "Linux", "Python"],
    "projects": ["Cloud Migration Initiative"],
    "teams": [],
    "people": [],
    "timelines": ["2024-07-01 to 2025-01-31"]
  },
  "normalized_question": "Analyze skill gaps for Cloud Migration Initiative project",
  "context": {
    "constraints": ["Budget: $900,000"],
    "urgency": "high",
    "scope": "company"
  },
  "analysis_focus": "Cloud migration skills gap analysis"
}'''
            print("🔍 DEBUG: Using perception response")
        elif "decision" in messages_str and "decision agent" in messages_str:
            print("🔍 DEBUG: Using decision response")
            response_content = '''{
  "natural_language_summary": "Based on the analysis, we recommend upskilling John Smith in AWS over 4 weeks. This approach leverages existing team strengths while addressing the critical AWS skill gap. The timeline is realistic given John's strong Python background, and the cost is manageable compared to hiring external talent.",
  "selected_strategy": {
    "strategy_name": "Upskill John Smith for AWS",
    "strategy_type": "upskill",
    "confidence": "high",
    "rationale": "John has strong Python background which transfers well to AWS, reducing learning curve and timeline"
  },
  "strategy_details": {
    "primary_action": "Provide John with AWS training and hands-on practice",
    "target_skill": "AWS Cloud Architecture",
    "timeline_weeks": 4,
    "success_probability": "high",
    "cost_estimate": "medium",
    "risk_level": "low"
  },
  "implementation_plan": {
    "primary_owner": "John Smith",
    "support_team": ["David Kim", "Michael Chen"],
    "timeline_weeks": 4,
    "key_milestones": ["Week 1: AWS fundamentals", "Week 2: Hands-on labs", "Week 3: Project practice", "Week 4: Certification prep"],
    "success_metrics": ["AWS certification passed", "Can deploy basic infrastructure", "Confident with core services"],
    "budget_estimate": "$2,000 - $3,000",
    "resource_requirements": ["AWS training course", "Lab environment access", "Mentor time"]
  },
  "risk_mitigation": {
    "primary_risks": ["Learning curve steeper than expected", "Project timeline conflicts"],
    "mitigation_strategies": ["Start with fundamentals", "Schedule dedicated learning time", "Pair with experienced team member"],
    "contingency_plan": "Consider hiring AWS specialist if upskilling timeline extends beyond 6 weeks",
    "monitoring_points": ["Weekly progress check-ins", "Hands-on project milestones"]
  },
  "review_schedule": {
    "next_review_date": "2025-10-07",
    "review_frequency": "Weekly during training, monthly after completion",
    "success_criteria": ["AWS certification achieved", "Can independently deploy infrastructure", "Team confidence in AWS capabilities"]
  },
  "alternative_strategies": [
    {
      "strategy_name": "Hire AWS Specialist",
      "approach": "Recruit external AWS expert",
      "selection_reason": "Higher cost and longer timeline, but immediate expertise",
      "confidence_score": 0.7
    },
    {
      "strategy_name": "Transfer from DevOps Team",
      "approach": "Move David Kim to project team",
      "selection_reason": "David has AWS expertise but would leave DevOps team short-staffed",
      "confidence_score": 0.6
    }
  ]
}'''
        elif "analysis" in messages_str or "analysis agent" in messages_str:
            print("🔍 DEBUG: Using analysis response")
            response_content = '''{
  "skill_gaps": ["AWS", "Cloud Architecture"],
  "upskilling": [
    {
      "employee": "John Smith",
      "skill_to_learn": "AWS",
      "timeline_weeks": 4,
      "confidence": "high",
      "reason": "Strong Python background transfers well to AWS"
    }
  ],
  "internal_transfers": [],
  "hiring": [
    {
      "role": "AWS Solutions Architect",
      "required_skills": ["AWS", "Cloud Architecture", "Python"],
      "urgency": "high",
      "estimated_cost": "$120,000 - $150,000"
    }
  ],
  "timeline_assessment": "4-6 weeks for team readiness",
  "risk_factors": ["Learning curve", "Timeline pressure"],
  "success_probability": "high"
}'''
        elif "research" in messages_str:
            response_content = "Project requires Python, React, and AWS. Team has Python and React skills but lacks AWS expertise."
            print("🔍 DEBUG: Using research response")
        else:
            response_content = "Mock response for testing purposes"
        
        # Print response to terminal if enabled
        if LLM_OUTPUT_VERBOSE and LLM_OUTPUT_SHOW_RESPONSES:
            print(f"\n📤 RESPONSE:")
            print(f"   {response_content}")
            print()
        
        return MockResponse(response_content, reasoning_steps)
    
    def _generate_reasoning_steps(self) -> List[str]:
        """Generate reasoning steps based on the current pattern."""
        if self.reasoning_pattern == ReasoningPattern.REWOO:
            return [
                "Reason: Analyzing the input to understand requirements",
                "Evaluate: Assessing available information and constraints",
                "Work: Processing the data systematically",
                "Observe: Identifying patterns and insights",
                "Optimize: Finding the best possible solution"
            ]
        elif self.reasoning_pattern == ReasoningPattern.REACT:
            return [
                "Reason: Understanding the problem context",
                "Evaluate: Assessing the current situation",
                "Act: Taking action based on analysis",
                "Check: Verifying the action's effectiveness",
                "Think: Reflecting on the outcome"
            ]
        elif self.reasoning_pattern == ReasoningPattern.COT:
            return [
                "Step 1: Understanding the input",
                "Step 2: Breaking down the problem",
                "Step 3: Analyzing each component",
                "Step 4: Synthesizing the solution",
                "Step 5: Providing the final answer"
            ]
        elif self.reasoning_pattern == ReasoningPattern.TOT:
            return [
                "Root: Starting with the main question",
                "Branch 1: Exploring first approach",
                "Branch 2: Considering alternative approach",
                "Evaluate: Comparing approaches",
                "Select: Choosing the best path"
            ]
        else:  # AGENT pattern
            return [
                "Agent 1: Specialized analysis",
                "Agent 2: Cross-validation",
                "Agent 3: Synthesis and integration",
                "Coordinator: Final decision making"
            ]

class AnthropicLLM:
    """Anthropic Claude LLM wrapper with reasoning pattern support."""
    
    def __init__(self, model: str = ANTHROPIC_MODEL, temperature: float = TEMPERATURE):
        self.model = model
        self.temperature = temperature
        self.reasoning_pattern = ReasoningPattern.COT  # Default to Chain of Thought
        
        # Get API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
        
        # Check for proxy-related environment variables that might cause issues
        proxy_vars = [k for k in os.environ.keys() if 'proxy' in k.lower()]
        if proxy_vars:
            print(f"⚠️  Found proxy environment variables: {proxy_vars}")
            print("   These might cause issues with Anthropic client initialization")
        
        # Initialize Anthropic client
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise RuntimeError("anthropic not installed. pip install anthropic")
    
    def set_reasoning_pattern(self, pattern: ReasoningPattern):
        """Set the reasoning pattern for this LLM."""
        self.reasoning_pattern = pattern
    
    def invoke(self, messages: list) -> Any:
        """Invoke the Anthropic LLM with reasoning pattern enhancement."""
        try:
            # Convert messages to Anthropic format
            system_message = ""
            user_message = ""
            
            for msg in messages:
                if hasattr(msg, 'content'):
                    if hasattr(msg, 'role') and msg.role == 'system':
                        system_message = msg.content
                    else:
                        user_message = msg.content
                else:
                    user_message = str(msg)
            
            # Enhance with reasoning pattern instructions
            enhanced_system = self._enhance_with_reasoning(system_message)
            
            # Make API call to Anthropic
            if enhanced_system:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=self.temperature,
                    system=enhanced_system,
                    messages=[{"role": "user", "content": user_message}]
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": user_message}]
                )
            
            # Return in compatible format
            class AnthropicResponse:
                def __init__(self, content: str):
                    self.content = content
                    self.reasoning_steps = []
            
            return AnthropicResponse(response.content[0].text)
            
        except Exception as e:
            print(f"❌ Anthropic API error: {e}")
            print("🔄 Falling back to fake backend...")
            fake_llm = FakeLLM("anthropic-fallback", self.temperature)
            fake_llm.set_reasoning_pattern(self.reasoning_pattern)
            return fake_llm.invoke(messages)
    
    def _enhance_with_reasoning(self, system_message: str) -> str:
        """Enhance system message with reasoning pattern instructions."""
        reasoning_instructions = {
            ReasoningPattern.REWOO: "Use REWOO reasoning: Reason, Evaluate, Work, Observe, Optimize",
            ReasoningPattern.REACT: "Use REACT reasoning: Reason, Evaluate, Act, Check, Think",
            ReasoningPattern.COT: "Use Chain of Thought reasoning with clear step-by-step analysis",
            ReasoningPattern.TOT: "Use Tree of Thoughts reasoning exploring multiple approaches",
            ReasoningPattern.AGENT: "Use multi-agent reasoning with specialized perspectives"
        }
        
        instruction = reasoning_instructions.get(self.reasoning_pattern, "")
        if instruction:
            return f"{system_message}\n\n{instruction}"
        return system_message

class GroqLLM:
    """Groq LLM client with reasoning pattern support."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or GROQ_MODEL
        self.reasoning_pattern = ReasoningPattern.COT
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required for Groq backend")
        
        # Initialize Groq client
        try:
            import groq
            self.client = groq.Groq(api_key=self.api_key)
            print(f"✅ Groq client initialized with model: {self.model}")
        except ImportError:
            print("❌ Install groq: pip install groq")
            raise
        except Exception as e:
            print(f"❌ Groq client error: {e}")
            raise
    
    def set_reasoning_pattern(self, pattern: ReasoningPattern):
        """Set the reasoning pattern for this LLM."""
        self.reasoning_pattern = pattern
    
    def invoke(self, messages: list) -> Any:
        """Invoke the Groq LLM with reasoning pattern enhancement."""
        try:
            # Show reasoning pattern
            if LLM_OUTPUT_VERBOSE and LLM_OUTPUT_SHOW_PATTERNS:
                print(f"\n🤖 GROQ LLM REASONING ({self.reasoning_pattern.value.upper()}):")
                print(f"   Model: {self.model}")
                print(f"   Pattern: {self.reasoning_pattern.value.upper()}")
            
            # Enhance messages with reasoning instructions
            enhanced_messages = self._enhance_with_reasoning(messages)
            
            # Convert to Groq format
            groq_messages = []
            for msg in enhanced_messages:
                if hasattr(msg, 'content'):
                    role = "system" if hasattr(msg, 'role') and msg.role == 'system' else "user"
                    groq_messages.append({"role": role, "content": msg.content})
                else:
                    groq_messages.append({"role": "user", "content": str(msg)})
            
            print(f"📤 Sending to Groq API...")
            
            # REAL GROQ API CALL
            response = self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            response_content = response.choices[0].message.content
            
            # Show response
            if LLM_OUTPUT_VERBOSE and LLM_OUTPUT_SHOW_RESPONSES:
                print(f"\n📤 GROQ RESPONSE:")
                print(f"   {response_content}")
            
            class GroqResponse:
                def __init__(self, content: str):
                    self.content = content
                    self.reasoning_steps = []
            
            return GroqResponse(response_content)
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            print("🔄 Falling back to fake backend...")
            fake_llm = FakeLLM()
            fake_llm.set_reasoning_pattern(self.reasoning_pattern)
            return fake_llm.invoke(messages)
    
    def _enhance_with_reasoning(self, messages: list) -> list:
        """Enhance messages with reasoning pattern instructions."""
        reasoning_instructions = {
            ReasoningPattern.REWOO: "Use REWOO reasoning: Reason, Evaluate, Work, Observe, Optimize",
            ReasoningPattern.REACT: "Use REACT reasoning: Reason, Evaluate, Act, Check, Think",
            ReasoningPattern.COT: "Use Chain of Thought reasoning with clear step-by-step analysis",
            ReasoningPattern.TOT: "Use Tree of Thoughts reasoning exploring multiple approaches",
            ReasoningPattern.AGENT: "Use multi-agent reasoning with specialized perspectives"
        }
        
        instruction = reasoning_instructions.get(self.reasoning_pattern, "")
        if instruction:
            # Add reasoning instruction to the first system message
            for i, msg in enumerate(messages):
                if hasattr(msg, 'content') and 'system' in str(msg).lower():
                    messages[i].content += f"\n\n{instruction}"
                    break
        
        return messages

def make_llm(backend: str = None, reasoning_pattern: ReasoningPattern = ReasoningPattern.COT):
    """Create a language model instance with reasoning pattern support."""
    if backend is None:
        backend = BACKEND
    
    backend = backend.lower()
    
    if backend == "fake":
        llm = FakeLLM("fake", TEMPERATURE)
        llm.set_reasoning_pattern(reasoning_pattern)
        return llm
    
    elif backend == "anthropic":
        try:
            llm = AnthropicLLM(ANTHROPIC_MODEL, TEMPERATURE)
            llm.set_reasoning_pattern(reasoning_pattern)
            return llm
        except Exception as e:
            print(f"⚠️  Anthropic failed: {e}, falling back to fake backend")
            llm = FakeLLM("anthropic-fallback", TEMPERATURE)
            llm.set_reasoning_pattern(reasoning_pattern)
            return llm
    
    elif backend == "groq":
        try:
            llm = GroqLLM()
            llm.set_reasoning_pattern(reasoning_pattern)
            return llm
        except Exception as e:
            print(f"⚠️  Groq failed: {e}, falling back to fake backend")
            llm = FakeLLM("groq-fallback", TEMPERATURE)
            llm.set_reasoning_pattern(reasoning_pattern)
            return llm
    
    else:
        raise ValueError(f"Unsupported backend: {backend}")

def make_reasoner(backend: str = None, reasoning_pattern: ReasoningPattern = ReasoningPattern.REWOO):
    """Create a reasoning-optimized language model instance."""
    return make_llm(backend, reasoning_pattern)

def make_perception_llm(backend: str = None):
    """Create a perception-optimized LLM with Chain of Thought reasoning."""
    return make_llm(backend, ReasoningPattern.COT)

def make_research_llm(backend: str = None):
    """Create a research-optimized LLM with REWOO reasoning."""
    return make_llm(backend, ReasoningPattern.REWOO)

def make_analysis_llm(backend: str = None):
    """Create an analysis-optimized LLM with REACT reasoning."""
    return make_llm(backend, ReasoningPattern.REACT)

def make_decision_llm(backend: str = None):
    """Create a decision-optimized LLM with Tree of Thoughts reasoning."""
    return make_llm(backend, ReasoningPattern.TOT)

def make_orchestrator_llm(backend: str = None):
    """Create an orchestrator-optimized LLM with Multi-agent reasoning."""
    return make_llm(backend, ReasoningPattern.AGENT)


def make_all_agent_llms(backend: str = None):
    """Create all specialized LLMs for the multi-agent system."""
    return {
        "perception": make_perception_llm(backend),
        "research": make_research_llm(backend),
        "analysis": make_analysis_llm(backend),
        "decision": make_decision_llm(backend),
        "orchestrator": make_orchestrator_llm(backend)
    }