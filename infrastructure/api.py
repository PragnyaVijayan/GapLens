"""
FastAPI application for GapLens Skills Analysis System
Provides endpoints for accessing project, team, and skills data
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json
import os
import sys

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the new organized mock data and models
from infrastructure.mock_data import mock_data, mock_employees, mock_projects, mock_teams, mock_skill_market_data
from infrastructure.models import Skill, Employee, Project, Team, SkillGapAnalysis, WorkflowResult

app = FastAPI(
    title="GapLens Skills Analysis API",
    description="API for accessing project requirements, team skills, and employee data",
    version="1.0.0"
)

# ============================================================================
# Basic Data Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "GapLens Skills Analysis API",
        "version": "1.0.0",
        "endpoints": [
            "/api/employees",
            "/api/projects", 
            "/api/teams",
            "/api/skills/market-data",
            "/api/analysis/skill-gaps",
            "/api/analysis/ai-reasoning"
        ]
    }

@app.get("/api/employees")
async def get_employees():
    """Get all employees."""
    return mock_employees

@app.get("/api/employees/skills")
async def get_employee_skills():
    """Get employee skills data."""
    return {
        "employees": mock_employees,
        "total_employees": len(mock_employees),
        "total_skills": sum(len(emp["skills"]) for emp in mock_employees),
        "unique_skills": list(set(skill["name"] for emp in mock_employees for skill in emp["skills"]))
    }

@app.get("/api/employees/departments")
async def get_employees_by_department():
    """Get employees grouped by department."""
    departments = {}
    
    for emp in mock_employees:
        dept = emp["department"]
        if dept not in departments:
            departments[dept] = {
                "count": 0,
                "total_experience": 0,
                "roles": set(),
                "skills": set(),
                "experience_levels": {"junior": 0, "mid": 0, "senior": 0},
                "total_salary": 0
            }
        
        departments[dept]["count"] += 1
        departments[dept]["total_experience"] += emp["experience_years"]
        departments[dept]["roles"].add(emp["role"])
        
        for skill in emp["skills"]:
            departments[dept]["skills"].add(skill["name"])
        
        # Categorize by experience level
        if emp["experience_years"] < 3:
            departments[dept]["experience_levels"]["junior"] += 1
        elif emp["experience_years"] < 6:
            departments[dept]["experience_levels"]["mid"] += 1
        else:
            departments[dept]["experience_levels"]["senior"] += 1
        
        # Calculate salary (convert range to average)
        salary_range = emp["salary_range"]
        if "-" in salary_range:
            min_sal, max_sal = salary_range.replace("$", "").replace("k", "").split("-")
            avg_sal = (int(min_sal) + int(max_sal)) / 2
        else:
            avg_sal = 100  # Default if parsing fails
        
        departments[dept]["total_salary"] += avg_sal
    
    # Calculate averages and convert sets to lists
    for dept in departments:
        if departments[dept]["count"] > 0:
            departments[dept]["avg_salary"] = round(departments[dept]["total_salary"] / departments[dept]["count"], 2)
        departments[dept]["roles"] = list(departments[dept]["roles"])
        departments[dept]["skills"] = list(departments[dept]["skills"])
    
    return {
        "departments": departments,
        "total_employees": len(mock_employees),
        "total_departments": len(departments)
    }

@app.get("/api/projects")
async def get_projects():
    """Get all projects."""
    return mock_projects

@app.get("/api/projects/{project_id}")
async def get_project_by_id(project_id: str):
    """Get a specific project by ID."""
    project = next((proj for proj in mock_projects if proj["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/api/projects/summary")
async def get_projects_summary():
    """Get projects summary with skills analysis."""
    return {
        "projects": mock_projects,
        "total_projects": len(mock_projects),
        "skills_needed": list(set(skill for proj in mock_projects for skill in proj["required_skills"]))
    }

@app.get("/api/teams")
async def get_teams():
    """Get all teams."""
    return mock_teams

@app.get("/api/teams/summary")
async def get_teams_summary():
    """Get teams summary with skills distribution."""
    return {
        "teams": mock_teams,
        "total_teams": len(mock_teams),
        "skill_distribution": {team["name"]: team["skills_coverage"] for team in mock_teams}
    }

@app.get("/api/teams/composition")
async def get_team_composition():
    """Get detailed team composition."""
    team_composition = []
    
    for team in mock_teams:
        team_members = []
        for emp_id in team["members"]:
            emp = next((emp for emp in mock_employees if emp["id"] == emp_id), None)
            if emp:
                team_members.append({
                    "id": emp["id"],
                    "name": emp["name"],
                    "role": emp["role"],
                    "skills": emp["skills"],
                    "experience_years": emp["experience_years"]
                })
        
        team_composition.append({
            "team_id": team["id"],
            "team_name": team["name"],
            "department": team["department"],
            "members": team_members,
            "skills_coverage": team["skills_coverage"]
        })
    
    return team_composition

@app.get("/api/skills/market-data")
async def get_skill_market_data():
    """Get skill market data and trends."""
    return mock_skill_market_data

@app.get("/api/analysis/project/{project_id}/skill-gaps")
async def analyze_project_skill_gaps(project_id: str):
    """Analyze skill gaps for a specific project."""
    # Find the project
    project = next((proj for proj in mock_projects if proj["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get project team (simulate team assignment based on project type)
    project_team = []
    if project["name"] == "Salesforce CRM Implementation":
        # Sales team + some engineering support
        project_team = [emp for emp in mock_employees if emp["department"] in ["Sales", "Engineering"]]
    elif project["name"] == "Data Pipeline Optimization":
        # Data Science team
        project_team = [emp for emp in mock_employees if emp["department"] == "Data Science"]
    elif project["name"] == "Mobile App for Field Sales":
        # Engineering team with mobile experience
        project_team = [emp for emp in mock_employees if emp["department"] == "Engineering"]
    elif project["name"] == "AI-Powered Customer Support":
        # Data Science + Engineering
        project_team = [emp for emp in mock_employees if emp["department"] in ["Data Science", "Engineering"]]
    else:
        # Default: get employees from any department
        project_team = mock_employees
    
    # Analyze skill gaps
    required_skills = set(project["required_skills"])
    available_skills = set()
    for emp in project_team:
        for skill in emp["skills"]:
            available_skills.add(skill["name"])
    
    missing_skills = required_skills - available_skills
    covered_skills = required_skills & available_skills
    
    return {
        "project": project,
        "project_team": project_team,
        "required_skills": list(required_skills),
        "available_skills": list(available_skills),
        "missing_skills": list(missing_skills),
        "covered_skills": list(covered_skills),
        "coverage_percentage": len(covered_skills) / len(required_skills) * 100 if required_skills else 0
    }

# ============================================================================
# Analysis Endpoints
# ============================================================================

# @app.get("/api/analysis/skill-gaps")
# async def analyze_skill_gaps(project_id: str):
#     """Analyze skill gaps for a specific project."""
#     # Find the project
#     project = None
#     for proj in mock_projects:
#         if proj["id"] == project_id:
#             project = proj
#             break
    
#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")
    
#     # Get project team (simulate team assignment)
#     project_team = []
#     if project["name"] == "Salesforce CRM Implementation":
#         # Sales team + some engineering support
#         project_team = [emp for emp in mock_employees if emp["department"] in ["Sales", "Engineering"]]
#     elif project["name"] == "Data Pipeline Optimization":
#         # Data Science team
#         project_team = [emp for emp in mock_employees if emp["department"] == "Data Science"]
#     elif project["name"] == "Mobile App for Field Sales":
#         # Engineering team with mobile experience
#         project_team = [emp for emp in mock_employees if emp["department"] == "Engineering"]
#     elif project["name"] == "AI-Powered Customer Support":
#         # Data Science + Engineering
#         project_team = [emp for emp in mock_employees if emp["department"] in ["Data Science", "Engineering"]]
#     else:
#         # Default: Engineering team
#         project_team = [emp for emp in mock_employees if emp["department"] == "Engineering"]
    
#     # Get team skills
#     team_skills = set()
#     for emp in project_team:
#         for skill in emp["skills"]:
#             team_skills.add(skill["name"])
    
#     required_skills = set(project["required_skills"])
#     skill_gaps = required_skills - team_skills
    
#     # Generate recommendations
#     recommendations = []
    
#     if skill_gaps:
#         # Upskill recommendations
#         for skill in skill_gaps:
#             if any(emp["upskilling_capacity"] == "high" for emp in project_team):
#                 recommendations.append({
#                     "type": "upskill",
#                     "skill": skill,
#                     "priority": "high",
#                     "reason": "Team has high upskilling capacity",
#                     "estimated_cost": 25000,
#                     "timeline": "4-6 weeks",
#                     "risk": "low"
#                 })
        
#         # Transfer recommendations
#         for skill in skill_gaps:
#             if any(emp["department"] != project_team[0]["department"] and skill in [s["name"] for s in emp["skills"]] for emp in mock_employees):
#                 recommendations.append({
#                     "type": "transfer",
#                     "skill": skill,
#                     "priority": "medium",
#                     "reason": "Skill available in other departments",
#                     "estimated_cost": 15000,
#                     "timeline": "2-3 weeks",
#                     "risk": "medium"
#                 })
        
#         # Hiring recommendations for remaining gaps
#         remaining_gaps = skill_gaps - {rec["skill"] for rec in recommendations if rec["type"] in ["upskill", "transfer"]}
#         for skill in remaining_gaps:
#             recommendations.append({
#                 "type": "hire",
#                 "skill": skill,
#                 "priority": "high",
#                 "reason": "Critical skill gap requiring external hire",
#                 "estimated_cost": 120000,
#                 "timeline": "8-12 weeks",
#                 "risk": "low"
#             })
    
#     return {
#         "project": project,
#         "team_analysis": {
#             "team_size": len(project_team),
#             "departments": list(set(emp["department"] for emp in project_team)),
#             "team_skills": list(team_skills),
#             "required_skills": list(required_skills),
#             "skill_gaps": list(skill_gaps),
#             "coverage_percentage": round((len(team_skills.intersection(required_skills)) / len(required_skills)) * 100, 2)
#         },
#         "recommendations": recommendations,
#         "analysis_summary": {
#             "total_recommendations": len(recommendations),
#             "upskill_count": len([r for r in recommendations if r["type"] == "upskill"]),
#             "transfer_count": len([r for r in recommendations if r["type"] == "transfer"]),
#             "hire_count": len([r for r in recommendations if r["type"] == "hire"])
#         }
#     }

# @app.get("/api/analysis/ai-reasoning")
# async def get_ai_reasoning_analysis(project_id: str, scope: str = "department"):
#     """
#     Get AI reasoning analysis for a project using the multi-agent workflow.
#     scope: 'department' (only team/department skills) or 'company' (all company skills)
#     """
#     # Find the project
#     project = None
#     for proj in mock_projects:
#         if proj["id"] == project_id:
#             project = proj
#             break
    
