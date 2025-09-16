#!/usr/bin/env python3
"""
Test the workflow components used by Streamlit app
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.workflow import MultiAgentWorkflow
from core import make_all_agent_llms
import json

def test_streamlit_workflow():
    """Test the workflow components used by Streamlit app."""
    
    print("🧪 Testing Streamlit Workflow Components")
    print("=" * 60)
    
    # Test LLM creation (same as in streamlit app)
    print("\n📋 Test 1: LLM Creation")
    try:
        agent_llms = make_all_agent_llms("anthropic")
        print(f"   ✅ LLMs created successfully")
        print(f"   🔑 Available LLMs: {list(agent_llms.keys())}")
    except Exception as e:
        print(f"   ❌ LLM creation failed: {e}")
        return False
    
    # Test workflow creation (same as in streamlit app)
    print("\n📋 Test 2: Workflow Creation")
    try:
        workflow = MultiAgentWorkflow(
            agent_llms["perception"],
            agent_llms["research"], 
            agent_llms["analysis"],
            agent_llms["decision"],
            agent_llms["orchestrator"]
        )
        print(f"   ✅ Workflow created successfully: {type(workflow)}")
    except Exception as e:
        print(f"   ❌ Workflow creation failed: {e}")
        return False
    
    # Test cases that match Streamlit app usage
    test_cases = [
        {
            "name": "General skill analysis",
            "question": "What are our Python skill gaps?",
            "project_id": None,
            "scope": "company"
        },
        {
            "name": "Project-specific analysis (like in Streamlit)",
            "question": "Analyze the skill gaps for this specific project and provide structured recommendations.\n\nProject ID: proj_005\nProject Name: Cloud Migration Initiative\nRequired Skills: AWS, Terraform, Kubernetes, Linux, Python\nTimeline: 2024-07-01 to 2025-01-31\nBudget: $900,000\nScope: department",
            "project_id": "proj_005",
            "scope": "department"
        },
        {
            "name": "Empty question handling",
            "question": "",
            "project_id": None,
            "scope": "company"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i+2}: {test_case['name']}")
        print(f"   Question: {test_case['question'][:100]}{'...' if len(test_case['question']) > 100 else ''}")
        print(f"   Project ID: {test_case['project_id']}")
        print(f"   Scope: {test_case['scope']}")
        
        try:
            # Test the workflow.run method (same as in streamlit app)
            result = workflow.run(
                test_case['question'],
                project_id=test_case['project_id'],
                scope=test_case['scope']
            )
            
            if result is None:
                print(f"   ⚠️ Analysis returned None (expected for empty question)")
                results.append(True)
                continue
                
            print(f"   📊 Analysis completed successfully")
            print(f"   🔑 Result keys: {list(result.keys())}")
            
            # Check for required fields that Streamlit app expects
            required_fields = ['intent', 'analysis', 'decision']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
                results.append(False)
            else:
                print(f"   ✅ All required fields present")
                
                # Check analysis quality
                analysis = result.get('analysis', '')
                if analysis and 'Analysis pending' not in analysis and len(analysis) > 100:
                    print(f"   ✅ Analysis contains real data")
                else:
                    print(f"   ⚠️ Analysis contains placeholder data")
                
                # Check decision quality
                decision = result.get('decision', '')
                if decision and 'Decision pending' not in decision and len(decision) > 100:
                    print(f"   ✅ Decision contains real data")
                else:
                    print(f"   ⚠️ Decision contains placeholder data")
                
                # Try to parse analysis and decision as JSON (Streamlit app does this)
                try:
                    analysis_json = json.loads(analysis) if analysis else {}
                    decision_json = json.loads(decision) if decision else {}
                    
                    print(f"   ✅ Analysis JSON valid: {list(analysis_json.keys())}")
                    print(f"   ✅ Decision JSON valid: {list(decision_json.keys())}")
                    
                    # Test specific fields that Streamlit app displays
                    if 'skill_gaps' in analysis_json:
                        print(f"   📊 Skill gaps found: {len(analysis_json['skill_gaps'])}")
                    if 'upskilling' in analysis_json:
                        print(f"   📊 Upskilling recommendations: {len(analysis_json['upskilling'])}")
                    if 'selected_strategy' in decision_json:
                        print(f"   📊 Selected strategy: {decision_json['selected_strategy'].get('strategy_name', 'N/A')}")
                    
                    results.append(True)
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON parsing error: {e}")
                    results.append(False)
                
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Test error handling scenarios that could occur in Streamlit
    print(f"\n🔧 Testing Streamlit Error Handling Scenarios")
    
    # Test with invalid project ID
    try:
        result = workflow.run(
            "Test question",
            project_id="invalid_project_id",
            scope="company"
        )
        print(f"   ✅ Invalid project ID handled gracefully")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Invalid project ID handling failed: {e}")
        results.append(False)
    
    # Test with very long question
    try:
        long_question = "What are our skill gaps? " * 100
        result = workflow.run(long_question, project_id=None, scope="company")
        print(f"   ✅ Long question handled gracefully")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Long question handling failed: {e}")
        results.append(False)
    
    # Test retry mechanism (like in Streamlit app)
    print(f"\n🔧 Testing Retry Mechanism")
    try:
        # Simulate the retry logic from Streamlit app
        try:
            result = workflow.run("Complex question with many details", project_id="proj_005", scope="department")
        except Exception as workflow_error:
            print(f"   ⚠️ First attempt failed: {workflow_error}")
            # Try again with a simpler question (like in Streamlit)
            simple_question = "Analyze skill gaps for project Cloud Migration Initiative requiring skills: AWS, Terraform, Kubernetes"
            result = workflow.run(simple_question, project_id="proj_005", scope="department")
            print(f"   ✅ Retry with simpler question succeeded")
        
        results.append(True)
    except Exception as e:
        print(f"   ❌ Retry mechanism failed: {e}")
        results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Streamlit Workflow Test Results:")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")
    print(f"   📈 Success Rate: {passed/total*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    test_streamlit_workflow()
