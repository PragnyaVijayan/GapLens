"""
Mock data for the GapLens Skills Analysis System
"""

from datetime import date
from .models import Employee, Project, Team

# Mock employee data
mock_employees = [
    # Engineering Department - Frontend
    {
        "id": "emp_001",
        "name": "John Smith",
        "role": "Senior Frontend Developer",
        "department": "Engineering",
        "skills": [
            {"name": "React", "level": "expert", "years_experience": 5.0, "last_used": date.today()},
            {"name": "Vue.js", "level": "advanced", "years_experience": 3.0, "last_used": date.today()},
            {"name": "JavaScript", "level": "expert", "years_experience": 6.0, "last_used": date.today()},
            {"name": "TypeScript", "level": "advanced", "years_experience": 4.0, "last_used": date.today()},
            {"name": "HTML", "level": "expert", "years_experience": 7.0, "last_used": date.today()},
            {"name": "CSS", "level": "expert", "years_experience": 6.0, "last_used": date.today()},
            {"name": "Sass", "level": "intermediate", "years_experience": 2.0, "last_used": date.today()}
        ],
        "experience_years": 7.0,
        "availability": "full-time",
        "location": "San Francisco",
        "salary_range": "$120k-$160k",
        "upskilling_capacity": "high"
    },
    {
        "id": "emp_002",
        "name": "Sarah Johnson",
        "role": "Frontend Developer",
        "department": "Engineering",
        "skills": [
            {"name": "React", "level": "intermediate", "years_experience": 2.5, "last_used": date.today()},
            {"name": "JavaScript", "level": "intermediate", "years_experience": 3.0, "last_used": date.today()},
            {"name": "HTML", "level": "advanced", "years_experience": 4.0, "last_used": date.today()},
            {"name": "CSS", "level": "advanced", "years_experience": 4.0, "last_used": date.today()},
            {"name": "Angular", "level": "beginner", "years_experience": 1.0, "last_used": date.today()}
        ],
        "experience_years": 3.0,
        "availability": "full-time",
        "location": "San Francisco",
        "salary_range": "$80k-$110k",
        "upskilling_capacity": "high"
    },
    # Engineering Department - Backend
    {
        "id": "emp_003",
        "name": "Michael Chen",
        "role": "Senior Backend Developer",
        "department": "Engineering",
        "skills": [
            {"name": "Python", "level": "expert", "years_experience": 8.0, "last_used": date.today()},
            {"name": "Django", "level": "expert", "years_experience": 6.0, "last_used": date.today()},
            {"name": "PostgreSQL", "level": "advanced", "years_experience": 5.0, "last_used": date.today()},
            {"name": "Redis", "level": "intermediate", "years_experience": 3.0, "last_used": date.today()},
            {"name": "Docker", "level": "advanced", "years_experience": 4.0, "last_used": date.today()},
            {"name": "AWS", "level": "intermediate", "years_experience": 3.0, "last_used": date.today()}
        ],
        "experience_years": 8.0,
        "availability": "full-time",
        "location": "San Francisco",
        "salary_range": "$130k-$170k",
        "upskilling_capacity": "medium"
    },
    # Data Science Department
    {
        "id": "emp_004",
        "name": "Emily Rodriguez",
        "role": "Data Scientist",
        "department": "Data Science",
        "skills": [
            {"name": "Python", "level": "expert", "years_experience": 5.0, "last_used": date.today()},
            {"name": "Pandas", "level": "expert", "years_experience": 4.0, "last_used": date.today()},
            {"name": "NumPy", "level": "advanced", "years_experience": 4.0, "last_used": date.today()},
            {"name": "Scikit-learn", "level": "advanced", "years_experience": 3.0, "last_used": date.today()},
            {"name": "SQL", "level": "intermediate", "years_experience": 3.0, "last_used": date.today()},
            {"name": "TensorFlow", "level": "intermediate", "years_experience": 2.0, "last_used": date.today()}
        ],
        "experience_years": 5.0,
        "availability": "full-time",
        "location": "San Francisco",
        "salary_range": "$100k-$140k",
        "upskilling_capacity": "high"
    },
    # DevOps Department
    {
        "id": "emp_005",
        "name": "David Kim",
        "role": "DevOps Engineer",
        "department": "DevOps",
        "skills": [
            {"name": "Docker", "level": "expert", "years_experience": 6.0, "last_used": date.today()},
            {"name": "Kubernetes", "level": "advanced", "years_experience": 4.0, "last_used": date.today()},
            {"name": "AWS", "level": "expert", "years_experience": 7.0, "last_used": date.today()},
            {"name": "Terraform", "level": "advanced", "years_experience": 3.0, "last_used": date.today()},
            {"name": "Jenkins", "level": "intermediate", "years_experience": 4.0, "last_used": date.today()},
            {"name": "Linux", "level": "expert", "years_experience": 8.0, "last_used": date.today()}
        ],
        "experience_years": 8.0,
        "availability": "full-time",
        "location": "San Francisco",
        "salary_range": "$120k-$160k",
        "upskilling_capacity": "medium"
    },
    # Mobile Department
    {
        "id": "emp_006",
        "name": "Priya Patel",
        "role": "Mobile App Developer",
        "department": "Mobile",
        "skills": [
            {"name": "React Native", "level": "advanced", "years_experience": 4, "last_used": date.today()},
            {"name": "Swift", "level": "intermediate", "years_experience": 2, "last_used": date.today()},
            {"name": "Kotlin", "level": "intermediate", "years_experience": 2, "last_used": date.today()}
        ],
        "experience_years": 5,
        "availability": "part-time",
        "location": "Austin",
        "salary_range": "$90k-$120k",
        "upskilling_capacity": "medium"
    },
    {
    "id": "emp_007",
    "name": "Ahmed Khan",
    "role": "QA Engineer",
    "department": "Quality Assurance",
    "skills": [
        {"name": "Selenium", "level": "expert", "years_experience": 6, "last_used": date.today()},
        {"name": "Cypress", "level": "advanced", "years_experience": 4, "last_used": date.today()},
        {"name": "Java", "level": "intermediate", "years_experience": 3, "last_used": date.today()}
    ],
    "experience_years": 7,
    "availability": "full-time",
    "location": "Toronto",
    "salary_range": "$85k-$115k",
    "upskilling_capacity": "high"
},
{
    "id": "emp_008",
    "name": "Laura Müller",
    "role": "Security Engineer",
    "department": "Security",
    "skills": [
        {"name": "Cybersecurity", "level": "expert", "years_experience": 8, "last_used": date.today()},
        {"name": "AWS", "level": "advanced", "years_experience": 5, "last_used": date.today()},
        {"name": "Python", "level": "intermediate", "years_experience": 3, "last_used": date.today()}
    ],
    "experience_years": 8,
    "availability": "full-time",
    "location": "Berlin",
    "salary_range": "$110k-$145k",
    "upskilling_capacity": "medium"
},
{
    "id": "emp_009",
    "name": "Carlos Diaz",
    "role": "Product Manager",
    "department": "Product",
    "skills": [
        {"name": "Agile", "level": "expert", "years_experience": 7, "last_used": date.today()},
        {"name": "JIRA", "level": "advanced", "years_experience": 5, "last_used": date.today()},
        {"name": "Stakeholder Management", "level": "expert", "years_experience": 6, "last_used": date.today()}
    ],
    "experience_years": 9,
    "availability": "full-time",
    "location": "New York",
    "salary_range": "$130k-$160k",
    "upskilling_capacity": "low"
}

]

