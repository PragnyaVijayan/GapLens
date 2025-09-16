#!/usr/bin/env python3
"""
Test the improved JSON parsing with LangChain and YAML support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.perception import perceive_input
from core.llm_factory import make_all_agent_llms
from core.memory_system import SessionMemory

def test_improved_json_parsing():
    """Test the improved JSON parsing with real LLM responses."""
    
    print("🧪 Testing Improved JSON Parsing")
    print("=" * 50)
    
    # Create LLM and session memory
    agent_llms = make_all_agent_llms("anthropic")
    perception_llm = agent_llms["perception"]
    session_memory = SessionMemory()
    
    # Test cases that might cause JSON parsing issues
    test_cases = [
        "What are our Python skill gaps?",
        "Analyze the skill gaps for this specific project and provide structured recommendations.\n\nProject ID: proj_005\nProject Name: Cloud Migration Initiative\nRequired Skills: AWS, Terraform, Kubernetes, Linux, Python\nTimeline: 2024-07-01 to 2025-01-31\nBudget: $900,000\nScope: department"
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {question[:100]}{'...' if len(question) > 100 else ''}")
        
        try:
            result = perceive_input(question, perception_llm, session_memory)
            
            print(f"   📊 Result type: {type(result)}")
            print(f"   🔑 Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            print(f"   ✅ Intent: {result.get('intent', 'N/A')}")
            print(f"   📝 Normalized: {result.get('normalized_question', 'N/A')[:50]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_improved_json_parsing()
