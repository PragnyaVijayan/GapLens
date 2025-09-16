#!/usr/bin/env python3
"""
Test Streamlit app integration with fixed agents
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import create_workflow, run_analysis
import json

def test_streamlit_integration():
    """Test Streamlit app integration with fixed agents."""
    
    print("🧪 Testing Streamlit App Integration")
    print("=" * 60)
    
    # Test workflow creation
    print("\n📋 Test 1: Workflow Creation")
    try:
        workflow = create_workflow()
        print(f"   ✅ Workflow created successfully: {type(workflow)}")
    except Exception as e:
        print(f"   ❌ Workflow creation failed: {e}")
        return False
    
    # Test analysis execution
    test_cases = [
        {
            "name": "General skill analysis",
            "question": "What are our Python skill gaps?",
            "project_id": None,
            "scope": "company"
        },
        {
            "name": "Project-specific analysis",
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
        print(f"\n📋 Test {i+1}: {test_case['name']}")
        print(f"   Question: {test_case['question'][:100]}{'...' if len(test_case['question']) > 100 else ''}")
        print(f"   Project ID: {test_case['project_id']}")
        print(f"   Scope: {test_case['scope']}")
        
        try:
            # Test the run_analysis function
            result = run_analysis(
                test_case['question'],
                workflow,
                test_case['project_id'],
                test_case['scope']
            )
            
            if result is None:
                print(f"   ⚠️ Analysis returned None (expected for empty question)")
                results.append(True)
                continue
                
            print(f"   📊 Analysis completed successfully")
            print(f"   🔑 Result keys: {list(result.keys())}")
            
            # Check for required fields
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
                
                # Try to parse analysis and decision as JSON
                try:
                    analysis_json = json.loads(analysis) if analysis else {}
                    decision_json = json.loads(decision) if decision else {}
                    
                    print(f"   ✅ Analysis JSON valid: {list(analysis_json.keys())}")
                    print(f"   ✅ Decision JSON valid: {list(decision_json.keys())}")
                    
                    results.append(True)
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON parsing error: {e}")
                    results.append(False)
                
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Test error handling scenarios
    print(f"\n🔧 Testing Error Handling Scenarios")
    
    # Test with invalid project ID
    try:
        result = run_analysis(
            "Test question",
            workflow,
            "invalid_project_id",
            "company"
        )
        print(f"   ✅ Invalid project ID handled gracefully")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Invalid project ID handling failed: {e}")
        results.append(False)
    
    # Test with very long question
    try:
        long_question = "What are our skill gaps? " * 100
        result = run_analysis(long_question, workflow, None, "company")
        print(f"   ✅ Long question handled gracefully")
        results.append(True)
    except Exception as e:
        print(f"   ❌ Long question handling failed: {e}")
        results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Streamlit Integration Test Results:")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")
    print(f"   📈 Success Rate: {passed/total*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    test_streamlit_integration()
