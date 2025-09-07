"""
Streamlit App for GapLens Skills Analysis System
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, List, Any
import pandas as pd
import os
from pathlib import Path
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("python-dotenv not installed. Install with: pip install python-dotenv")

# Page configuration
st.set_page_config(
    page_title="GapLens Skills Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Memory system paths
MEMORY_BASE_PATH = Path("infrastructure/memory")
SESSIONS_PATH = MEMORY_BASE_PATH / "sessions"
LOGS_PATH = MEMORY_BASE_PATH / "logs"

def safe_content_display(content, max_length=500):
    """Safely display content with proper type handling and length limiting."""
    try:
        if isinstance(content, str):
            return content[:max_length] + "..." if len(content) > max_length else content
        else:
            content_str = str(content)
            return content_str[:max_length] + "..." if len(content_str) > max_length else content_str
    except Exception:
        return str(content)[:max_length] + "..." if len(str(content)) > max_length else str(content)

def check_api_connection():
    """Check if the FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_api_data(endpoint: str) -> Dict[str, Any]:
    """Get data from the FastAPI backend."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def load_session_data(session_id: str = None) -> Dict[str, Any]:
    """Load session data from memory system."""
    try:
        if not SESSIONS_PATH.exists():
            return {}
        
        if session_id:
            session_file = SESSIONS_PATH / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
        
        # Load most recent session
        session_files = list(SESSIONS_PATH.glob("*.json"))
        if session_files:
            latest_file = max(session_files, key=lambda x: x.stat().st_mtime)
            with open(latest_file, 'r') as f:
                return json.load(f)
        
        return {}
    except Exception as e:
        st.error(f"Error loading session data: {e}")
        return {}

def get_reasoning_patterns() -> List[str]:
    """Get available reasoning patterns."""
    return ["REWOO", "REACT", "COT", "TOT", "AGENT"]

def main():
    """Main Streamlit application."""
    st.title("🔍 GapLens Skills Analysis System")
    st.markdown("AI-powered skills gap analysis and team optimization")
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ FastAPI backend is not running. Please start the backend server first.")
        st.info("Run: `cd infrastructure && python api.py`")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Department Overview", "Team Skills", "Employee Database", "Recommendations"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Department Overview":
        show_department_overview()
    elif page == "Team Skills":
        show_team_skills()
    elif page == "Employee Database":
        show_employee_database()
    elif page == "Recommendations":
        show_recommendations()

def show_dashboard():
    """Show the main dashboard."""
    st.header(" Dashboard")
    
    # Get summary data
    projects_data = get_api_data("/api/projects")
    employees_data = get_api_data("/api/employees")
    teams_data = get_api_data("/api/teams")
    departments_data = get_api_data("/api/departments")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if "error" not in projects_data:
            st.metric("Active Projects", len(projects_data))
        else:
            st.metric("Active Projects", "N/A")
   
    with col2:
        if "error" not in employees_data:
            st.metric("Team Members", len(employees_data))
        else:
            st.metric("Team Members", "N/A")
   
    with col3:
        if "error" not in teams_data:
            st.metric("Teams", len(teams_data))
        else:
            st.metric("Teams", "N/A")
   
    with col4:
        if "error" not in departments_data:
            st.metric("Departments", departments_data.get("total_departments", "N/A"))
        else:
            st.metric("Departments", "N/A")
   
    # Department breakdown
    if "error" not in departments_data:
        st.subheader(" Department Breakdown")
        dept_cols = st.columns(len(departments_data.get("departments", {})))
        
        for i, (dept_name, dept_info) in enumerate(departments_data.get("departments", {}).items()):
            with dept_cols[i]:
                st.metric(dept_name, dept_info["count"])
   
    # Recent projects
    st.subheader(" Recent Projects")
    if "error" not in projects_data:
        projects_df = pd.DataFrame(projects_data)
        st.dataframe(projects_df[["name", "status", "priority", "start_date", "budget"]], use_container_width=True)
    else:
        st.error("Failed to load projects data")


def show_team_skills():
    """Show team composition and collaboration analysis with visualizations."""
    st.header("👥 Team Composition & Collaboration Analysis")
    
    teams_data = get_api_data("/api/teams")
    employees_data = get_api_data("/api/employees")
    
    if "error" in teams_data or "error" in employees_data:
        st.error("Failed to load team or employee data")
        return
    
    # Team selection
    selected_team = st.selectbox(
        "Select a team to analyze:",
        teams_data,
        format_func=lambda x: f"{x['name']} ({len(x['members'])} members)"
    )
    
    if selected_team:
        team_members = [emp for emp in employees_data if emp["id"] in selected_team["members"]]
        
        # Team Overview Metrics
        st.subheader("📊 Team Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Team Size", len(team_members))
        with col2:
            departments = set(member["department"] for member in team_members)
            st.metric("Departments", len(departments))
        with col3:
            total_skills = len(set(skill["name"] if isinstance(skill, dict) else skill 
                                 for member in team_members for skill in member["skills"]))
            st.metric("Unique Skills", total_skills)
        with col4:
            avg_experience = sum(member["experience_years"] for member in team_members) / len(team_members)
            st.metric("Avg Experience", f"{avg_experience:.1f} years")
        
        # Department Distribution Visualization
        st.subheader("🏢 Department Distribution")
        dept_counts = {}
        for member in team_members:
            dept = member["department"]
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        # Create a pie chart for department distribution
        if dept_counts:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                
                fig, ax = plt.subplots(figsize=(8, 6))
                colors = plt.cm.Set3(np.linspace(0, 1, len(dept_counts)))
                wedges, texts, autotexts = ax.pie(dept_counts.values(), 
                                                labels=dept_counts.keys(), 
                                                autopct='%1.1f%%',
                                                colors=colors,
                                                startangle=90)
                ax.set_title('Team Department Distribution', fontsize=14, fontweight='bold')
                st.pyplot(fig)
                plt.close()
            except ImportError:
                st.warning("📊 Matplotlib not available. Install with: pip install matplotlib")
                # Fallback to simple text display
                st.write("**Department Distribution:**")
                total = sum(dept_counts.values())
            for dept, count in dept_counts.items():
                    percentage = (count / total) * 100
                    st.write(f"• {dept}: {count} members ({percentage:.1f}%)")
        
        # Skills Coverage Heatmap
        st.subheader("🔥 Skills Coverage Heatmap")
        
        # Get all unique skills across the team
        all_skills = set()
        for member in team_members:
            for skill in member["skills"]:
                skill_name = skill["name"] if isinstance(skill, dict) else skill
                all_skills.add(skill_name)
        
        # Create skills coverage matrix
        skills_matrix = []
        skill_names = sorted(list(all_skills))
        member_names = [f"{member['name']} ({member['department']})" for member in team_members]
        
        for member in team_members:
            member_skills = []
            for skill_name in skill_names:
                has_skill = any(skill["name"] if isinstance(skill, dict) else skill == skill_name 
                              for skill in member["skills"])
                member_skills.append(1 if has_skill else 0)
            skills_matrix.append(member_skills)
        
        # Create heatmap using pandas
        import pandas as pd
        skills_df = pd.DataFrame(skills_matrix, 
                               index=member_names, 
                               columns=skill_names)
        
        # Display heatmap
        st.dataframe(skills_df.style.background_gradient(cmap='RdYlGn', axis=None), 
                    use_container_width=True)
        
        # Skill Level Distribution
        st.subheader("📈 Skill Level Distribution")
        
        skill_levels = {}
        for member in team_members:
            for skill in member["skills"]:
                if isinstance(skill, dict):
                    skill_name = skill["name"]
                    level = skill["level"]
                    if skill_name not in skill_levels:
                        skill_levels[skill_name] = {"expert": 0, "advanced": 0, "intermediate": 0, "beginner": 0}
                    skill_levels[skill_name][level] += 1
        
        if skill_levels:
            try:
                # Create a stacked bar chart for skill levels
                fig, ax = plt.subplots(figsize=(12, 6))
                
                skills = list(skill_levels.keys())
                expert_counts = [skill_levels[skill]["expert"] for skill in skills]
                advanced_counts = [skill_levels[skill]["advanced"] for skill in skills]
                intermediate_counts = [skill_levels[skill]["intermediate"] for skill in skills]
                beginner_counts = [skill_levels[skill]["beginner"] for skill in skills]
                
                x = np.arange(len(skills))
                width = 0.6
                
                ax.bar(x, expert_counts, width, label='Expert', color='#2E8B57')
                ax.bar(x, advanced_counts, width, bottom=expert_counts, label='Advanced', color='#32CD32')
                ax.bar(x, intermediate_counts, width, 
                      bottom=[e+a for e, a in zip(expert_counts, advanced_counts)], 
                      label='Intermediate', color='#FFD700')
                ax.bar(x, beginner_counts, width, 
                      bottom=[e+a+i for e, a, i in zip(expert_counts, advanced_counts, intermediate_counts)], 
                      label='Beginner', color='#FF6347')
                
                ax.set_xlabel('Skills')
                ax.set_ylabel('Number of Team Members')
                ax.set_title('Skill Level Distribution Across Team')
                ax.set_xticks(x)
                ax.set_xticklabels(skills, rotation=45, ha='right')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            except ImportError:
                st.warning("📊 Matplotlib not available. Install with: pip install matplotlib")
                # Fallback to simple text display
                st.write("**Skill Level Distribution:**")
                for skill_name, levels in skill_levels.items():
                    total = sum(levels.values())
                    if total > 0:
                        st.write(f"**{skill_name}** ({total} people):")
                        for level, count in levels.items():
                            if count > 0:
                                st.write(f"  {level.title()}: {count}")
        
        # Cross-Department Collaboration Analysis
        st.subheader("🤝 Cross-Department Collaboration")
        
        if len(departments) > 1:
            st.success(f"✅ This team collaborates across {len(departments)} departments!")
            
            # Show collaboration strength
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Department Breakdown:**")
                for dept, count in dept_counts.items():
                    percentage = (count / len(team_members)) * 100
                    st.write(f"• {dept}: {count} members ({percentage:.1f}%)")
            
            with col2:
                # Calculate collaboration diversity score
                diversity_score = len(departments) / len(team_members) * 100
                st.metric("Collaboration Diversity Score", f"{diversity_score:.1f}%")
                
                if diversity_score > 50:
                    st.success("High collaboration diversity!")
                elif diversity_score > 25:
                    st.warning("Moderate collaboration diversity")
                else:
                    st.info("Low collaboration diversity")
        else:
            st.info("This is a single-department team")
        
        # Team Skill Gaps Analysis
        st.subheader("⚠️ Skill Coverage Analysis")
        
        # Identify skills with only one person
        single_person_skills = []
        for skill, count in selected_team["skills_coverage"].items():
            if count == 1:
                single_person_skills.append(skill)
        
        if single_person_skills:
            st.warning(f"🚨 {len(single_person_skills)} skills have only 1 team member:")
            for skill in single_person_skills:
                st.write(f"• {skill}")
            st.info("Consider cross-training to reduce single points of failure")
        else:
            st.success("✅ All skills have multiple team members")
        
        # Upskilling Opportunities
        st.subheader("📚 Upskilling Opportunities")
        
        high_capacity = [m for m in team_members if m["upskilling_capacity"] == "high"]
        medium_capacity = [m for m in team_members if m["upskilling_capacity"] == "medium"]
        low_capacity = [m for m in team_members if m["upskilling_capacity"] == "low"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("High Capacity", len(high_capacity), delta=f"{len(high_capacity)/len(team_members)*100:.1f}%")
        with col2:
            st.metric("Medium Capacity", len(medium_capacity), delta=f"{len(medium_capacity)/len(team_members)*100:.1f}%")
        with col3:
            st.metric("Low Capacity", len(low_capacity), delta=f"{len(low_capacity)/len(team_members)*100:.1f}%")
        
        if high_capacity:
            st.write("**High Upskilling Capacity Members:**")
            for member in high_capacity:
                st.write(f"• {member['name']} ({member['department']}) - {member['experience_years']} years exp")
        
        # Team Recommendations
        st.subheader("💡 Team Optimization Recommendations")
        
        recommendations = []
        
        # Team size recommendations
        if len(team_members) < 5:
            recommendations.append({
                "type": "warning",
                "title": "Consider Team Expansion",
                "message": f"Team has only {len(team_members)} members. Consider adding 2-3 more members for better skill coverage."
            })
        elif len(team_members) > 10:
            recommendations.append({
                "type": "info",
                "title": "Large Team Management",
                "message": f"Team has {len(team_members)} members. Consider breaking into smaller sub-teams for better coordination."
            })
        
        # Skill concentration recommendations
        if single_person_skills:
            recommendations.append({
                "type": "warning",
                "title": "Cross-Training Needed",
                "message": f"Cross-train team members on {len(single_person_skills)} skills to reduce single points of failure."
            })
        
        # Collaboration recommendations
        if len(departments) == 1:
            recommendations.append({
                "type": "info",
                "title": "Cross-Department Collaboration",
                "message": "Consider adding members from other departments to increase skill diversity."
            })
        
        # Upskilling recommendations
        if len(high_capacity) > 0:
            recommendations.append({
                "type": "success",
                "title": "Upskilling Opportunity",
                "message": f"Leverage {len(high_capacity)} high-capacity members for skill development initiatives."
            })
        
        # Display recommendations
        for rec in recommendations:
            if rec["type"] == "warning":
                st.warning(f"⚠️ **{rec['title']}**: {rec['message']}")
            elif rec["type"] == "info":
                st.info(f"ℹ️ **{rec['title']}**: {rec['message']}")
            elif rec["type"] == "success":
                st.success(f"✅ **{rec['title']}**: {rec['message']}")
        
        if not recommendations:
            st.success("🎉 Team composition looks optimal!")

def show_employee_database():
    """Show comprehensive employee talent management and skill inventory."""
    st.header("👤 Employee Talent Management & Skill Inventory")
    
    employees_data = get_api_data("/api/employees")
    if "error" in employees_data:
        st.error("Failed to load employee data")
        return
    
    # Advanced filtering and search
    st.subheader("🔍 Advanced Search & Filtering")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_term = st.text_input("Search:", placeholder="Name, role, or skill", key="search")
    with col2:
        department_filter = st.selectbox(
            "Department:",
            ["All"] + list(set(emp["department"] for emp in employees_data)),
            key="dept_filter"
        )
    with col3:
        experience_filter = st.selectbox(
            "Experience:",
            ["All", "Junior (0-3 years)", "Mid (3-6 years)", "Senior (6+ years)"],
            key="exp_filter"
        )
    with col4:
        capacity_filter = st.selectbox(
            "Upskilling Capacity:",
            ["All", "High", "Medium", "Low"],
            key="capacity_filter"
        )
    
    # Filter employees
    filtered_employees = employees_data
    if search_term:
        filtered_employees = [
            emp for emp in filtered_employees
            if (search_term.lower() in emp["name"].lower() or
                search_term.lower() in emp["role"].lower() or
                any(search_term.lower() in skill["name"].lower() if isinstance(skill, dict) else search_term.lower() in skill.lower() 
                    for skill in emp["skills"]))
        ]
    
    if department_filter != "All":
        filtered_employees = [emp for emp in filtered_employees if emp["department"] == department_filter]
    
    if experience_filter != "All":
        if experience_filter == "Junior (0-3 years)":
            filtered_employees = [emp for emp in filtered_employees if emp["experience_years"] < 3]
        elif experience_filter == "Mid (3-6 years)":
            filtered_employees = [emp for emp in filtered_employees if 3 <= emp["experience_years"] < 6]
        elif experience_filter == "Senior (6+ years)":
            filtered_employees = [emp for emp in filtered_employees if emp["experience_years"] >= 6]
    
    if capacity_filter != "All":
        filtered_employees = [emp for emp in filtered_employees if emp["upskilling_capacity"].lower() == capacity_filter.lower()]
    
    # Display results summary
    st.subheader(f"📊 Results: {len(filtered_employees)} employees found")
    
    if not filtered_employees:
        st.warning("No employees match your criteria. Try adjusting your filters.")
        return
    
    # Talent Overview Dashboard
    st.subheader("📈 Talent Overview Dashboard")
    
    # Calculate metrics
    total_employees = len(filtered_employees)
    departments = set(emp["department"] for emp in filtered_employees)
    avg_experience = sum(emp["experience_years"] for emp in filtered_employees) / total_employees
    
    # Skill distribution
    all_skills = {}
    skill_levels = {"expert": 0, "advanced": 0, "intermediate": 0, "beginner": 0}
    upskilling_capacity = {"high": 0, "medium": 0, "low": 0}
    
    for emp in filtered_employees:
        # Count upskilling capacity
        upskilling_capacity[emp["upskilling_capacity"]] += 1
        
        for skill in emp["skills"]:
            skill_name = skill["name"] if isinstance(skill, dict) else skill
            if skill_name not in all_skills:
                all_skills[skill_name] = {"count": 0, "levels": {}}
            all_skills[skill_name]["count"] += 1
            
            if isinstance(skill, dict):
                level = skill["level"]
                skill_levels[level] += 1
                if level not in all_skills[skill_name]["levels"]:
                    all_skills[skill_name]["levels"][level] = 0
                all_skills[skill_name]["levels"][level] += 1
    
    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Employees", total_employees)
    with col2:
        st.metric("Departments", len(departments))
    with col3:
        st.metric("Avg Experience", f"{avg_experience:.1f} years")
    with col4:
        st.metric("Unique Skills", len(all_skills))
    with col5:
        high_capacity = upskilling_capacity["high"]
        st.metric("High Upskilling", f"{high_capacity} ({high_capacity/total_employees*100:.1f}%)")
    
    # Skills Distribution Visualization
    st.subheader("🎯 Skills Distribution Analysis")
    
    if all_skills:
        # Top skills by count
        top_skills = sorted(all_skills.items(), key=lambda x: x[1]["count"], reverse=True)[:15]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Most Common Skills:**")
            for i, (skill_name, skill_info) in enumerate(top_skills[:10], 1):
                percentage = (skill_info["count"] / total_employees) * 100
                st.write(f"{i}. **{skill_name}**: {skill_info['count']} employees ({percentage:.1f}%)")
        
        with col2:
            # Skill level distribution pie chart
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                
                fig, ax = plt.subplots(figsize=(8, 6))
                levels = list(skill_levels.keys())
                counts = list(skill_levels.values())
                colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF6347']  # Expert, Advanced, Intermediate, Beginner
                
                wedges, texts, autotexts = ax.pie(counts, 
                                                labels=levels, 
                                                autopct='%1.1f%%',
                                                colors=colors,
                                                startangle=90)
                ax.set_title('Skill Level Distribution', fontsize=14, fontweight='bold')
                st.pyplot(fig)
                plt.close()
            except ImportError:
                st.warning("📊 Matplotlib not available. Install with: pip install matplotlib")
                # Fallback to simple text display
                st.write("**Skill Level Distribution:**")
                total_skills = sum(skill_levels.values())
                for level, count in skill_levels.items():
                    if count > 0:
                        percentage = (count / total_skills) * 100
                        st.write(f"• {level.title()}: {count} skills ({percentage:.1f}%)")
    
    
    # Employee Cards with Enhanced Information
    st.subheader("👥 Employee Profiles")
    
    # Sort options
    sort_option = st.selectbox(
        "Sort by:",
        ["Name", "Experience (High to Low)", "Experience (Low to High)", "Department", "Upskilling Capacity"],
        key="sort_option"
    )
    
    # Sort employees
    if sort_option == "Experience (High to Low)":
        filtered_employees.sort(key=lambda x: x["experience_years"], reverse=True)
    elif sort_option == "Experience (Low to High)":
        filtered_employees.sort(key=lambda x: x["experience_years"])
    elif sort_option == "Department":
        filtered_employees.sort(key=lambda x: x["department"])
    elif sort_option == "Upskilling Capacity":
        capacity_order = {"high": 3, "medium": 2, "low": 1}
        filtered_employees.sort(key=lambda x: capacity_order.get(x["upskilling_capacity"], 0), reverse=True)
    else:  # Name
        filtered_employees.sort(key=lambda x: x["name"])
    
    # Display employee cards
    for emp in filtered_employees:
        with st.expander(f"👤 {emp['name']} - {emp['role']} ({emp['department']})", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Basic Information**")
                st.write(f"**Experience:** {emp['experience_years']} years")
                st.write(f"**Location:** {emp['location']}")
                st.write(f"**Salary Range:** {emp['salary_range']}")
                st.write(f"**Availability:** {emp['availability']}")
                
                # Experience level with color coding
                if emp['experience_years'] < 3:
                    st.info("🟡 Junior Level")
                elif emp['experience_years'] < 6:
                    st.warning("🟠 Mid Level")
                else:
                    st.success("🟢 Senior Level")
            
            with col2:
                st.write("**Skills & Capabilities**")
                st.write(f"**Upskilling Capacity:** {emp['upskilling_capacity'].title()}")
                
                # Skills with level indicators
                st.write("**Skills:**")
                for skill in emp["skills"]:
                    if isinstance(skill, dict):
                        level = skill['level']
                        years = skill.get('years_experience', 0)
                        
                        # Color code skill levels
                        if level == "expert":
                            st.write(f"🟢 **{skill['name']}** ({level}, {years} years)")
                        elif level == "advanced":
                            st.write(f"🔵 **{skill['name']}** ({level}, {years} years)")
                        elif level == "intermediate":
                            st.write(f"🟡 **{skill['name']}** ({level}, {years} years)")
                        else:
                            st.write(f"🔴 **{skill['name']}** ({level}, {years} years)")
                    else:
                        st.write(f"• {skill}")
            
            with col3:
                st.write("**Talent Insights**")
                
                # Calculate skill diversity score
                skill_count = len(emp["skills"])
                if skill_count > 10:
                    diversity_score = "High"
                    diversity_color = "success"
                elif skill_count > 5:
                    diversity_score = "Medium"
                    diversity_color = "warning"
                else:
                    diversity_score = "Low"
                    diversity_color = "error"
                
                if diversity_color == "success":
                    st.success(f"🎯 Skill Diversity: {diversity_score}")
                elif diversity_color == "warning":
                    st.warning(f"🎯 Skill Diversity: {diversity_score}")
                else:
                    st.error(f"🎯 Skill Diversity: {diversity_score}")
                
                # Upskilling potential
                if emp["upskilling_capacity"] == "high":
                    st.success("🚀 High Upskilling Potential")
                elif emp["upskilling_capacity"] == "medium":
                    st.warning("⚡ Medium Upskilling Potential")
                else:
                    st.info("📚 Low Upskilling Potential")
                
                # Career stage recommendation
                if emp['experience_years'] < 3:
                    st.info("💡 Focus on foundational skills development")
                elif emp['experience_years'] < 6:
                    st.info("💡 Ready for advanced specialization")
                else:
                    st.info("💡 Consider leadership and mentoring roles")
    


def show_recommendations():
    """Show AI-generated recommendations using clean, focused implementation."""
    st.header("🎯 AI Recommendations")
    st.markdown("AI-powered skills gap analysis and team optimization recommendations")
    
    # Project selection
    st.subheader("📋 Select Project for Analysis")
    
    projects_data = get_api_data("/api/projects")
    if "error" in projects_data:
        st.error("Failed to load projects data")
        return
    
    if not projects_data:
        st.warning("No projects available for analysis")
        return
    
    # Project selection with better formatting
    selected_project = st.selectbox(
        "Choose a project to analyze:",
        projects_data,
        format_func=lambda x: f"{x['name']} - {x['status']} (${int(x['budget']):,})" if isinstance(x.get('budget'), (int, str)) and str(x['budget']).isdigit() else f"{x['name']} - {x['status']} (${x.get('budget', 'N/A')})"
    )
    
    if selected_project:
        # Display project details
        st.subheader("📊 Project Details")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Project Name:** {selected_project['name']}")
            st.write(f"**Description:** {selected_project['description']}")
            
            # Format dates properly
            try:
                if isinstance(selected_project['start_date'], str):
                    start_date = datetime.strptime(selected_project['start_date'], '%Y-%m-%d').strftime('%B %d, %Y')
                else:
                    start_date = selected_project['start_date'].strftime('%B %d, %Y')
                    
                if isinstance(selected_project['end_date'], str):
                    end_date = datetime.strptime(selected_project['end_date'], '%Y-%m-%d').strftime('%B %d, %Y')
                else:
                    end_date = selected_project['end_date'].strftime('%B %d, %Y')
                
                st.write(f"**Timeline:** {start_date} to {end_date}")
            except Exception as e:
                st.write(f"**Timeline:** {selected_project['start_date']} to {selected_project['end_date']}")
            
            try:
                budget = int(selected_project['budget'])
                st.write(f"**Budget:** ${budget:,}")
            except (ValueError, TypeError):
                st.write(f"**Budget:** ${selected_project['budget']}")
        
        with col2:
            st.write(f"**Priority:** {selected_project['priority']}")
            st.write(f"**Status:** {selected_project['status']}")
            st.write("**Required Skills:**")
            for skill in selected_project["required_skills"]:
                st.write(f"• {skill}")
        
        # Project Overview Summary
        st.subheader("🔍 Project Overview")
        required_skills_count = len(selected_project["required_skills"])
        
        # Convert string dates to date objects for calculation
        try:
            if isinstance(selected_project['start_date'], str):
                start_date = datetime.strptime(selected_project['start_date'], '%Y-%m-%d').date()
            else:
                start_date = selected_project['start_date']
                
            if isinstance(selected_project['end_date'], str):
                end_date = datetime.strptime(selected_project['end_date'], '%Y-%m-%d').date()
            else:
                end_date = selected_project['end_date']
            
            timeline_months = (end_date - start_date).days // 30
            timeline_text = f"approximately **{timeline_months} months**"
        except Exception as e:
            timeline_text = "the specified timeline"
        
        st.write(f"This **{selected_project['priority']} priority** project requires **{required_skills_count} key skills** and will run for {timeline_text}.")
        st.write(f"The project aims to: {selected_project['description']}")
        
        # Budget analysis
        try:
            budget = int(selected_project['budget'])
            if budget > 500000:
            st.info("💰 **High-budget project** - Consider comprehensive skill development and external hiring options.")
            elif budget > 200000:
            st.info("💰 **Medium-budget project** - Balance between upskilling existing team and strategic hiring.")
        else:
            st.info("💰 **Budget-conscious project** - Focus on internal upskilling and team transfers where possible.")
        except (ValueError, TypeError):
            st.info("💰 **Project budget information available** - Consider skill development and hiring options based on project requirements.")
        
        # Analysis scope selection
        st.subheader("🎯 Analysis Scope")
        scope = st.radio(
            "Choose analysis scope:",
            ["Department Only", "Full Company"],
            help="Department: Analyze skills within the project team's department only. Full Company: Consider all company skills."
        )
        
        scope_param = "department" if scope == "Department Only" else "company"
        
        # AI Analysis button
        if st.button("🚀 Generate AI Recommendations", type="primary", use_container_width=True):
            with st.spinner("🤖 AI agents are analyzing your project..."):
                try:
                    # Import the full workflow system
                    from core.workflow import MultiAgentWorkflow
                    from core import make_llm, make_reasoner
                    
                    # Create LLMs with anthropic backend
                    perception_llm = make_llm("anthropic")
                    reasoner_llm = make_reasoner("anthropic")
                    
                    # Prepare the analysis question focused on the selected project
                    analysis_question = f"""Analyze ONLY the skill gaps for this specific project and provide structured recommendations.

