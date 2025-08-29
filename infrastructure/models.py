"""
Data models for the GapLens Skills Analysis System
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class Skill(BaseModel):
    """Skill model with proficiency level and experience."""
    name: str
    level: str  # beginner, intermediate, advanced, expert
    years_experience: float
    last_used: Optional[date]

class Employee(BaseModel):
    """Employee model with skills and availability."""
    id: str
    name: str
    role: str
    department: str
    skills: List[Skill]
    experience_years: float
    availability: str  # full-time, part-time, available, unavailable
    location: str
    salary_range: str
    upskilling_capacity: str  # high, medium, low

class Project(BaseModel):
    """Project model with requirements and constraints."""
    id: str
    name: str
    description: str
    start_date: date
    end_date: date
    required_skills: List[str]
    team_size: int
    budget: float
    priority: str  # high, medium, low
    status: str  # planning, active, completed, cancelled

class Team(BaseModel):
    """Team model with composition and skills coverage."""
    id: str
    name: str
    department: str
    members: List[str]  # employee IDs
    manager_id: str
    skills_coverage: Dict[str, int]  # skill -> number of people with that skill

class SkillGapAnalysis(BaseModel):
    """Skill gap analysis result."""
    project_id: str
    required_skills: List[str]
    team_skills: List[str]
    skill_gaps: List[str]
    coverage_percentage: float
    recommendations: List[Dict[str, Any]]

class WorkflowResult(BaseModel):
    """Multi-agent workflow result."""
    question: str
    intent: str
    entities: List[str]
    research_facts: List[str]
    analysis: str
    decision: str
    session_id: str
