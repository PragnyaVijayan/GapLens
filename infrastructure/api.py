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
# Additional Analysis Endpoints (if needed in the future)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
