#!/usr/bin/env python3
"""
Simple test script to demonstrate GapLens functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import SkillGapOrchestrator
from src.mock_data import get_mock_projects, get_mock_employees


async def test_system():
    """Test the basic system functionality."""
    print("🔍 Testing GapLens System...")
    print("=" * 50)
    
    # Test mock data
    print("\n📊 Testing Mock Data:")
    projects = get_mock_projects()
    employees = get_mock_employees()
    
    print(f"   ✅ Loaded {len(projects)} projects")
    print(f"   ✅ Loaded {len(employees)} employees")
    
    # Show sample project
    if projects:
        project = projects[0]
        print(f"\n📋 Sample Project: {project.name}")
        print(f"   Priority: {project.priority}")
        print(f"   Timeline: {project.start_date.strftime('%Y-%m-%d')} to {project.end_date.strftime('%Y-%m-%d')}")
        print(f"   Description: {project.description[:100]}...")
    
    # Show sample employee
    if employees:
        employee = employees[0]
        print(f"\n👤 Sample Employee: {employee.name}")
        print(f"   Department: {employee.department}")
        print(f"   Skills: {len(employee.skills)} skills")
        print(f"   Expert skills: {[s for s, l in employee.skills.items() if l >= 3]}")    
    # Test orchestrator
    print("\n⚙️ Testing Orchestrator:")
    try:
        orchestrator = SkillGapOrchestrator()
        print("   ✅ Orchestrator initialized")
        
        # Get workflow status
        status = orchestrator.get_workflow_status()
        print(f"   ✅ Workflow status: {status['status']}")
        print(f"   ✅ Total steps: {status['total_steps']}")
        
        # Run workflow
        print("\n🚀 Running Workflow...")
        results = await orchestrator.run_workflow()
        
        if results["success"]:
            print("   ✅ Workflow completed successfully!")
            
            summary = results.get("summary", {})
            if summary:
                final_results = summary.get('final_results', {})
                print(f"   📊 Projects analyzed: {final_results.get('projects_analyzed', 0)}")
                print(f"   📊 Skills extracted: {final_results.get('skills_extracted', 0)}")
                print(f"   📊 Gaps identified: {final_results.get('gaps_identified', 0)}")
                print(f"   📊 Decisions created: {final_results.get('decisions_created', 0)}")
        else:
            print("   ❌ Workflow failed!")
            if results.get("errors"):
                for error in results["errors"]:
                    print(f"      Error: {error}")
        
    except Exception as e:
        print(f"   ❌ Orchestrator error: {e}")
    
    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Start the API server: python main.py api")
    print("   2. Start the UI: python main.py ui")
    print("   3. Open http://localhost:8000/docs for API docs")
    print("   4. Open http://localhost:8501 for Streamlit UI")


if __name__ == "__main__":
    asyncio.run(test_system()) 