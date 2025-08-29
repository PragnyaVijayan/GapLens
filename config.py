"""
Configuration settings for the GapLens Skills Analysis System
"""

import os
from pathlib import Path

# ============================================================================
# LLM Configuration
# ============================================================================
BACKEND = os.getenv("BACKEND", "anthropic").lower()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# ============================================================================
# Display and Output Configuration
# ============================================================================
DEFAULT_DISPLAY_LIMIT = 200
FULL_OUTPUT_DISPLAY_LIMIT = 1000

# LLM Output Configuration
LLM_OUTPUT_VERBOSE = False  # Show detailed LLM reasoning steps
LLM_OUTPUT_SHOW_PATTERNS = False  # Show reasoning patterns used
LLM_OUTPUT_SHOW_RESPONSES = False  # Show LLM responses
LLM_OUTPUT_SHOW_MEMORY = False  # Show memory operations

# Agent Verbosity Control
AGENT_VERBOSE_OUTPUT = False  # Enable for debugging agent behavior
AGENT_SHOW_JSON_VALIDATION = False  # Show JSON validation steps

# ============================================================================
# Memory System Configuration
# ============================================================================
MEMORY_BASE_PATH = Path("infrastructure/memory")
MEMORY_SESSION_RETENTION_DAYS = 30  # How long to keep session files
MEMORY_LOG_RETENTION_MONTHS = 12  # How long to keep log files
MEMORY_AUTO_CLEANUP = True  # Automatically clean up old files
MEMORY_COMPRESSION = False  # Compress memory files (future feature)

# ============================================================================
# API Configuration
# ============================================================================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 10  # seconds

# ============================================================================
# Project and Skills Configuration
# ============================================================================
PROJECT_SKILLS_MAPPING = {
    "web_development": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Python", "Django", "PostgreSQL"],
    "mobile_development": ["React Native", "Flutter", "iOS", "Android", "Swift", "Kotlin", "Java"],
    "data_science": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
    "devops": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Jenkins", "Git"],
    "machine_learning": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "SQL", "AWS"],
    "cybersecurity": ["Network Security", "Penetration Testing", "Cryptography", "Python", "Linux", "Wireshark"],
    "cloud_computing": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Python", "Bash"]
}

# Upskilling time estimates (in weeks)
UPSKILLING_TIME_ESTIMATES = {
    "beginner": 4,      # 0-1 years experience
    "intermediate": 2,   # 1-3 years experience
    "advanced": 1        # 3+ years experience
}

# Risk levels for recommendations
RISK_LEVELS = {
    "low": "Minimal risk, high confidence in success",
    "medium": "Moderate risk, requires careful planning",
    "high": "High risk, consider alternatives or extended timeline"
}

# ============================================================================
# FastAPI Endpoints
# ============================================================================
EXTERNAL_API_ENDPOINTS = {
    "employee_skills": "/api/employees/skills",
    "project_requirements": "/api/projects",
    "team_composition": "/api/teams/composition",
    "skill_market_data": "/api/skills/market-data"
}

# ============================================================================
# Workflow Configuration
# ============================================================================
WORKFLOW_MAX_RETRIES = 3
WORKFLOW_TIMEOUT = 300  # seconds
WORKFLOW_VERBOSE = False

# ============================================================================
# Agent Configuration
# ============================================================================
AGENT_TIMEOUT = 60  # seconds per agent
AGENT_MAX_RETRIES = 2
AGENT_CONFIDENCE_THRESHOLD = 0.7

# ============================================================================
# Development and Testing
# ============================================================================
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