Project ID: {selected_project.get('id', 'unknown')}
Project Name: {selected_project['name']}
Required Skills: {', '.join(selected_project['required_skills'])}
Timeline: {selected_project['start_date']} to {selected_project['end_date']}
Budget: ${selected_project['budget']:,}
Scope: {scope_param}

IMPORTANT: Focus ONLY on this specific project. Do NOT analyze all projects or other projects. Return ONLY a JSON object with upskilling, transfer, and hiring recommendations for this specific project. Focus on actionable solutions with timelines and success probabilities."""
                    
                    # Show the analysis question
                    with st.expander("🔍 Analysis Question", expanded=False):
                        st.write(analysis_question)
                    
                    # Create and run the multi-agent workflow
                    st.subheader("🤖 Multi-Agent Workflow Execution")
                    
                    # Get the project ID and scope for the workflow
                    project_id = selected_project.get('id', 'unknown')
                    
                    # Show workflow parameters
                    with st.expander("🔍 Workflow Parameters", expanded=False):
                        st.write(f"**Project ID:** {project_id}")
                        st.write(f"**Project Name:** {selected_project['name']}")
                        st.write(f"**Analysis Scope:** {scope_param}")
                        st.write(f"**Required Skills:** {', '.join(selected_project['required_skills'])}")
                    
                    workflow = MultiAgentWorkflow(perception_llm, reasoner_llm)
                    result = workflow.run(analysis_question, project_id=project_id, scope=scope_param)
                    
                    # Display results from the full workflow
                    if result:
                        # Show intent and entities
                        if result.get('intent'):
                            st.info(f"**Analysis Intent:** {result['intent']}")
                        
                        if result.get('entities'):
                            st.info(f"**Identified Entities:** {', '.join(result['entities'])}")
                        
                        # Parse and display results using clean formatting
                        analysis_data = None
                        decision_data = None
                        
                        # Parse analysis data - handle both string and dict formats
                        if result.get('analysis'):
                            try:
                                if isinstance(result['analysis'], str):
                                    # Try to parse as JSON first
                                    try:
                                        analysis_data = json.loads(result['analysis'])
                                    except json.JSONDecodeError:
                                        # If not JSON, treat as text analysis
                                        analysis_data = {"text_analysis": result['analysis']}
                                else:
                                    analysis_data = result['analysis']
                            except Exception as e:
                                st.warning(f"Could not parse analysis data: {e}")
                                analysis_data = {"text_analysis": str(result['analysis'])}
                        
                        # Parse decision data - handle both string and dict formats
                        if result.get('decision'):
                            try:
                                if isinstance(result['decision'], str):
                                    # Try to parse as JSON first
                                    try:
                                        decision_data = json.loads(result['decision'])
                                    except json.JSONDecodeError:
                                        # If not JSON, treat as text decision
                                        decision_data = {"text_decision": result['decision']}
                                else:
                                    decision_data = result['decision']
                            except Exception as e:
                                st.warning(f"Could not parse decision data: {e}")
                                decision_data = {"text_decision": str(result['decision'])}
                        
                        # Display clean recommendations
                        display_clean_recommendations(analysis_data, result)
                        
                        # Show workflow summary
                        with st.expander("📊 Workflow Summary", expanded=False):
                            st.json(result)
                        
                        st.success("✅ Multi-agent workflow completed successfully!")
                            
                        # Next steps
                        st.subheader("🔄 Next Steps")
                        st.write("1. **Review Recommendations**: Carefully consider each recommendation based on your team's capacity and timeline")
                        st.write("2. **Prioritize Actions**: Start with high-confidence, high-impact recommendations")
                        st.write("3. **Plan Implementation**: Create detailed action plans with timelines and responsibilities")
                        st.write("4. **Monitor Progress**: Track skill development and adjust plans as needed")
                        st.write("5. **Regular Reviews**: Schedule periodic assessments to ensure project readiness")
                    
                    else:
                        st.error("❌ No results generated from multi-agent workflow")
                        
                except Exception as e:
                    st.error(f"❌ Error running multi-agent workflow: {e}")
                    st.info("Make sure you have the ANTHROPIC_API_KEY set in your environment")
                    
                    # Show environment check
                    with st.expander("🔧 Environment Check", expanded=False):
                        st.write("**ANTHROPIC_API_KEY:**", "✅ Set" if os.getenv("ANTHROPIC_API_KEY") else "❌ Not Set")
                        if os.getenv("ANTHROPIC_API_KEY"):
                            st.write("**Key length:**", len(os.getenv("ANTHROPIC_API_KEY")))
                        st.write("**Current working directory:**", os.getcwd())
                        
                        # Manual API key input as fallback
                        if not os.getenv("ANTHROPIC_API_KEY"):
                            st.warning("ANTHROPIC_API_KEY not found. You can manually enter it below:")
                            manual_key = st.text_input("Enter Anthropic API Key:", type="password")
                            if manual_key:
                                os.environ["ANTHROPIC_API_KEY"] = manual_key
                                st.success("API key set manually")
                                st.rerun()

def display_clean_recommendations(analysis_data, workflow_result=None):
    """Display recommendations in a clean, readable format instead of raw JSON."""
    
    # Display workflow summary and agent thinking process
    if workflow_result:
        st.subheader("🤖 Agent Workflow Summary")
        
        # Show the original question
        if workflow_result.get('question'):
            with st.expander("📝 Original Analysis Question", expanded=False):
                st.write(workflow_result['question'])
        
        # Show intent and entities
        if workflow_result.get('intent') and workflow_result['intent'] != 'unknown':
            st.info(f"**🎯 Analysis Intent:** {workflow_result['intent']}")
        
        if workflow_result.get('entities') and workflow_result['entities']:
            st.info(f"**🔍 Identified Entities:** {', '.join(workflow_result['entities'])}")
        
        # Show normalized question if different from original
        if workflow_result.get('normalized_question') and workflow_result['normalized_question'] != workflow_result.get('question'):
            with st.expander("🔄 Normalized Question", expanded=False):
                st.write(workflow_result['normalized_question'])
        
        # Show project context (without banners)
        if workflow_result.get('project_id'):
            st.write(f"**📋 Project ID:** {workflow_result['project_id']}")
        if workflow_result.get('scope'):
            st.write(f"**🌐 Analysis Scope:** {workflow_result['scope']}")
        
        st.write("---")
    
    # Display Analysis Results
    if analysis_data:
        st.subheader("📋 Skills Gap Analysis")
        
        # Handle text analysis format
        if analysis_data.get('text_analysis'):
            st.markdown("**📄 Analysis Report:**")
            st.markdown(analysis_data['text_analysis'])
            st.write("")
        
        # Handle structured analysis format
        if analysis_data.get('skill_gaps'):
            st.write("**🔍 Missing Skills:**")
            for skill in analysis_data['skill_gaps']:
                st.write(f"• {skill}")
            st.write("")
        
        # Upskilling recommendations
        if analysis_data.get('upskilling'):
            st.write("**🎓 Upskilling Opportunities:**")
            for i, rec in enumerate(analysis_data['upskilling'], 1):
                confidence_badge = f"<span style='background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.875rem; font-weight: 600;'>{rec.get('confidence', 'Unknown').title()}</span>" if rec.get('confidence') == 'high' else f"<span style='background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.875rem; font-weight: 600;'>{rec.get('confidence', 'Unknown').title()}</span>"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                    border-radius: 12px;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 5px solid #10b981;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    color: #064e3b;
                ">
                    <h4 style="margin: 0 0 15px 0; color: #065f46; display: flex; align-items: center; gap: 10px;">
                        📚 Recommendation {i}: Upskill {rec.get('employee', 'Unknown')}
                        {confidence_badge}
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                        <div><strong>🎯 Skill to Learn:</strong><br>{rec.get('skill_to_learn', 'Unknown')}</div>
                        <div><strong>⏱️ Timeline:</strong><br>{rec.get('timeline_weeks', 'Unknown')} weeks</div>
                    </div>
                    <p style="margin: 0; font-style: italic; color: #1f2937;"><strong>💡 Reason:</strong> {rec.get('reason', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
        
        # Internal transfers
        if analysis_data.get('internal_transfers'):
            st.write("**🔄 Internal Transfer Opportunities:**")
            for i, rec in enumerate(analysis_data['internal_transfers'], 1):
                urgency_badge = f"<span style='background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.875rem; font-weight: 600;'>{rec.get('availability', 'Unknown').title()}</span>" if rec.get('availability') == 'immediate' else f"<span style='background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.875rem; font-weight: 600;'>{rec.get('availability', 'Unknown').title()}</span>"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
                    border-radius: 12px;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 5px solid #f59e0b;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    color: #92400e;
                ">
                    <h4 style="margin: 0 0 15px 0; color: #92400e; display: flex; align-items: center; gap: 10px;">
                        🔄 Recommendation {i}: Transfer {rec.get('employee', 'Unknown')}
                        {urgency_badge}
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                        <div><strong>🏢 From Team:</strong><br>{rec.get('current_team', 'Unknown')}</div>
                        <div><strong>🎯 Skills Brought:</strong><br>{', '.join(rec.get('skills_brought', []))}</div>
                    </div>
                    <p style="margin: 0; font-style: italic; color: #1f2937;"><strong>💡 Reason:</strong> {rec.get('reason', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
        
        # Hiring recommendations
        if analysis_data.get('hiring'):
            st.write("**👥 Hiring Recommendations:**")
            for i, rec in enumerate(analysis_data['hiring'], 1):
                urgency_badge = f"<span style='background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.875rem; font-weight: 600;'>{rec.get('urgency', 'Unknown').title()}</span>" if rec.get('urgency') == 'critical' else f"<span style='background: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.875rem; font-weight: 600;'>{rec.get('urgency', 'Unknown').title()}</span>"
        st.markdown(f"""
        <div style="
                    background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
                    border-radius: 12px;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 5px solid #ef4444;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    color: #991b1b;
                ">
                    <h4 style="margin: 0 0 15px 0; color: #991b1b; display: flex; align-items: center; gap: 10px;">
                        👥 Recommendation {i}: Hire {rec.get('role', 'Unknown Role')}
                        {urgency_badge}
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                        <div><strong>🎯 Required Skills:</strong><br>{', '.join(rec.get('required_skills', []))}</div>
                        <div><strong>💰 Estimated Cost:</strong><br>{rec.get('estimated_cost', 'N/A')}</div>
                    </div>
        </div>
        """, unsafe_allow_html=True)
            st.write("")
        
        # Timeline and risk assessment
        if analysis_data.get('timeline_assessment'):
            st.info(f"**⏰ Timeline Assessment:** {analysis_data['timeline_assessment']}")
        
        if analysis_data.get('risk_factors'):
            st.warning("**⚠️ Risk Factors:**")
            for risk in analysis_data['risk_factors']:
                st.write(f"• {risk}")
        
        if analysis_data.get('success_probability'):
            success_color = "#4CAF50" if analysis_data['success_probability'] == "high" else "#FF9800" if analysis_data['success_probability'] == "medium" else "#F44336"
            st.markdown(f"**🎯 Success Probability:** <span style='color: {success_color}; font-weight: bold;'>{analysis_data['success_probability'].title()}</span>", unsafe_allow_html=True)


def show_department_overview():
    """Show comprehensive department overview."""
    st.header("🏢 Department Overview")
    
    # Get department data
    dept_overview = get_api_data("/api/employees/departments")
    
    if "error" in dept_overview:
        st.error("Failed to load department data")
        return
    
    # Department summary cards
    st.subheader(" Department Summary")
    
    # Create department cards in a grid
    dept_data = dept_overview.get("departments", {})
    dept_names = list(dept_data.keys())
    
    # Calculate grid layout
    cols_per_row = 3
    for i in range(0, len(dept_names), cols_per_row):
        row_depts = dept_names[i:i + cols_per_row]
        cols = st.columns(len(row_depts))
        
        for j, dept_name in enumerate(row_depts):
            with cols[j]:
                dept_info = dept_data[dept_name]
                st.metric(
                    label=dept_name,
                    value=dept_info["count"],
                    delta=f"${dept_info['avg_salary']}k avg"
                )
                
                # Experience level breakdown
                exp_levels = dept_info["experience_levels"]
                st.write(f"**Experience:** {exp_levels['junior']}J, {exp_levels['mid']}M, {exp_levels['senior']}S")
    
    # Detailed department analysis
    st.subheader(" Detailed Analysis")
    
    selected_dept = st.selectbox(
        "Select Department for Detailed View:",
        dept_names
    )
    
    if selected_dept:
        dept_info = dept_data[selected_dept]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Total Employees:** {dept_info['count']}")
            st.write(f"**Average Salary:** ${dept_info['avg_salary']}k")
            st.write(f"**Total Skills:** {len(dept_info['skills'])}")
            
            # Experience level chart
            exp_levels = dept_info["experience_levels"]
            st.write("**Experience Distribution:**")
            for level, count in exp_levels.items():
                if count > 0:
                    st.progress(count / dept_info['count'])
                    st.write(f"{level.title()}: {count}")
        
        with col2:
            st.write("**Roles in Department:**")
            for role in dept_info["roles"]:
                st.write(f"• {role}")
            
            st.write("**Key Skills:**")
            # Show top skills (limit to 10)
            skills_to_show = dept_info["skills"][:10]
            for skill in skills_to_show:
                st.write(f"• {skill}")
            
            if len(dept_info["skills"]) > 10:
                st.write(f"... and {len(dept_info['skills']) - 10} more skills")
    
    # Skills heatmap across departments
    st.subheader(" Skills Heatmap Across Departments")
    
    # Create skills matrix
    all_skills = set()
    for dept_info in dept_data.values():
        all_skills.update(dept_info["skills"])
    
    skills_matrix = {}
    for skill in sorted(all_skills):
        skills_matrix[skill] = {}
        for dept_name in dept_names:
            skills_matrix[skill][dept_name] = skill in dept_data[dept_name]["skills"]
    
    # Convert to DataFrame for display
    skills_df = pd.DataFrame(skills_matrix).T
    
    # Create a styled heatmap
    def color_skills(val):
        return 'background-color: #90EE90' if val else 'background-color: #FFB6C1'
    
    st.dataframe(skills_df.style.applymap(color_skills), use_container_width=True)
    
    # Department comparison
    st.subheader(" Department Comparison")
    
    # Salary comparison
    salary_data = []
    for dept_name in dept_names:
        dept_info = dept_data[dept_name]
        salary_data.append({
            "Department": dept_name,
            "Employee Count": dept_info["count"],
            "Avg Salary ($k)": dept_info["avg_salary"],
            "Total Skills": len(dept_info["skills"])
        })
    
    comparison_df = pd.DataFrame(salary_data)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Skills Distribution Analysis
    st.subheader("🎯 Skills Distribution Analysis")
    
    # Get all employees data for skills analysis
    employees_data = get_api_data("/api/employees")
    if "error" not in employees_data:
        # Calculate skill distribution across all employees
        all_skills = {}
        skill_levels = {"expert": 0, "advanced": 0, "intermediate": 0, "beginner": 0}
        
        for emp in employees_data:
            for skill in emp["skills"]:
                skill_name = skill["name"] if isinstance(skill, dict) else skill
                if skill_name not in all_skills:
                    all_skills[skill_name] = {"count": 0, "levels": {}}
                all_skills[skill_name]["count"] += 1
                
                if isinstance(skill, dict):
                    level = skill["level"]
                    skill_levels[level] += 1
                    if level not in all_skills[skill_name]["levels"]:
                        all_skills[skill_name]["levels"][level] = 0
                    all_skills[skill_name]["levels"][level] += 1
        
        if all_skills:
            # Top skills by count
            top_skills = sorted(all_skills.items(), key=lambda x: x[1]["count"], reverse=True)[:15]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Most Common Skills Across All Departments:**")
                for i, (skill_name, skill_info) in enumerate(top_skills[:10], 1):
                    percentage = (skill_info["count"] / len(employees_data)) * 100
                    st.write(f"{i}. **{skill_name}**: {skill_info['count']} employees ({percentage:.1f}%)")
            
            with col2:
                # Skill level distribution pie chart
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    levels = list(skill_levels.keys())
                    counts = list(skill_levels.values())
                    colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF6347']  # Expert, Advanced, Intermediate, Beginner
                    
                    wedges, texts, autotexts = ax.pie(counts, 
                                                    labels=levels, 
                                                    autopct='%1.1f%%',
                                                    colors=colors,
                                                    startangle=90)
                    ax.set_title('Skill Level Distribution', fontsize=14, fontweight='bold')
                    st.pyplot(fig)
                    plt.close()
                except ImportError:
                    st.warning("📊 Matplotlib not available. Install with: pip install matplotlib")
                    # Fallback to simple text display
                    st.write("**Skill Level Distribution:**")
                    total_skills = sum(skill_levels.values())
                    for level, count in skill_levels.items():
                        if count > 0:
                            percentage = (count / total_skills) * 100
                            st.write(f"• {level.title()}: {count} skills ({percentage:.1f}%)")
    else:
        st.warning("Could not load employee data for skills analysis")


if __name__ == "__main__":
    main()
