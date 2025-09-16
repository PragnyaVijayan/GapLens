"""
Pydantic schemas for agent outputs validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal, Union
from enum import Enum


class IntentType(str, Enum):
    """Valid intent types for perception agent"""
    SKILL_GAP_ANALYSIS = "skill_gap_analysis"
    TEAM_OPTIMIZATION = "team_optimization"
    UPSKILLING_PLAN = "upskilling_plan"
    PROJECT_READINESS = "project_readiness"

class UrgencyLevel(str, Enum):
    """Valid urgency levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScopeType(str, Enum):
    """Valid scope types"""
    DEPARTMENT = "department"
    TEAM = "team"
    COMPANY = "company"
    PROJECT = "project"


class ConfidenceLevel(str, Enum):
    """Valid confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AvailabilityType(str, Enum):
    """Valid availability types"""
    IMMEDIATE = "immediate"
    TWO_WEEKS = "2_weeks"
    ONE_MONTH = "1_month"


class UrgencyType(str, Enum):
    """Valid urgency types for hiring"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class StrategyType(str, Enum):
    """Valid strategy types"""
    UPSKILL = "upskill"
    TRANSFER = "transfer"
    HIRE = "hire"
    MIXED = "mixed"


class CostLevel(str, Enum):
    """Valid cost levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    """Valid risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SuccessProbability(str, Enum):
    """Valid success probability levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Perception Agent Schemas
class PerceptionEntities(BaseModel):
    """Entities extracted from user input"""
    skills: List[str] = Field(default_factory=list, description="List of skills mentioned")
    projects: List[str] = Field(default_factory=list, description="List of projects mentioned")
    teams: List[str] = Field(default_factory=list, description="List of teams mentioned")
    people: List[str] = Field(default_factory=list, description="List of people mentioned")
    timelines: List[str] = Field(default_factory=list, description="List of timelines mentioned")


class PerceptionContext(BaseModel):
    """Context information from user input"""
    constraints: List[str] = Field(default_factory=list, description="List of constraints")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM, description="Urgency level")
    scope: ScopeType = Field(default=ScopeType.COMPANY, description="Scope of analysis")


class PerceptionOutput(BaseModel):
    """Perception agent output schema"""
    intent: IntentType = Field(description="Detected intent from user input")
    entities: PerceptionEntities = Field(description="Extracted entities")
    normalized_question: str = Field(description="Normalized user question")
    context: PerceptionContext = Field(description="Context information")
    analysis_focus: str = Field(description="Specific aspect to analyze")

    @validator('normalized_question')
    def validate_normalized_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Normalized question cannot be empty")
        return v.strip()

    @validator('analysis_focus')
    def validate_analysis_focus(cls, v):
        if not v or not v.strip():
            raise ValueError("Analysis focus cannot be empty")
        return v.strip()


# Analysis Agent Schemas
class UpskillingRecommendation(BaseModel):
    """Upskilling recommendation schema"""
    employee: str = Field(description="Full name of employee")
    skill_to_learn: str = Field(description="Skill to learn")
    timeline_weeks: int = Field(ge=1, le=104, description="Timeline in weeks (1-104)")
    confidence: ConfidenceLevel = Field(description="Confidence level")
    reason: str = Field(description="Brief reason for recommendation")

    @validator('employee')
    def validate_employee_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee name cannot be empty")
        return v.strip()

    @validator('skill_to_learn')
    def validate_skill(cls, v):
        if not v or not v.strip():
            raise ValueError("Skill to learn cannot be empty")
        return v.strip()


class InternalTransferRecommendation(BaseModel):
    """Internal transfer recommendation schema"""
    employee: str = Field(description="Full name of employee")
    current_team: str = Field(description="Current team name")
    skills_brought: List[str] = Field(description="Skills this employee brings")
    availability: AvailabilityType = Field(description="Availability timeline")
    reason: str = Field(description="Brief reason for transfer")

    @validator('employee')
    def validate_employee_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee name cannot be empty")
        return v.strip()

    @validator('current_team')
    def validate_team_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Current team name cannot be empty")
        return v.strip()


class HiringRecommendation(BaseModel):
    """Hiring recommendation schema"""
    role: str = Field(description="Job title/role")
    required_skills: List[str] = Field(description="Required skills for the role")
    urgency: UrgencyType = Field(description="Hiring urgency")
    estimated_cost: str = Field(description="Salary range estimate")

    @validator('role')
    def validate_role(cls, v):
        if not v or not v.strip():
            raise ValueError("Role cannot be empty")
        return v.strip()

    @validator('estimated_cost')
    def validate_cost(cls, v):
        if not v or not v.strip():
            raise ValueError("Estimated cost cannot be empty")
        return v.strip()


class AnalysisOutput(BaseModel):
    """Analysis agent output schema"""
    skill_gaps: List[str] = Field(default_factory=list, description="List of identified skill gaps")
    upskilling: List[UpskillingRecommendation] = Field(default_factory=list, description="Upskilling recommendations")
    internal_transfers: List[InternalTransferRecommendation] = Field(default_factory=list, description="Internal transfer recommendations")
    hiring: List[HiringRecommendation] = Field(default_factory=list, description="Hiring recommendations")
    timeline_assessment: str = Field(description="Brief timeline analysis")
    risk_factors: List[str] = Field(default_factory=list, description="List of risk factors")
    success_probability: SuccessProbability = Field(description="Overall success probability")

    @validator('timeline_assessment')
    def validate_timeline_assessment(cls, v):
        if not v or not v.strip():
            raise ValueError("Timeline assessment cannot be empty")
        return v.strip()


# Decision Agent Schemas - Enhanced for more flexible recommendations
class SelectedStrategy(BaseModel):
    """Selected strategy schema - more flexible"""
    strategy_name: str = Field(description="Name of the selected strategy")
    strategy_type: StrategyType = Field(description="Type of strategy")
    confidence: ConfidenceLevel = Field(description="Confidence in strategy selection")
    rationale: str = Field(description="Why this strategy was selected")
    
    # Optional fields for more detailed recommendations
    specific_people: Optional[List[str]] = Field(default=None, description="Specific people involved")
    specific_skills: Optional[List[str]] = Field(default=None, description="Specific skills involved")
    comparison_details: Optional[str] = Field(default=None, description="Comparison between options")
    experience_years: Optional[Dict[str, int]] = Field(default=None, description="Years of experience for people")

    @validator('strategy_name')
    def validate_strategy_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Strategy name cannot be empty")
        return v.strip()

    @validator('rationale')
    def validate_rationale(cls, v):
        if not v or not v.strip():
            raise ValueError("Rationale cannot be empty")
        return v.strip()


class StrategyDetails(BaseModel):
    """Strategy details schema - more flexible"""
    primary_action: str = Field(description="Main action to take")
    target_skill: Optional[str] = Field(default=None, description="Skill to focus on")
    timeline_weeks: Optional[int] = Field(default=None, ge=1, le=104, description="Timeline in weeks")
    success_probability: Optional[SuccessProbability] = Field(default=None, description="Success probability")
    cost_estimate: Optional[CostLevel] = Field(default=None, description="Cost estimate")
    risk_level: Optional[RiskLevel] = Field(default=None, description="Risk level")
    
    # Additional flexible fields
    specific_recommendations: Optional[List[str]] = Field(default=None, description="Specific recommendations")
    why_not_alternatives: Optional[List[str]] = Field(default=None, description="Why other options were not chosen")
    immediate_actions: Optional[List[str]] = Field(default=None, description="Immediate actions to take")

    @validator('primary_action')
    def validate_primary_action(cls, v):
        if not v or not v.strip():
            raise ValueError("Primary action cannot be empty")
        return v.strip()


class ImplementationPlan(BaseModel):
    """Implementation plan schema - more flexible"""
    primary_owner: Optional[str] = Field(default=None, description="Primary owner of the plan")
    support_team: Optional[List[str]] = Field(default=None, description="Support team members")
    timeline_weeks: Optional[int] = Field(default=None, ge=1, le=104, description="Implementation timeline in weeks")
    key_milestones: Optional[List[str]] = Field(default=None, description="Key milestones")
    success_metrics: Optional[List[str]] = Field(default=None, description="Success metrics")
    budget_estimate: Optional[str] = Field(default=None, description="Budget estimate")
    resource_requirements: Optional[List[str]] = Field(default=None, description="Resource requirements")
    
    # Additional flexible fields
    team_assignments: Optional[Dict[str, str]] = Field(default=None, description="Specific team assignments")
    skill_development_plan: Optional[Dict[str, str]] = Field(default=None, description="Skill development plan for individuals")
    project_phases: Optional[List[Dict[str, Any]]] = Field(default=None, description="Detailed project phases")

    @validator('primary_owner')
    def validate_primary_owner(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Primary owner cannot be empty if provided")
        return v.strip() if v else v

    @validator('budget_estimate')
    def validate_budget_estimate(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Budget estimate cannot be empty if provided")
        return v.strip() if v else v


class RiskMitigation(BaseModel):
    """Risk mitigation schema - more flexible"""
    primary_risks: Optional[List[str]] = Field(default=None, description="Primary risks identified")
    mitigation_strategies: Optional[List[str]] = Field(default=None, description="Mitigation strategies")
    contingency_plan: Optional[str] = Field(default=None, description="Brief contingency plan")
    monitoring_points: Optional[List[str]] = Field(default=None, description="Monitoring points")
    
    # Additional flexible fields
    risk_impact_assessment: Optional[Dict[str, str]] = Field(default=None, description="Risk impact assessment")
    early_warning_signs: Optional[List[str]] = Field(default=None, description="Early warning signs to watch for")
    escalation_path: Optional[Dict[str, str]] = Field(default=None, description="Escalation path for different risk levels")

    @validator('contingency_plan')
    def validate_contingency_plan(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Contingency plan cannot be empty if provided")
        return v.strip() if v else v


class ReviewSchedule(BaseModel):
    """Review schedule schema - more flexible"""
    next_review_date: Optional[str] = Field(default=None, description="Next review date")
    review_frequency: Optional[str] = Field(default=None, description="Review frequency")
    success_criteria: Optional[List[str]] = Field(default=None, description="Success criteria")
    
    # Additional flexible fields
    check_in_schedule: Optional[Dict[str, str]] = Field(default=None, description="Regular check-in schedule")
    progress_indicators: Optional[List[str]] = Field(default=None, description="Progress indicators to track")
    decision_points: Optional[List[Dict[str, Any]]] = Field(default=None, description="Key decision points and criteria")

    @validator('next_review_date')
    def validate_next_review_date(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Next review date cannot be empty if provided")
        return v.strip() if v else v

    @validator('review_frequency')
    def validate_review_frequency(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Review frequency cannot be empty if provided")
        return v.strip() if v else v


class AlternativeStrategy(BaseModel):
    """Alternative strategy schema"""
    strategy_name: str = Field(description="Alternative strategy name")
    approach: str = Field(description="Brief description of approach")
    selection_reason: str = Field(description="Why this strategy was not selected")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")

    @validator('strategy_name')
    def validate_strategy_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Strategy name cannot be empty")
        return v.strip()

    @validator('approach')
    def validate_approach(cls, v):
        if not v or not v.strip():
            raise ValueError("Approach cannot be empty")
        return v.strip()

    @validator('selection_reason')
    def validate_selection_reason(cls, v):
        if not v or not v.strip():
            raise ValueError("Selection reason cannot be empty")
        return v.strip()


class DecisionOutput(BaseModel):
    """Decision agent output schema - enhanced for flexible recommendations"""
    natural_language_summary: str = Field(description="Comprehensive recommendation summary")
    selected_strategy: SelectedStrategy = Field(description="Selected strategy details")
    strategy_details: StrategyDetails = Field(description="Strategy implementation details")
    implementation_plan: Optional[ImplementationPlan] = Field(default=None, description="Implementation plan")
    risk_mitigation: Optional[RiskMitigation] = Field(default=None, description="Risk mitigation plan")
    review_schedule: Optional[ReviewSchedule] = Field(default=None, description="Review schedule")
    alternative_strategies: Optional[List[AlternativeStrategy]] = Field(default=None, description="Alternative strategies")
    
    # Additional flexible fields for detailed recommendations
    specific_people_recommendations: Optional[Dict[str, str]] = Field(default=None, description="Specific people and their roles")
    skill_comparisons: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, description="Detailed skill comparisons between people")
    project_impact: Optional[Dict[str, str]] = Field(default=None, description="Impact on different projects/teams")
    timeline_breakdown: Optional[Dict[str, str]] = Field(default=None, description="Detailed timeline breakdown")
    resource_allocation: Optional[Dict[str, Any]] = Field(default=None, description="Resource allocation details")
    success_factors: Optional[List[str]] = Field(default=None, description="Key success factors")
    potential_obstacles: Optional[List[str]] = Field(default=None, description="Potential obstacles and solutions")

    @validator('natural_language_summary')
    def validate_summary(cls, v):
        if not v or not v.strip():
            raise ValueError("Natural language summary cannot be empty")
        return v.strip()


# Orchestrator Agent Schemas
class WorkflowState(BaseModel):
    """Workflow state schema"""
    intent: Optional[str] = Field(default=None, description="Detected intent")
    entities: Optional[Dict[str, Any]] = Field(default=None, description="Extracted entities")
    analysis: Optional[str] = Field(default=None, description="Analysis result")
    decision: Optional[str] = Field(default=None, description="Decision result")
    normalized_question: Optional[str] = Field(default=None, description="Normalized question")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context information")
    perception_output: Optional[Dict[str, Any]] = Field(default=None, description="Perception output")
    workflow_status: Optional[str] = Field(default=None, description="Workflow status")


class WorkflowValidation(BaseModel):
    """Workflow validation schema"""
    perception_complete: bool = Field(description="Whether perception is complete")
    analysis_complete: bool = Field(description="Whether analysis is complete")
    decision_complete: bool = Field(description="Whether decision is complete")
    workflow_complete: bool = Field(description="Whether workflow is complete")
    missing_components: List[str] = Field(description="Missing workflow components")


# Utility functions for validation
def validate_perception_output(data: Dict[str, Any]) -> PerceptionOutput:
    """Validate perception agent output"""
    return PerceptionOutput(**data)


def validate_analysis_output(data: Dict[str, Any]) -> AnalysisOutput:
    """Validate analysis agent output"""
    return AnalysisOutput(**data)


def validate_decision_output(data: Dict[str, Any]) -> DecisionOutput:
    """Validate decision agent output"""
    return DecisionOutput(**data)


def validate_workflow_state(data: Dict[str, Any]) -> WorkflowState:
    """Validate workflow state"""
    return WorkflowState(**data)


def validate_workflow_validation(data: Dict[str, Any]) -> WorkflowValidation:
    """Validate workflow validation result"""
    return WorkflowValidation(**data)
