#!/usr/bin/env python3
"""
Test the enhanced decision agent with flexible schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.decision import make_decision
from core.llm_factory import make_all_agent_llms
from core.memory_system import SessionMemory
import json

def test_enhanced_decision():
    """Test the enhanced decision agent with flexible schema."""
    
    print("🧪 Testing Enhanced Decision Agent")
    print("=" * 50)
    
    # Create LLM and session memory
    agent_llms = make_all_agent_llms("anthropic")
    decision_llm = agent_llms["decision"]
    session_memory = SessionMemory()
    
    # Sample analysis data that would trigger specific recommendations
    sample_analysis = {
        "skill_gaps": ["AWS", "Kubernetes", "React"],
        "upskilling": [
            {
                "employee": "John Smith",
                "skill_to_learn": "AWS",
                "timeline_weeks": 4,
                "confidence": "high",
                "reason": "Strong Python background transfers well to AWS"
            }
        ],
        "internal_transfers": [
            {
                "employee": "Alexa Johnson",
                "current_team": "DevOps",
                "skills_brought": ["AWS", "Kubernetes"],
                "availability": "immediate",
                "reason": "5 years AWS experience, perfect fit for project"
            },
            {
                "employee": "Kim Chen",
                "current_team": "Frontend",
                "skills_brought": ["React", "JavaScript"],
                "availability": "2 weeks",
                "reason": "2 years React experience, needs AWS training"
            }
        ],
        "hiring": [
            {
                "role": "Senior AWS Engineer",
                "required_skills": ["AWS", "Terraform", "Kubernetes"],
                "urgency": "high",
                "estimated_cost": "$120k-$160k"
            }
        ],
        "timeline_assessment": "4-6 weeks for upskilling, 2-3 months for hiring",
        "risk_factors": ["Limited AWS expertise", "Tight timeline"],
        "success_probability": "high"
    }
    
    test_cases = [
        {
            "name": "Project with specific people comparison",
            "question": "We need to assign someone to our AWS migration project. Who should we choose between Alexa and Kim?",
            "analysis": json.dumps(sample_analysis)
        },
        {
            "name": "General skill gap analysis",
            "question": "What should we do about our React skill gaps?",
            "analysis": json.dumps(sample_analysis)
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Question: {test_case['question']}")
        
        try:
            result = make_decision(
                test_case['question'], 
                test_case['analysis'], 
                decision_llm, 
                session_memory
            )
            
            print(f"   📊 Result length: {len(result)} characters")
            print(f"   📋 Result preview: {result[:300]}...")
            
            # Try to parse the result as JSON
            try:
                parsed_result = json.loads(result)
                print(f"   ✅ Valid JSON structure")
                print(f"   🔑 Keys: {list(parsed_result.keys())}")
                
                # Check for new flexible fields
                if 'specific_people_recommendations' in parsed_result:
                    print(f"   👥 Specific people recommendations: {parsed_result['specific_people_recommendations']}")
                
                if 'skill_comparisons' in parsed_result:
                    print(f"   🔍 Skill comparisons: {parsed_result['skill_comparisons']}")
                
                if 'comparison_details' in parsed_result.get('selected_strategy', {}):
                    print(f"   📊 Comparison details: {parsed_result['selected_strategy']['comparison_details']}")
                
                if 'experience_years' in parsed_result.get('selected_strategy', {}):
                    print(f"   📈 Experience years: {parsed_result['selected_strategy']['experience_years']}")
                
                print(f"   ✅ Enhanced decision agent working with flexible schema")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON: {e}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_decision()