#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")
    
#     # Get project team (simulate team assignment)
#     project_team = []
#     if project["name"] == "Salesforce CRM Implementation":
#         # Sales team + some engineering support
#         project_team = [emp for emp in mock_employees if emp["department"] in ["Sales", "Engineering"]]
#     elif project["name"] == "Data Pipeline Optimization":
#         # Data Science team
#         project_team = [emp for emp in mock_employees if emp["department"] == "Data Science"]
#     elif project["name"] == "Mobile App for Field Sales":
#         # Engineering team with mobile experience
#         project_team = [emp for emp in mock_employees if emp["department"] == "Engineering"]
#     elif project["name"] == "AI-Powered Customer Support":
#         # Data Science + Engineering
#         project_team = [emp for emp in mock_employees if emp["department"] in ["Data Science", "Engineering"]]
#     else:
#         # Default: Engineering team
#         project_team = [emp for emp in mock_employees if emp["department"] == "Engineering"]
    
#     # Limit scope if requested
#     if scope == "department":
#         # Use only the primary department for the project
#         primary_dept = project_team[0]["department"] if project_team else "Engineering"
#         project_team = [emp for emp in project_team if emp["department"] == primary_dept]
    
#     # Get team skills
#     team_skills = set()
#     for emp in project_team:
#         for skill in emp["skills"]:
#             team_skills.add(skill["name"])
    