# Mock project data
mock_projects = [
    {
        "id": "proj_001",
        "name": "Salesforce CRM Implementation",
        "description": "Implement Salesforce CRM for sales team",
        "start_date": date(2024, 3, 1),
        "end_date": date(2024, 8, 31),
        "required_skills": ["Salesforce", "Apex", "Lightning", "JavaScript", "SQL"],
        "team_size": 4,
        "budget": 500000,
        "priority": "high",
        "status": "planning"
    },
    {
        "id": "proj_002",
        "name": "Data Pipeline Optimization",
        "description": "Optimize data processing pipeline for analytics",
        "start_date": date(2024, 4, 1),
        "end_date": date(2024, 9, 30),
        "required_skills": ["Python", "Apache Spark", "Kafka", "PostgreSQL", "Docker"],
        "team_size": 3,
        "budget": 300000,
        "priority": "medium",
        "status": "planning"
    },
    {
        "id": "proj_003",
        "name": "Mobile App for Field Sales",
        "description": "Develop mobile app for field sales team",
        "start_date": date(2024, 5, 1),
        "end_date": date(2024, 12, 31),
        "required_skills": ["React Native", "TypeScript", "Node.js", "MongoDB", "AWS"],
        "team_size": 5,
        "budget": 800000,
        "priority": "high",
        "status": "planning"
    },
    {
        "id": "proj_004",
        "name": "AI-Powered Customer Support",
        "description": "Implement AI chatbot for customer support",
        "start_date": date(2024, 6, 1),
        "end_date": date(2025, 2, 28),
        "required_skills": ["Python", "TensorFlow", "NLP", "FastAPI", "PostgreSQL"],
        "team_size": 4,
        "budget": 600000,
        "priority": "medium",
        "status": "planning"
    },
    {
    "id": "proj_005",
    "name": "Cloud Migration Initiative",
    "description": "Migrate infrastructure from on-prem to AWS cloud.",
    "start_date": date(2024, 7, 1),
    "end_date": date(2025, 1, 31),
    "required_skills": ["AWS", "Terraform", "Kubernetes", "Linux", "Python"],
    "team_size": 6,
    "budget": 900000,
    "priority": "high",
    "status": "planning"
},
{
    "id": "proj_006",
    "name": "E-Commerce Platform Upgrade",
    "description": "Upgrade legacy e-commerce platform to modern stack.",
    "start_date": date(2024, 9, 1),
    "end_date": date(2025, 3, 30),
    "required_skills": ["React", "Node.js", "MongoDB", "Docker", "CI/CD"],
    "team_size": 5,
    "budget": 750000,
    "priority": "medium",
    "status": "planning"
},
{
    "id": "proj_007",
    "name": "Automated Testing Framework",
    "description": "Build an end-to-end automated test system.",
    "start_date": date(2024, 10, 1),
    "end_date": date(2025, 4, 30),
    "required_skills": ["Selenium", "Cypress", "Java", "Python", "TestRail"],
    "team_size": 3,
    "budget": 250000,
    "priority": "low",
    "status": "planning"
}

]

