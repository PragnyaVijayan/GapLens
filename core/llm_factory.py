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
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
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
        if "perception" in str(messages).lower():
            response_content = '{"intent": "skills_analysis", "entities": ["project", "team"], "normalized_question": "Analyze skills for project"}'
        elif "research" in str(messages).lower():
            response_content = "Project requires Python, React, and AWS. Team has Python and React skills but lacks AWS expertise."
        elif "analysis" in str(messages).lower():
            response_content = "Skills gap identified: AWS expertise missing. Team member John could be upskilled in AWS within 2 weeks."
        elif "decision" in str(messages).lower():
            response_content = "Recommendation: Upskill John in AWS (2 weeks). Alternative: Transfer Sarah from DevOps team. Risk: Low"
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
    
    def __init__(self, api_key: str = None, model: str = "llama3-8b-8192"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
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