#     required_skills = set(project["required_skills"])
#     skill_gaps = required_skills - team_skills
    
#     # Create a comprehensive question for the multi-agent workflow
#     workflow_question = f"""
#     Analyze the skills gap for project: {project['name']}
    
#     Project Details:
#     - Required Skills: {', '.join(required_skills)}
#     - Team Size: {len(project_team)} members
#     - Team Departments: {', '.join(set(emp['department'] for emp in project_team))}
#     - Current Team Skills: {', '.join(team_skills)}
#     - Identified Skill Gaps: {', '.join(skill_gaps) if skill_gaps else 'None'}
    
#     Please provide:
#     1. Analysis of current team capabilities vs project requirements
#     2. Specific recommendations for upskilling, transfers, or hiring
#     3. Risk assessment and timeline estimates
#     4. Implementation steps and success metrics
#     """
    
#     try:
#         # Import the workflow system
#         from core.workflow import MultiAgentWorkflow
#         from core import make_llm, make_reasoner
        
#         # Try to use real LLM first, fallback to fake if it fails
#         try:
#             perception_llm = make_llm("anthropic")
#             reasoner_llm = make_reasoner("anthropic")
#             print(f"✅ Using real Anthropic LLM for project: {project['name']}")
#         except Exception as llm_error:
#             print(f"⚠️  Real LLM failed, falling back to fake LLM: {llm_error}")
#             perception_llm = make_llm("fake")
#             reasoner_llm = make_reasoner("fake")
        