# Mock team data
mock_teams = [
    {
        "id": "team_001",
        "name": "Frontend Team",
        "department": "Engineering",
        "members": ["emp_001", "emp_002"],
        "manager_id": "emp_001",
        "skills_coverage": {
            "React": 2, "JavaScript": 2, "HTML": 2, "CSS": 2,
            "Vue.js": 1, "TypeScript": 1, "Sass": 1, "Angular": 1
        }
    },
    {
        "id": "team_002",
        "name": "Backend Team",
        "department": "Engineering",
        "members": ["emp_003"],
        "manager_id": "emp_003",
        "skills_coverage": {
            "Python": 1, "Django": 1, "PostgreSQL": 1, "Redis": 1,
            "Docker": 1, "AWS": 1
        }
    },
    {
        "id": "team_003",
        "name": "Data Science Team",
        "department": "Data Science",
        "members": ["emp_004"],
        "manager_id": "emp_004",
        "skills_coverage": {
            "Python": 1, "Pandas": 1, "NumPy": 1, "Scikit-learn": 1,
            "SQL": 1, "TensorFlow": 1
        }
    },
    {
        "id": "team_004",
        "name": "DevOps Team",
        "department": "DevOps",
        "members": ["emp_005"],
        "manager_id": "emp_005",
        "skills_coverage": {
            "Docker": 1, "Kubernetes": 1, "AWS": 1, "Terraform": 1,
            "Jenkins": 1, "Linux": 1
        }
    },
    {
    "id": "team_005",
    "name": "QA Team",
    "department": "Quality Assurance",
    "members": ["emp_007"],
    "manager_id": "emp_007",
    "skills_coverage": {
        "Selenium": 1, "Cypress": 1, "Java": 1
    }
},
{
    "id": "team_006",
    "name": "Security Team",
    "department": "Security",
    "members": ["emp_008"],
    "manager_id": "emp_008",
    "skills_coverage": {
        "Cybersecurity": 1, "AWS": 1, "Python": 1
    }
}

]

# Mock skill market data
mock_skill_market_data = {
    "skill_costs": {
        "React": {"hourly_rate": 75, "demand": "high", "supply": "medium"},
        "Python": {"hourly_rate": 80, "demand": "very_high", "supply": "high"},
        "AWS": {"hourly_rate": 90, "demand": "very_high", "supply": "low"},
        "Docker": {"hourly_rate": 70, "demand": "high", "supply": "medium"},
        "TensorFlow": {"hourly_rate": 95, "demand": "high", "supply": "low"},
        "Salesforce": {"hourly_rate": 85, "demand": "medium", "supply": "medium"},
        "React Native": {"hourly_rate": 85, "demand": "high", "supply": "medium"},
        "Selenium": {"hourly_rate": 60, "demand": "high", "supply": "high"},
        "Swift": {"hourly_rate": 95, "demand": "medium", "supply": "low"},
        "Cybersecurity": {"hourly_rate": 120, "demand": "very_high", "supply": "low"},
        "Agile": {"hourly_rate": 70, "demand": "medium", "supply": "medium"}
        },
    "trends": {
        "rising_skills": ["AI/ML", "Cloud Computing", "Cybersecurity", "Test Automation"],
        "stable_skills": ["Web Development", "Mobile Development", "Database Management"],
        "declining_skills": ["Legacy Systems", "Waterfall Project Management"]
    }
}

# Consolidated mock data
mock_data = {
    "employees": mock_employees,
    "projects": mock_projects,
    "teams": mock_teams,
    "skill_market_data": mock_skill_market_data
}