#         # Create and run workflow
#         workflow = MultiAgentWorkflow(perception_llm, reasoner_llm)
#         print(f"🚀 Running multi-agent workflow for project: {project['name']}")
#         result = workflow.run(workflow_question, verbose=False)
        
#         # Extract the real agent outputs
#         reasoning_steps = []
        
#         # Step 1: Perception Agent output
#         if result.get("intent"):
#             reasoning_steps.append({
#                 "step": 1,
#                 "agent": "Perception Agent",
#                 "action": "Extracted project intent and requirements",
#                 "details": f"Intent: {result['intent']}, Entities: {', '.join(result.get('entities', []))}",
#                 "agent_output": result.get("normalized_question", workflow_question)
#             })
        
#         # Step 2: Research Agent output
#         if result.get("research_facts"):
#             reasoning_steps.append({
#                 "step": 2,
#                 "agent": "Research Agent",
#                 "action": "Gathered project and team data",
#                 "details": f"Found {len(result['research_facts'])} research facts",
#                 "agent_output": result["research_facts"]
#             })
        
#         # Step 3: Analysis Agent output
#         if result.get("analysis"):
#             reasoning_steps.append({
#                 "step": 3,
#                 "agent": "Analysis Agent",
#                 "action": "Analyzed skill gaps and generated recommendations",
#                 "details": "Completed comprehensive skills analysis",
#                 "agent_output": result["analysis"]
#             })
        
#         # Step 4: Decision Agent output
#         if result.get("decision"):
#             reasoning_steps.append({
#                 "step": 4,
#                 "agent": "Decision Agent",
#                 "action": "Made final actionable recommendations",
#                 "details": "Generated strategic implementation plan",
#                 "agent_output": result["decision"]
#             })
        
#         # Parse the decision output to extract structured recommendations
#         recommendations = []
#         decision_text = result.get("decision", "")
        
#         # Try to extract structured information from the decision output
#         if "upskill" in decision_text.lower():
#             recommendations.append({
#                 "type": "upskill",
#                 "priority": "high",
#                 "reason": "Identified by AI analysis",
#                 "details": "AI agent recommended upskilling existing team members",
#                 "agent_output": decision_text,
#                 "estimated_cost": 50000,
#                 "timeline": "4-6 weeks",
#                 "risk": "low",
#                 "success_probability": 0.8
#             })
        
#         if "transfer" in decision_text.lower():
#             recommendations.append({
#                 "type": "transfer",
#                 "priority": "medium",
#                 "reason": "Identified by AI analysis",
#                 "details": "AI agent recommended internal transfers",
#                 "agent_output": decision_text,
#                 "estimated_cost": 25000,
#                 "timeline": "3-4 weeks",
#                 "risk": "medium",
#                 "success_probability": 0.7
#             })
        
#         if "hire" in decision_text.lower() or "recruit" in decision_text.lower():
#             recommendations.append({
#                 "type": "hire",
#                 "priority": "high",
#                 "reason": "Identified by AI analysis",
#                 "details": "AI agent recommended external hiring",
#                 "agent_output": decision_text,
#                 "estimated_cost": 150000,
#                 "timeline": "8-10 weeks",
#                 "risk": "low",
#                 "success_probability": 0.9
#             })
        
#         # If no specific recommendations found, create a general one based on the analysis
#         if not recommendations and result.get("analysis"):
#             recommendations.append({
#                 "type": "ai_analysis",
#                 "priority": "medium",
#                 "reason": "AI-generated comprehensive analysis",
#                 "details": "Multi-agent workflow provided detailed skills gap analysis",
#                 "agent_output": result["analysis"],
#                 "estimated_cost": 75000,
#                 "timeline": "6-8 weeks",
#                 "risk": "medium",
#                 "success_probability": 0.75
#             })
        
#         # If still no recommendations, create a basic one
#         if not recommendations:
#             recommendations.append({
#                 "type": "basic_analysis",
#                 "priority": "medium",
#                 "reason": "Basic skills gap analysis",
#                 "details": "Identified skill gaps and provided basic recommendations",
#                 "agent_output": f"Skill gaps identified: {', '.join(skill_gaps) if skill_gaps else 'None'}",
#                 "estimated_cost": 100000,
#                 "timeline": "8-12 weeks",
#                 "risk": "medium",
#                 "success_probability": 0.6
#             })
        
#         return {
#             "project": project,
#             "team_analysis": {
#                 "team_size": len(project_team),
#                 "departments": list(set(emp["department"] for emp in project_team)),
#                 "team_skills": list(team_skills),
#                 "required_skills": list(required_skills),
#                 "skill_gaps": list(skill_gaps),
#                 "coverage_percentage": round((len(team_skills.intersection(required_skills)) / len(required_skills)) * 100, 2)
#             },
#             "reasoning_steps": reasoning_steps,
#             "recommendations": recommendations,
#             "analysis_summary": {
#                 "total_recommendations": len(recommendations),
#                 "upskill_count": len([r for r in recommendations if r["type"] == "upskill"]),
#                 "transfer_count": len([r for r in recommendations if r["type"] == "transfer"]),
#                 "hire_count": len([r for r in recommendations if r["type"] == "hire"]),
#                 "ai_analysis_count": len([r for r in recommendations if r["type"] in ["ai_analysis", "basic_analysis"]])
#             },
#             "workflow_metadata": {
#                 "question_processed": workflow_question,
#                 "agents_executed": [step["agent"] for step in reasoning_steps],
#                 "workflow_success": len(reasoning_steps) >= 3,  # At least perception, research, and analysis
#                 "llm_backend": "anthropic" if "anthropic" in str(type(perception_llm)) else "fake"
#             }
#         }
        
#     except Exception as e:
#         print(f"❌ Error running multi-agent workflow: {e}")
        
#         # Fallback to basic analysis if workflow fails
#         reasoning_steps = [
#             {
#                 "step": 1,
#                 "agent": "System",
#                 "action": "Basic skills gap analysis",
#                 "details": f"Project requires: {', '.join(required_skills)}. Team has: {', '.join(team_skills)}",
#                 "agent_output": "Workflow execution failed, using fallback analysis"
#             }
#         ]
        
#         recommendations = [
#             {
#                 "type": "fallback",
#                 "priority": "medium",
#                 "reason": "Workflow execution failed",
#                 "details": "Using basic skills gap analysis due to workflow error",
#                 "agent_output": f"Error: {str(e)}",
#                 "estimated_cost": 100000,
#                 "timeline": "8-12 weeks",
#                 "risk": "high",
#                 "success_probability": 0.5
#             }
#         ]
        
#         return {
#             "project": project,
#             "team_analysis": {
#                 "team_size": len(project_team),
#                 "departments": list(set(emp["department"] for emp in project_team)),
#                 "team_skills": list(team_skills),
#                 "required_skills": list(required_skills),
#                 "skill_gaps": list(skill_gaps),
#                 "coverage_percentage": round((len(team_skills.intersection(required_skills)) / len(required_skills)) * 100, 2)
#             },
#             "reasoning_steps": reasoning_steps,
#             "recommendations": recommendations,
#             "analysis_summary": {
#                 "total_recommendations": len(recommendations),
#                 "upskill_count": 0,
#                 "transfer_count": 0,
#                 "hire_count": 0,
#                 "fallback_count": len(recommendations)
#             },
#             "workflow_metadata": {
#                 "question_processed": workflow_question,
#                 "agents_executed": ["System"],
#                 "workflow_success": False,
#                 "error": str(e)
#             }
#         }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
