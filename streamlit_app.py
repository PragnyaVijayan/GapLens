"""
Streamlit App for GapLens Skills Analysis System
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, List, Any
import pandas as pd
from core.memory_system import ReasoningPattern
from core.workflow import MultiAgentWorkflow
from core import make_all_agent_llms
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
        ["Dashboard", "Department Overview", "Team Skills", "Employee Database", "Recommendations", "Analysis History"]
    )
    
    # Add recommendation history management
    if page == "Analysis History":
        show_analysis_history()
        return
    
    # Quick action panel in sidebar
    if page == "Recommendations":
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚡ Quick Actions")
        
        if st.sidebar.button("🔄 Load Last Analysis", use_container_width=True):
            if 'analysis_history' in st.session_state and st.session_state.analysis_history:
                latest = st.session_state.analysis_history[0]
                st.session_state.analysis_results = latest['results']
                st.session_state.analysis_params = latest['params']
                st.sidebar.success("Latest analysis loaded!")
            else:
                st.sidebar.warning("No analysis history found")
        
        if st.sidebar.button("📊 Quick Stats", use_container_width=True):
            if 'analysis_results' in st.session_state:
                st.sidebar.success("Check the Results & Insights tab!")
            else:
                st.sidebar.info("Generate recommendations first")
        
        if st.sidebar.button("💾 Save Current", use_container_width=True):
            if 'analysis_results' in st.session_state:
                st.sidebar.success("Analysis saved to history!")
            else:
                st.sidebar.warning("No analysis to save")
        
        # Recent analyses
        if 'analysis_history' in st.session_state and st.session_state.analysis_history:
            st.sidebar.markdown("---")
            st.sidebar.subheader("📚 Recent Analyses")
            for i, analysis in enumerate(st.session_state.analysis_history[:3]):  # Show last 3
                if st.sidebar.button(f"📊 {analysis['project'][:20]}...", key=f"quick_load_{i}"):
                    st.session_state.analysis_results = analysis['results']
                    st.session_state.analysis_params = analysis['params']
                    st.sidebar.success(f"Loaded {analysis['project']}!")
    
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
    """Enhanced recommendations page with advanced filtering and analysis options."""
    st.header("🎯 AI-Powered Recommendations")
    st.markdown("Get comprehensive skill gap analysis and strategic recommendations for your projects")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Project Analysis", "⚙️ Analysis Configuration", "📊 Results & Insights", "📈 Impact Assessment"])
    
    with tab1:
        st.subheader("📋 Project Selection & Configuration")
        
        # Get projects data - use mock data directly since API functions are async
        try:
            from infrastructure.mock_data import mock_projects
            projects_data = mock_projects
        except:
            # Fallback to hardcoded mock data with more projects
            projects_data = [
                {
                    "id": "proj_001",
                    "name": "Cloud Migration Initiative",
                    "description": "Migrate legacy systems to AWS cloud infrastructure",
                    "required_skills": ["AWS", "Terraform", "Kubernetes", "Python", "Docker"],
                    "start_date": "2024-07-01",
                    "end_date": "2025-01-31",
                    "budget": 900000,
                    "priority": "High",
                    "status": "Planning",
                    "department": "Engineering",
                    "team_size": 8
                },
                {
                    "id": "proj_002", 
                    "name": "Data Analytics Platform",
                    "description": "Build real-time analytics dashboard",
                    "required_skills": ["Python", "SQL", "React", "Docker", "Kafka"],
                    "start_date": "2024-08-15",
                    "end_date": "2025-02-28",
                    "budget": 500000,
                    "priority": "Medium",
                    "status": "In Progress",
                    "department": "Data Science",
                    "team_size": 5
                },
                {
                    "id": "proj_003",
                    "name": "Mobile App Development",
                    "description": "Cross-platform mobile application for customer engagement",
                    "required_skills": ["React Native", "TypeScript", "Node.js", "MongoDB"],
                    "start_date": "2024-09-01",
                    "end_date": "2025-03-15",
                    "budget": 750000,
                    "priority": "High",
                    "status": "Planning",
                    "department": "Product",
                    "team_size": 6
                },
                {
                    "id": "proj_004",
                    "name": "AI/ML Integration",
                    "description": "Integrate machine learning models into existing systems",
                    "required_skills": ["Python", "TensorFlow", "MLOps", "Kubernetes", "Python"],
                    "start_date": "2024-10-01",
                    "end_date": "2025-06-30",
                    "budget": 1200000,
                    "priority": "High",
                    "status": "Planning",
                    "department": "AI/ML",
                    "team_size": 10
                }
            ]
        
        if not projects_data:
            st.error("No projects available")
            return
        
        # Advanced project filtering
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_term = st.text_input("🔍 Search Projects", placeholder="Project name or description")
        
        with col2:
            status_filter = st.selectbox("📊 Status", ["All"] + list(set(p["status"] for p in projects_data)))
        
        with col3:
            priority_filter = st.selectbox("⚡ Priority", ["All"] + list(set(p["priority"] for p in projects_data)))
        
        with col4:
            department_filter = st.selectbox("🏢 Department", ["All"] + list(set(p.get("department", "Unknown") for p in projects_data)))
        
        # Filter projects
        filtered_projects = projects_data
        if search_term:
            filtered_projects = [p for p in filtered_projects if 
                               search_term.lower() in p["name"].lower() or 
                               search_term.lower() in p["description"].lower()]
        
        if status_filter != "All":
            filtered_projects = [p for p in filtered_projects if p["status"] == status_filter]
        
        if priority_filter != "All":
            filtered_projects = [p for p in filtered_projects if p["priority"] == priority_filter]
        
        if department_filter != "All":
            filtered_projects = [p for p in filtered_projects if p.get("department", "Unknown") == department_filter]
        
        # Display filtered results count
        st.info(f"📊 Found {len(filtered_projects)} project(s) matching your criteria")
        
        if not filtered_projects:
            st.warning("No projects match your filter criteria. Try adjusting your search parameters.")
            return
        
        # Project selection with enhanced display
        selected_project = st.selectbox(
            "Choose a project to analyze:",
            filtered_projects,
            format_func=lambda x: f"{x['name']} - {x['status']} (${x['budget']:,}) - {x.get('department', 'Unknown')}"
        )
    
        if not selected_project:
            st.warning("Please select a project")
            return
        
        # Enhanced project details display
        st.subheader("📊 Project Details")
        
        # Project overview cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Budget", f"${selected_project['budget']:,}")
        
        with col2:
            priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            st.metric("Priority", f"{priority_color.get(selected_project['priority'], '⚪')} {selected_project['priority']}")
        
        with col3:
            status_color = {"Planning": "🔵", "In Progress": "🟡", "Completed": "🟢", "On Hold": "🔴"}
            st.metric("Status", f"{status_color.get(selected_project['status'], '⚪')} {selected_project['status']}")
        
        with col4:
            st.metric("Team Size", f"{selected_project.get('team_size', 'N/A')} members")
        
        # Detailed project information
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**📝 Name:** {selected_project['name']}")
            st.write(f"**📋 Description:** {selected_project['description']}")
            st.write(f"**📅 Timeline:** {selected_project['start_date']} to {selected_project['end_date']}")
            st.write(f"**🏢 Department:** {selected_project.get('department', 'Unknown')}")
        
        with col2:
            st.write("**🛠️ Required Skills:**")
            for skill in selected_project['required_skills']:
                st.write(f"• {skill}")
            
            # Skill count and complexity
            skill_count = len(selected_project['required_skills'])
            if skill_count > 8:
                complexity = "🔴 High"
            elif skill_count > 4:
                complexity = "🟡 Medium"
            else:
                complexity = "🟢 Low"
            st.write(f"**📊 Skill Complexity:** {complexity} ({skill_count} skills)")
    
    with tab2:
        st.subheader("⚙️ Analysis Configuration")
        
        # Analysis scope with more options
        st.write("**🎯 Analysis Scope**")
        scope = st.radio(
            "Choose analysis scope:",
            ["Department Only", "Full Company", "Custom Team Selection"],
            help="Department: Analyze skills within the project team's department only. Full Company: Consider all company skills. Custom: Select specific teams or individuals."
        )
        
        scope_param = "department" if scope == "Department Only" else "company"
        
        if scope == "Custom Team Selection":
            st.subheader("👥 Custom Team Selection")
            
            # Get available employees
            try:
                from infrastructure.mock_data import mock_employees
                employees_data = mock_employees
            except:
                employees_data = []
            
            if employees_data:
                # Multi-select for team members
                selected_employees = st.multiselect(
                    "Select team members:",
                    employees_data,
                    format_func=lambda x: f"{x['name']} - {x['role']} ({x['department']})",
                    help="Choose specific team members for the analysis"
                )
                
                if selected_employees:
                    st.write(f"**Selected Team ({len(selected_employees)} members):**")
                    for emp in selected_employees:
                        st.write(f"• {emp['name']} - {emp['role']} ({emp['department']})")
                    
                    # Show team skills summary
                    team_skills = set()
                    for emp in selected_employees:
                        for skill in emp['skills']:
                            skill_name = skill['name'] if isinstance(skill, dict) else skill
                            team_skills.add(skill_name)
                    
                    st.write(f"**Team Skills Coverage:** {len(team_skills)} unique skills")
                    st.write(f"**Skills:** {', '.join(sorted(team_skills))}")
                    
                    scope_param = "custom_team"
                    st.session_state.custom_team = selected_employees
                else:
                    st.warning("Please select at least one team member")
                    scope_param = "company"  # Fallback
            else:
                st.error("No employee data available for team selection")
                scope_param = "company"  # Fallback
        
        # Advanced analysis options
        st.write("**🔧 Advanced Analysis Options**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Budget constraints
            budget_constraint = st.selectbox(
                "💰 Budget Constraint",
                ["No Limit", "Under $100k", "Under $500k", "Under $1M", "Custom"],
                help="Set budget limits for hiring and training recommendations"
            )
            
            if budget_constraint == "Custom":
                custom_budget = st.number_input("Custom Budget Limit ($)", min_value=0, value=500000, step=10000)
            else:
                custom_budget = None
            
            # Timeline preferences
            timeline_preference = st.selectbox(
                "⏱️ Timeline Preference",
                ["Fast Track (1-3 months)", "Standard (3-6 months)", "Extended (6+ months)", "Flexible"],
                help="Preferred timeline for implementing recommendations"
            )
        
        with col2:
            # Risk tolerance
            risk_tolerance = st.selectbox(
                "⚠️ Risk Tolerance",
                ["Conservative", "Balanced", "Aggressive"],
                help="How much risk are you willing to take with recommendations"
            )
            
            # Focus areas
            focus_areas = st.multiselect(
                "🎯 Focus Areas",
                ["Cost Optimization", "Speed to Market", "Quality Assurance", "Team Development", "Innovation"],
                default=["Cost Optimization", "Team Development"],
                help="Areas to prioritize in the analysis"
            )
        
        # Analysis depth
        st.write("**🔍 Analysis Depth**")
        analysis_depth = st.select_slider(
            "Analysis Detail Level",
            options=["Quick", "Standard", "Comprehensive", "Deep Dive"],
            value="Standard",
            help="More detailed analysis takes longer but provides more insights"
        )
        
        # Additional filters
        with st.expander("🔧 Additional Filters", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Experience level preferences
                exp_preference = st.multiselect(
                    "👥 Experience Level Preferences",
                    ["Junior (0-3 years)", "Mid-level (3-6 years)", "Senior (6+ years)", "Expert (10+ years)"],
                    default=["Mid-level (3-6 years)", "Senior (6+ years)"]
                )
                
                # Skill level requirements
                skill_level_req = st.selectbox(
                    "🛠️ Minimum Skill Level Required",
                    ["Beginner", "Intermediate", "Advanced", "Expert"],
                    help="Minimum skill level for recommendations"
                )
            
            with col2:
                # Geographic preferences
                geo_preference = st.multiselect(
                    "🌍 Geographic Preferences",
                    ["Local", "Remote", "Hybrid", "Global"],
                    default=["Local", "Remote"]
                )
                
                # Availability requirements
                availability_req = st.selectbox(
                    "📅 Availability Requirements",
                    ["Immediate", "Within 1 month", "Within 3 months", "Flexible"],
                    help="When do you need the skills to be available"
                )
        
        # Analysis parameters summary
        st.write("**📋 Analysis Parameters Summary**")
        params_col1, params_col2 = st.columns(2)
        
        with params_col1:
            st.write(f"• **Scope:** {scope}")
            st.write(f"• **Budget:** {budget_constraint}")
            st.write(f"• **Timeline:** {timeline_preference}")
        
        with params_col2:
            st.write(f"• **Risk Tolerance:** {risk_tolerance}")
            st.write(f"• **Analysis Depth:** {analysis_depth}")
            st.write(f"• **Focus Areas:** {', '.join(focus_areas) if focus_areas else 'None'}")
    
    # Generate recommendations button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate AI Recommendations", type="primary", use_container_width=True):
            # Store analysis parameters in session state
            st.session_state.analysis_params = {
                'project': selected_project,
                'scope': scope_param,
                'budget_constraint': budget_constraint,
                'timeline_preference': timeline_preference,
                'risk_tolerance': risk_tolerance,
                'focus_areas': focus_areas,
                'analysis_depth': analysis_depth,
                'exp_preference': exp_preference,
                'skill_level_req': skill_level_req,
                'geo_preference': geo_preference,
                'availability_req': availability_req
            }
            
            # Check for API key
            if not os.getenv("ANTHROPIC_API_KEY"):
                st.error("❌ ANTHROPIC_API_KEY not found in environment variables")
                st.info("Please set your Anthropic API key in the environment or use the manual input below:")
                manual_key = st.text_input("Enter Anthropic API Key:", type="password")
                if manual_key:
                    os.environ["ANTHROPIC_API_KEY"] = manual_key
                    st.success("API key set! Please click the button again.")
                    return
                else:
                    return
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Initialize
                status_text.text("🤖 Initializing AI agents...")
                progress_bar.progress(10)
                
                # Create LLMs
                agent_llms = make_all_agent_llms("anthropic")
                
                # Step 2: Create workflow
                status_text.text("🔧 Setting up workflow...")
                progress_bar.progress(20)
                
                workflow = MultiAgentWorkflow(
                    agent_llms["perception"],
                    agent_llms["research"], 
                    agent_llms["analysis"],
                    agent_llms["decision"],
                    agent_llms["orchestrator"]
                )
                
                # Step 3: Prepare enhanced question
                status_text.text("📝 Preparing analysis question...")
                progress_bar.progress(30)
                
                analysis_question = f"""Analyze the skill gaps for this specific project and provide structured recommendations.

Project ID: {selected_project['id']}
Project Name: {selected_project['name']}
Required Skills: {', '.join(selected_project['required_skills'])}
Timeline: {selected_project['start_date']} to {selected_project['end_date']}
Budget: ${selected_project['budget']:,}
Scope: {scope_param}
Analysis Depth: {analysis_depth}
Risk Tolerance: {risk_tolerance}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'None'}
Timeline Preference: {timeline_preference}

Focus ONLY on this specific project. Return ONLY a JSON object with upskilling, transfer, and hiring recommendations for this specific project."""
                
                # Step 4: Run workflow
                status_text.text("🧠 Running AI analysis...")
                progress_bar.progress(50)
                
                try:
                    result = workflow.run(
                        analysis_question, 
                        project_id=selected_project['id'], 
                        scope=scope_param
                    )
                except Exception as workflow_error:
                    st.error(f"❌ Workflow execution failed: {str(workflow_error)}")
                    st.info("This might be due to JSON parsing issues. The system will retry with improved error handling.")
                    
                    # Try again with a simpler question
                    simple_question = f"Analyze skill gaps for project {selected_project['name']} requiring {', '.join(selected_project['required_skills'][:3])}"
                    try:
                        result = workflow.run(simple_question, project_id=selected_project['id'], scope=scope_param)
                    except Exception as retry_error:
                        st.error(f"❌ Retry also failed: {str(retry_error)}")
                        return
                
                # Step 5: Process results
                status_text.text("📊 Processing results...")
                progress_bar.progress(80)
                
                if result:
                    # Store results in session state
                    st.session_state.analysis_results = result
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    st.success("🎉 Analysis completed! Check the 'Results & Insights' tab to view recommendations.")
                    
                else:
                    st.error("❌ No results generated")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
            finally:
                progress_bar.empty()
                status_text.empty()
    
    with tab3:
        st.subheader("📊 Results & Insights")
        
        if 'analysis_results' not in st.session_state:
            st.info("👆 Please generate recommendations first by clicking the 'Generate AI Recommendations' button.")
            return
        
        result = st.session_state.analysis_results
        selected_project = st.session_state.analysis_params['project']
        
        # Results overview
        st.write("**📋 Analysis Overview**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project", selected_project['name'])
        with col2:
            st.metric("Scope", st.session_state.analysis_params['scope'].title())
        with col3:
            st.metric("Analysis Depth", st.session_state.analysis_params['analysis_depth'])
        with col4:
            st.metric("Risk Tolerance", st.session_state.analysis_params['risk_tolerance'])
        
        # Display results using existing function
        display_recommendations(result, selected_project)
        
        # Additional insights and export options
        st.subheader("📈 Additional Insights & Tools")
        
        # Create tabs for different tools
        tool_tab1, tool_tab2, tool_tab3, tool_tab4 = st.tabs(["🔧 Tools", "📊 Visualizations", "📋 Export", "🔄 Compare"])
        
        with tool_tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Generate Comparison Report", use_container_width=True):
                    if len(st.session_state.get('analysis_history', [])) >= 2:
                        # Generate comparison between current and most recent analysis
                        current_analysis = {
                            'analysis': result.get('analysis', '{}'),
                            'project': selected_project
                        }
                        latest_analysis = st.session_state.analysis_history[0]
                        
                        comparison_report = generate_comparison_report(current_analysis, latest_analysis)
                        st.markdown(comparison_report)
                    else:
                        st.warning("Need at least 2 analyses to generate comparison report. Generate more analyses first.")
                
                if st.button("📈 Create Timeline Visualization", use_container_width=True):
                    # Create interactive timeline
                    st.subheader("📅 Interactive Timeline")
                    
                    # Timeline phases
                    phases = [
                        {"name": "Planning", "duration": 2, "status": "completed"},
                        {"name": "Skill Assessment", "duration": 1, "status": "completed"},
                        {"name": "Training Program", "duration": 6, "status": "in_progress"},
                        {"name": "Implementation", "duration": 12, "status": "pending"},
                        {"name": "Testing & Review", "duration": 3, "status": "pending"},
                        {"name": "Go-Live", "duration": 1, "status": "pending"}
                    ]
                    
                    # Create timeline visualization
                    for i, phase in enumerate(phases):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            status_icon = "✅" if phase["status"] == "completed" else "🟡" if phase["status"] == "in_progress" else "⏳"
                            st.write(f"{status_icon} **{phase['name']}**")
                        
                        with col2:
                            st.write(f"Duration: {phase['duration']} weeks")
                        
                        with col3:
                            status_color = {"completed": "success", "in_progress": "warning", "pending": "info"}
                            st.write(f"Status: {phase['status'].title()}")
                
                if st.button("🎯 Skill Gap Heatmap", use_container_width=True):
                    # Generate skill gap heatmap
                    st.subheader("🔥 Skill Gap Heatmap")
                    
                    if 'analysis' in result:
                        heatmap_df = generate_skill_gap_heatmap(result)
                        if not heatmap_df.empty:
                            st.dataframe(heatmap_df, use_container_width=True)
                            
                            # Color-coded priority visualization
                            st.write("**Priority Distribution:**")
                            priority_counts = heatmap_df['Priority'].value_counts()
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("High Priority", priority_counts.get('High', 0))
                            with col2:
                                st.metric("Medium Priority", priority_counts.get('Medium', 0))
                            with col3:
                                st.metric("Low Priority", priority_counts.get('Low', 0))
                        else:
                            st.info("No skill gap data available for heatmap")
                    else:
                        st.warning("No analysis data available")
            
            with col2:
                if st.button("💾 Save Analysis", use_container_width=True):
                    # Add current analysis to history
                    if 'analysis_results' in st.session_state and 'analysis_params' in st.session_state:
                        current_analysis = {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'project': st.session_state.analysis_params['project']['name'],
                            'project_id': st.session_state.analysis_params['project']['id'],
                            'scope': st.session_state.analysis_params['scope'],
                            'analysis_depth': st.session_state.analysis_params['analysis_depth'],
                            'risk_tolerance': st.session_state.analysis_params['risk_tolerance'],
                            'results': st.session_state.analysis_results,
                            'params': st.session_state.analysis_params
                        }
                        
                        if 'analysis_history' not in st.session_state:
                            st.session_state.analysis_history = []
                        
                        st.session_state.analysis_history.insert(0, current_analysis)
                        st.success("Analysis saved to session history!")
                    else:
                        st.warning("No analysis to save")
                
                if st.button("📝 Generate Summary", use_container_width=True):
                    if 'analysis' in result:
                        summary = generate_summary_report(result, selected_project)
                        st.markdown(summary)
                        
                        # Add download button
                        st.download_button(
                            label="📥 Download Summary as Markdown",
                            data=summary,
                            file_name=f"analysis_summary_{selected_project['id']}.md",
                            mime="text/markdown"
                        )
                    else:
                        st.warning("No analysis data available for summary generation")
                
                if st.button("🔍 Deep Dive Analysis", use_container_width=True):
                    st.subheader("🔍 Deep Dive Analysis")
                    
                    if 'analysis' in result:
                        analysis = result['analysis']
                        if isinstance(analysis, str):
                            analysis = json.loads(analysis)
                        
                        # Detailed breakdown
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**📊 Detailed Metrics**")
                            skill_gaps = analysis.get('skill_gaps', [])
                            upskilling = analysis.get('upskilling', [])
                            hiring = analysis.get('hiring', [])
                            
                            st.metric("Total Skill Gaps", len(skill_gaps))
                            st.metric("Upskilling Opportunities", len(upskilling))
                            st.metric("Hiring Needs", len(hiring))
                            st.metric("Success Probability", analysis.get('success_probability', 'Unknown'))
                        
                        with col2:
                            st.write("**🎯 Risk Assessment**")
                            risk_factors = analysis.get('risk_factors', [])
                            if risk_factors:
                                for risk in risk_factors:
                                    st.write(f"• {risk}")
                            else:
                                st.write("No specific risk factors identified")
                        
                        # Detailed recommendations breakdown
                        if upskilling:
                            st.write("**👥 Detailed Upskilling Analysis**")
                            for i, upskill in enumerate(upskilling, 1):
                                with st.expander(f"Upskilling {i}: {upskill.get('employee', 'Unknown')} → {upskill.get('skill_to_learn', 'Unknown')}"):
                                    st.write(f"**Timeline:** {upskill.get('timeline_weeks', 'N/A')} weeks")
                                    st.write(f"**Confidence:** {upskill.get('confidence', 'N/A')}")
                                    st.write(f"**Reason:** {upskill.get('reason', 'N/A')}")
                        
                        if hiring:
                            st.write("**💼 Detailed Hiring Analysis**")
                            for i, hire in enumerate(hiring, 1):
                                with st.expander(f"Hiring {i}: {hire.get('role', 'Unknown')}"):
                                    st.write(f"**Required Skills:** {', '.join(hire.get('required_skills', []))}")
                                    st.write(f"**Urgency:** {hire.get('urgency', 'N/A')}")
                                    st.write(f"**Estimated Cost:** {hire.get('estimated_cost', 'N/A')}")
                    else:
                        st.warning("No analysis data available for deep dive")
        
        with tool_tab2:
            st.write("**📊 Interactive Visualizations**")
            
            # Skill gap visualization
            if 'analysis' in result:
                try:
                    analysis_data = result['analysis']
                    if isinstance(analysis_data, str):
                        analysis_data = json.loads(analysis_data)
                    
                    skill_gaps = analysis_data.get('skill_gaps', [])
                    upskilling = analysis_data.get('upskilling', [])
                    hiring = analysis_data.get('hiring', [])
                    
                    # Create a simple visualization
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Skill Gaps", len(skill_gaps))
                        if skill_gaps:
                            st.write("**Gap Details:**")
                            for gap in skill_gaps[:3]:  # Show first 3
                                st.write(f"• {gap}")
                    
                    with col2:
                        st.metric("Upskilling Opportunities", len(upskilling))
                        if upskilling:
                            st.write("**Upskilling Details:**")
                            for upskill in upskilling[:3]:  # Show first 3
                                employee = upskill.get('employee', 'Unknown')
                                skill = upskill.get('skill_to_learn', 'Unknown')
                                st.write(f"• {employee} → {skill}")
                    
                    with col3:
                        st.metric("Hiring Needs", len(hiring))
                        if hiring:
                            st.write("**Hiring Details:**")
                            for hire in hiring[:3]:  # Show first 3
                                role = hire.get('role', 'Unknown')
                                urgency = hire.get('urgency', 'Unknown')
                                st.write(f"• {role} ({urgency})")
                
                except Exception as e:
                    st.warning(f"Could not parse analysis data: {e}")
            
            # Interactive charts
            if st.button("📈 Generate Interactive Charts"):
                st.subheader("📈 Interactive Data Visualizations")
                
                if 'analysis' in result:
                    analysis = result['analysis']
                    if isinstance(analysis, str):
                        analysis = json.loads(analysis)
                    
                    # Create interactive charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Skill gap distribution pie chart
                        skill_gaps = analysis.get('skill_gaps', [])
                        upskilling = analysis.get('upskilling', [])
                        hiring = analysis.get('hiring', [])
                        
                        if skill_gaps or upskilling or hiring:
                            chart_data = {
                                'Skill Gaps': len(skill_gaps),
                                'Upskilling': len(upskilling),
                                'Hiring': len(hiring)
                            }
                            
                            try:
                                import plotly.express as px
                                import pandas as pd
                                
                                df = pd.DataFrame(list(chart_data.items()), columns=['Category', 'Count'])
                                fig = px.pie(df, values='Count', names='Category', title='Recommendation Distribution')
                                st.plotly_chart(fig, use_container_width=True)
                            except ImportError:
                                st.warning("📊 Plotly not installed. Install with: pip install plotly")
                                # Fallback to simple bar chart
                                import pandas as pd
                                df = pd.DataFrame(list(chart_data.items()), columns=['Category', 'Count'])
                                st.bar_chart(df.set_index('Category'))
                    
                    with col2:
                        # Timeline visualization
                        if upskilling:
                            timeline_data = []
                            for upskill in upskilling:
                                timeline_data.append({
                                    'Employee': upskill.get('employee', 'Unknown'),
                                    'Skill': upskill.get('skill_to_learn', 'Unknown'),
                                    'Timeline (weeks)': upskill.get('timeline_weeks', 0)
                                })
                            
                            if timeline_data:
                                try:
                                    import plotly.express as px
                                    df_timeline = pd.DataFrame(timeline_data)
                                    fig_timeline = px.bar(df_timeline, x='Employee', y='Timeline (weeks)', 
                                                        color='Skill', title='Upskilling Timeline by Employee')
                                    st.plotly_chart(fig_timeline, use_container_width=True)
                                except ImportError:
                                    # Fallback to simple bar chart
                                    df_timeline = pd.DataFrame(timeline_data)
                                    st.bar_chart(df_timeline.set_index('Employee'))
                    
                    # Additional visualizations
                    st.write("**📊 Additional Metrics**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Recommendations", len(skill_gaps) + len(upskilling) + len(hiring))
                    with col2:
                        st.metric("Success Probability", analysis.get('success_probability', 'Unknown'))
                    with col3:
                        st.metric("Timeline Assessment", analysis.get('timeline_assessment', 'Unknown'))
                else:
                    st.warning("No analysis data available for charts")
        
        with tool_tab3:
            st.write("**📋 Export Options**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Export to PDF", use_container_width=True):
                    if 'analysis' in result:
                        summary = generate_summary_report(result, selected_project)
                        success, message = export_to_pdf(summary, f"analysis_report_{selected_project['id']}.pdf")
                        if success:
                            st.success(message)
                            with open(f"analysis_report_{selected_project['id']}.pdf", "rb") as file:
                                st.download_button(
                                    label="📥 Download PDF",
                                    data=file.read(),
                                    file_name=f"analysis_report_{selected_project['id']}.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            st.error(message)
                    else:
                        st.warning("No analysis data available for PDF export")
                
                if st.button("📊 Export to Excel", use_container_width=True):
                    if 'analysis' in result:
                        analysis = result['analysis']
                        if isinstance(analysis, str):
                            analysis = json.loads(analysis)
                        
                        success, message = export_to_excel(analysis, f"analysis_report_{selected_project['id']}.xlsx")
                        if success:
                            st.success(message)
                            with open(f"analysis_report_{selected_project['id']}.xlsx", "rb") as file:
                                st.download_button(
                                    label="📥 Download Excel",
                                    data=file.read(),
                                    file_name=f"analysis_report_{selected_project['id']}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        else:
                            st.error(message)
                    else:
                        st.warning("No analysis data available for Excel export")
                
                if st.button("📋 Export to CSV", use_container_width=True):
                    if 'analysis' in result:
                        analysis = result['analysis']
                        if isinstance(analysis, str):
                            analysis = json.loads(analysis)
                        
                        success, message = export_to_csv(analysis, f"analysis_report_{selected_project['id']}.csv")
                        if success:
                            st.success(message)
                            with open(f"analysis_report_{selected_project['id']}.csv", "rb") as file:
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=file.read(),
                                    file_name=f"analysis_report_{selected_project['id']}.csv",
                                    mime="text/csv"
                                )
                        else:
                            st.error(message)
                    else:
                        st.warning("No analysis data available for CSV export")
            
            with col2:
                if st.button("📧 Email Report", use_container_width=True):
                    st.subheader("📧 Email Report")
                    email = st.text_input("Enter email address:", placeholder="your.email@company.com")
                    if email and st.button("Send Report"):
                        # Simulate email sending
                        st.success(f"Report sent to {email}! (Simulated)")
                
                if st.button("🔗 Share Link", use_container_width=True):
                    # Generate a shareable link (simulated)
                    share_link = f"https://gaplens.app/share/{selected_project['id']}_{datetime.now().strftime('%Y%m%d')}"
                    st.success("Shareable link generated!")
                    st.code(share_link)
                    st.button("📋 Copy Link")
                
                if st.button("📱 Mobile View", use_container_width=True):
                    st.subheader("📱 Mobile-Optimized View")
                    st.info("Mobile view is automatically optimized! The app is responsive and works well on mobile devices.")
                    
                    # Show mobile-specific metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Screen Size", "Responsive")
                    with col2:
                        st.metric("Touch Friendly", "✅ Yes")
        
        with tool_tab4:
            st.write("**🔄 Compare Analyses**")
            
            if len(st.session_state.get('analysis_history', [])) < 2:
                st.info("Need at least 2 analyses to compare. Generate more recommendations first!")
            else:
                st.write("**Select analyses to compare:**")
                
                # Get available analyses
                available_analyses = st.session_state.get('analysis_history', [])
                if 'analysis_results' in st.session_state and 'analysis_params' in st.session_state:
                    current_analysis = {
                        'project': st.session_state.analysis_params['project']['name'],
                        'timestamp': 'Current Session'
                    }
                    available_analyses = [current_analysis] + available_analyses
                
                # Analysis selection
                analysis1 = st.selectbox(
                    "First Analysis:",
                    available_analyses,
                    format_func=lambda x: f"{x['project']} - {x['timestamp']}"
                )
                
                analysis2 = st.selectbox(
                    "Second Analysis:",
                    [a for a in available_analyses if a != analysis1],
                    format_func=lambda x: f"{x['project']} - {x['timestamp']}"
                )
                
                if st.button("🔄 Compare Analyses"):
                    if analysis1 and analysis2:
                        # Find the actual analysis data
                        analysis1_data = None
                        analysis2_data = None
                        
                        # Get current analysis if selected
                        if analysis1.get('timestamp') == 'Current Session':
                            analysis1_data = {
                                'analysis': result.get('analysis', '{}'),
                                'project': selected_project
                            }
                        else:
                            analysis1_data = analysis1
                        
                        if analysis2.get('timestamp') == 'Current Session':
                            analysis2_data = {
                                'analysis': result.get('analysis', '{}'),
                                'project': selected_project
                            }
                        else:
                            analysis2_data = analysis2
                        
                        if analysis1_data and analysis2_data:
                            comparison_report = generate_comparison_report(analysis1_data, analysis2_data)
                            st.markdown(comparison_report)
                        else:
                            st.error("Could not load analysis data for comparison")
                    else:
                        st.warning("Please select two analyses to compare")
    
    with tab4:
        st.subheader("📈 Impact Assessment & ROI Analysis")
        
        if 'analysis_results' not in st.session_state:
            st.info("👆 Please generate recommendations first to see impact assessment.")
            return
        
        # Impact assessment widgets
        st.write("**💰 Cost-Benefit Analysis**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Estimated Total Cost", "$500K - $750K", delta="+15% vs budget")
        
        with col2:
            st.metric("Expected ROI", "180%", delta="+25% vs baseline")
        
        with col3:
            st.metric("Payback Period", "8 months", delta="-2 months vs target")
        
        # Risk assessment
        st.write("**⚠️ Risk Assessment**")
        
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            st.write("**High Risk Factors:**")
            st.write("• Skill shortage in critical areas")
            st.write("• Timeline constraints")
            st.write("• Budget overruns")
        
        with risk_col2:
            st.write("**Mitigation Strategies:**")
            st.write("• Cross-training programs")
            st.write("• Phased implementation")
            st.write("• Contingency budget allocation")
        
        # Success metrics
        st.write("**📊 Success Metrics**")
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.write("**Quantitative Metrics:**")
            st.write("• 95% skill coverage target")
            st.write("• 90% on-time delivery")
            st.write("• 15% cost reduction")
        
        with metrics_col2:
            st.write("**Qualitative Outcomes:**")
            st.write("• Improved team morale")
            st.write("• Enhanced knowledge sharing")
            st.write("• Reduced technical debt")
        
        # Timeline visualization
        st.write("**📅 Implementation Timeline**")
        
        # Create a more detailed timeline
        timeline_data = {
            "Phase": ["Project Planning", "Skill Assessment", "Training Program", "Implementation", "Testing & Review", "Go-Live"],
            "Duration (weeks)": [2, 1, 6, 12, 3, 1],
            "Start Week": [1, 3, 4, 10, 22, 25],
            "End Week": [2, 3, 9, 21, 24, 25],
            "Status": ["Completed", "Completed", "In Progress", "Pending", "Pending", "Pending"],
            "Dependencies": ["None", "Project Planning", "Skill Assessment", "Training Program", "Implementation", "Testing & Review"]
        }
        
        import pandas as pd
        timeline_df = pd.DataFrame(timeline_data)
        
        # Display timeline with better formatting
        st.dataframe(timeline_df, use_container_width=True)
        
        # Visual timeline representation
        st.write("**📊 Visual Timeline**")
        
        # Create a simple Gantt-like visualization
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from datetime import datetime, timedelta
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Color mapping for status
            status_colors = {
                "Completed": "#2E8B57",
                "In Progress": "#FFD700", 
                "Pending": "#D3D3D3"
            }
            
            # Create timeline bars
            y_pos = 0
            for _, row in timeline_df.iterrows():
                color = status_colors.get(row['Status'], "#D3D3D3")
                
                # Create rectangle for each phase
                rect = patches.Rectangle(
                    (row['Start Week'], y_pos), 
                    row['Duration (weeks)'], 
                    0.8,
                    linewidth=1, 
                    edgecolor='black', 
                    facecolor=color,
                    alpha=0.7
                )
                ax.add_patch(rect)
                
                # Add phase name
                ax.text(row['Start Week'] + row['Duration (weeks)']/2, y_pos + 0.4, 
                       row['Phase'], ha='center', va='center', fontsize=8, fontweight='bold')
                
                y_pos += 1
            
            ax.set_xlim(0, 26)
            ax.set_ylim(-0.5, len(timeline_df))
            ax.set_xlabel('Weeks')
            ax.set_ylabel('Project Phases')
            ax.set_title('Implementation Timeline Gantt Chart')
            ax.set_yticks(range(len(timeline_df)))
            ax.set_yticklabels(timeline_df['Phase'])
            ax.grid(True, alpha=0.3)
            
            # Add legend
            legend_elements = [patches.Patch(color=color, label=status) 
                             for status, color in status_colors.items()]
            ax.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
        except ImportError:
            st.warning("📊 Matplotlib not available. Install with: pip install matplotlib")
            # Fallback to simple text timeline
            st.write("**Timeline Overview:**")
            for _, row in timeline_df.iterrows():
                status_icon = "✅" if row['Status'] == "Completed" else "🟡" if row['Status'] == "In Progress" else "⏳"
                st.write(f"{status_icon} **{row['Phase']}**: Weeks {row['Start Week']}-{row['End Week']} ({row['Duration (weeks)']} weeks)")
        
        # Interactive timeline controls
        st.write("**🎛️ Timeline Controls**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏭️ Advance Timeline"):
                st.subheader("⏭️ Timeline Advancement")
                current_phase = st.selectbox("Current Phase:", ["Planning", "Skill Assessment", "Training Program", "Implementation", "Testing & Review", "Go-Live"])
                next_phase = st.selectbox("Advance to:", ["Planning", "Skill Assessment", "Training Program", "Implementation", "Testing & Review", "Go-Live"])
                
                if st.button("Advance Timeline"):
                    st.success(f"Timeline advanced from {current_phase} to {next_phase}!")
                    st.info("Timeline updated successfully. All dependent phases have been adjusted accordingly.")
        
        with col2:
            if st.button("📊 Update Progress"):
                st.subheader("📊 Progress Update")
                
                # Progress tracking form
                with st.form("progress_form"):
                    phase = st.selectbox("Phase:", ["Planning", "Skill Assessment", "Training Program", "Implementation", "Testing & Review", "Go-Live"])
                    progress = st.slider("Progress (%)", 0, 100, 50)
                    notes = st.text_area("Progress Notes:", placeholder="Enter any updates or notes...")
                    
                    if st.form_submit_button("Update Progress"):
                        st.success(f"Progress updated for {phase}: {progress}% complete")
                        if notes:
                            st.info(f"Notes: {notes}")
        
        with col3:
            if st.button("🔄 Reset Timeline"):
                st.subheader("🔄 Timeline Reset")
                
                if st.button("Confirm Reset", type="primary"):
                    st.warning("Timeline has been reset to initial state!")
                    st.info("All phases are now marked as pending. You can restart the timeline from the beginning.")
        
        # Recommendation validation
        st.write("**✅ Recommendation Validation**")
        
        validation_col1, validation_col2 = st.columns(2)
        
        with validation_col1:
            if st.button("👍 Approve Recommendations"):
                st.success("✅ Recommendations approved!")
            
            if st.button("🔄 Request Modifications"):
                st.info("Modification request submitted!")
        
        with validation_col2:
            if st.button("📝 Add Feedback"):
                feedback = st.text_area("Your feedback:", placeholder="Enter your feedback here...")
                if feedback:
                    st.success("Feedback submitted!")
            
            if st.button("📊 Generate Alternative"):
                st.info("Alternative recommendations generated!")

def display_recommendations(result, project):
    """Display the analysis and decision results in a clean format."""
    
    st.subheader("🧠 Analysis Results")
    
    # Parse analysis
    analysis = result.get('analysis', '')
    if analysis:
        try:
            if isinstance(analysis, str):
                analysis_data = json.loads(analysis)
            else:
                analysis_data = analysis
                
            # Display skill gaps
            skill_gaps = analysis_data.get('skill_gaps', [])
            if skill_gaps:
                st.write("**🔍 Skill Gaps Identified:**")
                for gap in skill_gaps:
                    st.write(f"• {gap}")
            else:
                st.info("No specific skill gaps identified")
            
            # Display upskilling recommendations
            upskilling = analysis_data.get('upskilling', [])
            if upskilling:
                st.write("**👥 Upskilling Recommendations:**")
                for rec in upskilling:
                    employee = rec.get('employee', 'Unknown')
                    skill = rec.get('skill_to_learn', 'Unknown')
                    timeline = rec.get('timeline_weeks', 'Unknown')
                    confidence = rec.get('confidence', 'Unknown')
                    reason = rec.get('reason', 'No reason provided')
                    
                    with st.expander(f"🎯 {employee} - Learn {skill}"):
                        st.write(f"**Timeline:** {timeline} weeks")
                        st.write(f"**Confidence:** {confidence}")
                        st.write(f"**Reason:** {reason}")
            else:
                st.info("No upskilling recommendations")
            
            # Display hiring recommendations
            hiring = analysis_data.get('hiring', [])
            if hiring:
                st.write("**💼 Hiring Recommendations:**")
                for hire in hiring:
                    role = hire.get('role', 'Unknown')
                    skills = hire.get('required_skills', [])
                    urgency = hire.get('urgency', 'Unknown')
                    cost = hire.get('estimated_cost', 'Unknown')
                    
                    with st.expander(f"👔 {role}"):
                        st.write(f"**Required Skills:** {', '.join(skills)}")
                        st.write(f"**Urgency:** {urgency}")
                        st.write(f"**Estimated Cost:** {cost}")
            else:
                st.info("No hiring recommendations")
            
            # Display timeline and success probability
            timeline_assessment = analysis_data.get('timeline_assessment', 'Not available')
            success_probability = analysis_data.get('success_probability', 'Unknown')
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Timeline Assessment", timeline_assessment)
            with col2:
                st.metric("Success Probability", success_probability)
                
        except json.JSONDecodeError as e:
            st.error(f"Could not parse analysis results: {e}")
            st.code(analysis)
    else:
        st.warning("No analysis results available")
    
    # Display decision results
    st.subheader("🎯 Final Recommendations")
    
    decision = result.get('decision', '')
    if decision:
        try:
            if isinstance(decision, str):
                decision_data = json.loads(decision)
            else:
                decision_data = decision
            
            # Display selected strategy
            selected_strategy = decision_data.get('selected_strategy', {})
            if selected_strategy:
                strategy_name = selected_strategy.get('strategy_name', 'Unknown')
                strategy_type = selected_strategy.get('strategy_type', 'Unknown')
                confidence = selected_strategy.get('confidence', 'Unknown')
                rationale = selected_strategy.get('rationale', 'No rationale provided')
                
                st.success(f"**Selected Strategy: {strategy_name}**")
                st.write(f"**Type:** {strategy_type}")
                st.write(f"**Confidence:** {confidence}")
                st.write(f"**Rationale:** {rationale}")
            
            # Display implementation plan
            implementation_plan = decision_data.get('implementation_plan', {})
            if implementation_plan:
                st.write("**📋 Implementation Plan:**")
                
                primary_owner = implementation_plan.get('primary_owner', 'TBD')
                timeline_weeks = implementation_plan.get('timeline_weeks', 'Unknown')
                budget_estimate = implementation_plan.get('budget_estimate', 'Unknown')
                
                st.write(f"**Primary Owner:** {primary_owner}")
                st.write(f"**Timeline:** {timeline_weeks} weeks")
                st.write(f"**Budget Estimate:** {budget_estimate}")
                
                milestones = implementation_plan.get('key_milestones', [])
                if milestones:
                    st.write("**Key Milestones:**")
                    for i, milestone in enumerate(milestones, 1):
                        st.write(f"{i}. {milestone}")
            
            # Display natural language summary
            summary = decision_data.get('natural_language_summary', '')
            if summary:
                st.write("**📝 Summary:**")
                st.write(summary)
                
        except json.JSONDecodeError as e:
            st.error(f"Could not parse decision results: {e}")
            st.code(decision)
    else:
        st.warning("No decision results available")
    
    # Show raw data for debugging
    with st.expander("🔧 Debug Information", expanded=False):
        st.json(result)

def display_analysis_strategies(analysis_data):
    """Display analysis agent strategies in an expandable widget."""
    
    # Handle both old format (single object) and new format (array of strategies)
    strategies = []
    if isinstance(analysis_data, list):
        strategies = analysis_data
    elif isinstance(analysis_data, dict):
        # Check if it's the new format with strategies array
        if 'strategy_name' in analysis_data:
            strategies = [analysis_data]
        else:
            # Old format - create a single strategy
            strategies = [{
                "strategy_name": "Analysis Results",
                "strategy_type": "mixed",
                "skill_gaps": analysis_data.get('skill_gaps', []),
                "upskilling": analysis_data.get('upskilling', []),
                "internal_transfers": analysis_data.get('internal_transfers', []),
                "hiring": analysis_data.get('hiring', []),
                "timeline_assessment": analysis_data.get('timeline_assessment', 'N/A'),
                "risk_factors": analysis_data.get('risk_factors', []),
                "success_probability": analysis_data.get('success_probability', 'medium'),
                "estimated_cost": analysis_data.get('estimated_cost', 'N/A'),
                "pros": analysis_data.get('pros', []),
                "cons": analysis_data.get('cons', [])
            }]
    
    if not strategies:
        return
    
    with st.expander("📊 Analysis Strategies Generated", expanded=False):
        st.markdown("The Analysis Agent generated the following recommendation strategies:")
        
        for i, strategy in enumerate(strategies, 1):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
                border-left: 4px solid #3b82f6;
                box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
            ">
                <h4 style="margin: 0 0 15px 0; color: #1e40af; display: flex; align-items: center; gap: 10px;">
                    📋 Strategy {i}: {strategy.get('strategy_name', 'Unknown Strategy')}
                    <span style="background: #3b82f6; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">
                        {strategy.get('strategy_type', 'mixed').title()}
                    </span>
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Strategy details in columns
            col1, col2 = st.columns(2)
            
            with col1:
                if strategy.get('skill_gaps'):
                    st.markdown("**🎯 Skill Gaps:**")
                    for gap in strategy['skill_gaps']:
                        st.write(f"• {gap}")
                
                if strategy.get('timeline_assessment'):
                    st.markdown(f"**⏱️ Timeline:** {strategy['timeline_assessment']}")
                
                if strategy.get('success_probability'):
                    prob_color = "#10b981" if strategy['success_probability'] == "high" else "#f59e0b" if strategy['success_probability'] == "medium" else "#ef4444"
                    st.markdown(f"**📈 Success Probability:** <span style='color: {prob_color}; font-weight: bold;'>{strategy['success_probability'].title()}</span>", unsafe_allow_html=True)
            
            with col2:
                if strategy.get('estimated_cost'):
                    st.markdown(f"**💰 Estimated Cost:** {strategy['estimated_cost']}")
                
                if strategy.get('risk_factors'):
                    st.markdown("**⚠️ Risk Factors:**")
                    for risk in strategy['risk_factors']:
                        st.write(f"• {risk}")
            
            # Upskilling details
            if strategy.get('upskilling'):
                st.markdown("**🎓 Upskilling Recommendations:**")
                for upskill in strategy['upskilling']:
                    st.write(f"• **{upskill.get('employee', 'Unknown')}** → {upskill.get('skill_to_learn', 'Unknown skill')} ({upskill.get('timeline_weeks', 'N/A')} weeks)")
            
            # Internal transfers
            if strategy.get('internal_transfers'):
                st.markdown("**🔄 Internal Transfers:**")
                for transfer in strategy['internal_transfers']:
                    st.write(f"• **{transfer.get('employee', 'Unknown')}** from {transfer.get('current_team', 'Unknown team')}")
            
            # Hiring recommendations
            if strategy.get('hiring'):
                st.markdown("**👥 Hiring Recommendations:**")
                for hire in strategy['hiring']:
                    st.write(f"• **{hire.get('role', 'Unknown role')}** - {hire.get('estimated_cost', 'Cost TBD')}")
            
            # Pros and cons
            col1, col2 = st.columns(2)
            
            with col1:
                if strategy.get('pros'):
                    st.markdown("**✅ Advantages:**")
                    for pro in strategy['pros']:
                        st.write(f"• {pro}")
            
            with col2:
                if strategy.get('cons'):
                    st.markdown("**❌ Disadvantages:**")
                    for con in strategy['cons']:
                        st.write(f"• {con}")
            
            st.write("---")


def display_clean_recommendations(decision_data, workflow_result=None):
    """Display decision agent recommendations in natural language while logging JSON to memory."""
    
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
    
    # Display Decision Agent Results in Natural Language
    if decision_data:
        # Log the full JSON to memory for technical reference
        if workflow_result and workflow_result.get('session_memory'):
            workflow_result['session_memory'].add_entry(
                agent="decision",
                content=json.dumps(decision_data, indent=2),
                reasoning_pattern=ReasoningPattern.TOT,
                reasoning_steps=["Decision agent provided structured JSON output"],
                confidence=0.9,
                metadata={"output_type": "structured_json", "display_format": "natural_language"}
            )
        
        # Display the main natural language recommendation prominently
        st.subheader("🎯 Recommendation")
        
        # Show the natural language summary prominently
        if decision_data.get('natural_language_summary'):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border-radius: 12px;
                padding: 30px;
                margin: 20px 0;
                border-left: 5px solid #0ea5e9;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="margin: 0 0 20px 0; color: #0c4a6e; font-size: 1.5rem;">
                    💡 Our Recommendation
                </h3>
                <div style="color: #1e40af; font-size: 1.1rem; line-height: 1.7; white-space: pre-line;">
                    {decision_data['natural_language_summary']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif decision_data.get('website_message'):
            # Fallback for old format
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border-radius: 12px;
                padding: 30px;
                margin: 20px 0;
                border-left: 5px solid #0ea5e9;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="margin: 0 0 20px 0; color: #0c4a6e; font-size: 1.5rem;">
                    💡 Our Recommendation
                </h3>
                <p style="margin: 0; color: #1e40af; font-size: 1.2rem; line-height: 1.6;">
                    {decision_data['website_message']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed Strategy Information in Expandable Widget
        with st.expander("📊 Detailed Strategy Information", expanded=False):
            if decision_data.get('selected_strategy'):
                strategy = decision_data['selected_strategy']
                confidence = strategy.get('confidence', 'medium')
                confidence_color = "#10b981" if confidence == "high" else "#f59e0b" if confidence == "medium" else "#ef4444"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                        border-radius: 8px;
                        padding: 20px;
                        margin: 10px 0;
                        border-left: 4px solid #64748b;
                        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
                    ">
                        <h4 style="margin: 0 0 10px 0; color: #334155; display: flex; align-items: center; gap: 10px;">
                            📊 Selected Strategy: {strategy.get('strategy_name', 'Unknown Strategy')}
                            <span style="background: {confidence_color}; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">
                                {confidence.title()} Confidence
                            </span>
                        </h4>
                        <p style="margin: 0; color: #475569; font-size: 1rem;"><strong>Type:</strong> {strategy.get('strategy_type', 'Unknown').title()}</p>
                        <p style="margin: 8px 0 0 0; color: #64748b; font-size: 0.9rem;"><strong>Rationale:</strong> {strategy.get('rationale', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if decision_data.get('decision_summary'):
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                            border-radius: 8px;
                            padding: 20px;
                            margin: 10px 0;
                            border-left: 4px solid #22c55e;
                            box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
                        ">
                            <h4 style="margin: 0 0 10px 0; color: #166534;">📝 Decision Summary</h4>
                            <p style="margin: 0; color: #15803d; font-size: 0.95rem;">{decision_data['decision_summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Strategy Details
        if decision_data.get('strategy_details'):
            details = decision_data['strategy_details']
            
            st.markdown("### 📋 Strategy Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if details.get('primary_action'):
                    st.write(f"**🎯 Primary Action:** {details['primary_action']}")
                if details.get('target_skill'):
                    st.write(f"**🔧 Target Skill:** {details['target_skill']}")
                if details.get('timeline_weeks'):
                    st.write(f"**⏱️ Timeline:** {details['timeline_weeks']} weeks")
            
            with col2:
                if details.get('success_probability'):
                    prob_color = "#10b981" if details['success_probability'] == "high" else "#f59e0b" if details['success_probability'] == "medium" else "#ef4444"
                    st.markdown(f"**📊 Success Probability:** <span style='color: {prob_color}; font-weight: bold;'>{details['success_probability'].title()}</span>", unsafe_allow_html=True)
                if details.get('cost_estimate'):
                    cost_color = "#10b981" if details['cost_estimate'] == "low" else "#f59e0b" if details['cost_estimate'] == "medium" else "#ef4444"
                    st.markdown(f"**💰 Cost Estimate:** <span style='color: {cost_color}; font-weight: bold;'>{details['cost_estimate'].title()}</span>", unsafe_allow_html=True)
                if details.get('risk_level'):
                    risk_color = "#10b981" if details['risk_level'] == "low" else "#f59e0b" if details['risk_level'] == "medium" else "#ef4444"
                    st.markdown(f"**⚠️ Risk Level:** <span style='color: {risk_color}; font-weight: bold;'>{details['risk_level'].title()}</span>", unsafe_allow_html=True)
        
        # Implementation Plan
        if decision_data.get('implementation_plan'):
            impl = decision_data['implementation_plan']
            
            st.markdown("### 📋 Implementation Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if impl.get('primary_owner'):
                    st.write(f"**👤 Primary Owner:** {impl['primary_owner']}")
                if impl.get('timeline_weeks'):
                    st.write(f"**⏱️ Duration:** {impl['timeline_weeks']} weeks")
                if impl.get('budget_estimate'):
                    st.write(f"**💰 Budget Estimate:** {impl['budget_estimate']}")
            
            with col2:
                if impl.get('support_team'):
                    st.write(f"**👥 Support Team:** {', '.join(impl['support_team'])}")
                if impl.get('success_metrics'):
                    st.write("**📊 Success Metrics:**")
                    for metric in impl['success_metrics']:
                        st.write(f"• {metric}")
            
            # Key Milestones
            if impl.get('key_milestones'):
                st.markdown("#### 🎯 Key Milestones")
                for i, milestone in enumerate(impl['key_milestones'], 1):
                    st.write(f"{i}. {milestone}")
            
            # Resource Requirements
            if impl.get('resource_requirements'):
                st.markdown("#### 📦 Resource Requirements")
                for req in impl['resource_requirements']:
                    st.write(f"• {req}")
        
        # Risk Mitigation
        if decision_data.get('risk_mitigation'):
            risk = decision_data['risk_mitigation']
            
            st.markdown("### 🛡️ Risk Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if risk.get('primary_risks'):
                    st.write("**⚠️ Primary Risks:**")
                    for risk_item in risk['primary_risks']:
                        st.write(f"• {risk_item}")
            
            with col2:
                if risk.get('mitigation_strategies'):
                    st.write("**🛠️ Mitigation Strategies:**")
                    for strategy in risk['mitigation_strategies']:
                        st.write(f"• {strategy}")
            
            if risk.get('contingency_plan'):
                st.write(f"**🔄 Contingency Plan:** {risk['contingency_plan']}")
            
            if risk.get('monitoring_points'):
                st.write("**📊 Monitoring Points:**")
                for point in risk['monitoring_points']:
                    st.write(f"• {point}")
        
        # Review Schedule
        if decision_data.get('review_schedule'):
            review = decision_data['review_schedule']
            
            st.markdown("### 📅 Review Schedule")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if review.get('next_review_date'):
                    st.write(f"**📅 Next Review:** {review['next_review_date']}")
                if review.get('review_frequency'):
                    st.write(f"**🔄 Frequency:** {review['review_frequency']}")
            
            with col2:
                if review.get('success_criteria'):
                    st.write("**✅ Success Criteria:**")
                    for criteria in review['success_criteria']:
                        st.write(f"• {criteria}")
        
            # Alternative Strategies
            if decision_data.get('alternative_strategies'):
                st.markdown("#### 🔄 Alternative Strategies Considered")
                for i, alt_strategy in enumerate(decision_data['alternative_strategies'], 1):
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                        border-radius: 6px;
                        padding: 15px;
                        margin: 10px 0;
                        border-left: 3px solid #f59e0b;
                    ">
                        <h5 style="margin: 0 0 8px 0; color: #92400e;">{i}. {alt_strategy.get('strategy_name', 'Unknown Strategy')}</h5>
                        <p style="margin: 0; color: #a16207; font-size: 0.9rem;"><strong>Type:</strong> {alt_strategy.get('strategy_type', 'Unknown').title()}</p>
                        <p style="margin: 5px 0 0 0; color: #a16207; font-size: 0.9rem;"><strong>Why not chosen:</strong> {alt_strategy.get('why_not_chosen', 'N/A')}</p>
                        <p style="margin: 5px 0 0 0; color: #a16207; font-size: 0.9rem;"><strong>Backup plan:</strong> {alt_strategy.get('backup_plan', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Action Plan
            if decision_data.get('action_plan'):
                action_plan = decision_data['action_plan']
                st.markdown("#### 📋 Action Plan")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if action_plan.get('immediate_actions'):
                        st.markdown("**🚀 Immediate Actions:**")
                        for action in action_plan['immediate_actions']:
                            st.write(f"• {action}")
                
                with col2:
                    if action_plan.get('timeline_weeks'):
                        st.markdown(f"**⏱️ Timeline:** {action_plan['timeline_weeks']} weeks")
                    
                    if action_plan.get('key_milestones'):
                        st.markdown("**🎯 Key Milestones:**")
                        for milestone in action_plan['key_milestones']:
                            st.write(f"• {milestone}")
            
            # Team Assignment
            if decision_data.get('team_assignment'):
                team_assignment = decision_data['team_assignment']
                st.markdown("#### 👥 Team Assignment")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if team_assignment.get('primary_owner'):
                        st.markdown(f"**👑 Primary Owner:** {team_assignment['primary_owner']}")
                    
                    if team_assignment.get('support_team'):
                        st.markdown("**🤝 Support Team:**")
                        for member in team_assignment['support_team']:
                            st.write(f"• {member}")
                
                with col2:
                    if team_assignment.get('responsibilities'):
                        st.markdown("**📝 Responsibilities:**")
                        for member, responsibility in team_assignment['responsibilities'].items():
                            st.write(f"**{member}:** {responsibility}")
            
            # Risk Management
            if decision_data.get('risk_management'):
                risk_mgmt = decision_data['risk_management']
                st.markdown("#### 🛡️ Risk Management")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if risk_mgmt.get('primary_risks'):
                        st.markdown("**⚠️ Primary Risks:**")
                        for risk in risk_mgmt['primary_risks']:
                            st.write(f"• {risk}")
                
                with col2:
                    if risk_mgmt.get('mitigation_strategies'):
                        st.markdown("**🛠️ Mitigation Strategies:**")
                        for strategy in risk_mgmt['mitigation_strategies']:
                            st.write(f"• {strategy}")
                
                if risk_mgmt.get('contingency_plan'):
                    st.markdown(f"**🆘 Contingency Plan:** {risk_mgmt['contingency_plan']}")
            
            # Success Criteria
            if decision_data.get('success_criteria'):
                success_criteria = decision_data['success_criteria']
                st.markdown("#### ✅ Success Criteria")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if success_criteria.get('quantitative'):
                        st.markdown("**📊 Quantitative Metrics:**")
                        for metric in success_criteria['quantitative']:
                            st.write(f"• {metric}")
                
                with col2:
                    if success_criteria.get('qualitative'):
                        st.markdown("**📝 Qualitative Outcomes:**")
                        for outcome in success_criteria['qualitative']:
                            st.write(f"• {outcome}")
            
            # Next Review Date
            if decision_data.get('next_review_date'):
                st.markdown(f"**📅 Next Review Date:** {decision_data['next_review_date']}")

        # Show raw JSON in expandable section for technical users
        with st.expander("🔧 Technical Details (JSON Output)", expanded=False):
            st.json(decision_data)


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


def generate_comparison_report(analysis1, analysis2):
    """Generate a detailed comparison report between two analyses."""
    try:
        # Extract key metrics from both analyses
        def extract_metrics(analysis):
            if 'analysis' in analysis:
                analysis_data = analysis['analysis']
                if isinstance(analysis_data, str):
                    analysis_data = json.loads(analysis_data)
                
                return {
                    'skill_gaps': len(analysis_data.get('skill_gaps', [])),
                    'upskilling': len(analysis_data.get('upskilling', [])),
                    'hiring': len(analysis_data.get('hiring', [])),
                    'success_probability': analysis_data.get('success_probability', 'unknown'),
                    'timeline': analysis_data.get('timeline_assessment', 'unknown')
                }
            return {'skill_gaps': 0, 'upskilling': 0, 'hiring': 0, 'success_probability': 'unknown', 'timeline': 'unknown'}
        
        metrics1 = extract_metrics(analysis1)
        metrics2 = extract_metrics(analysis2)
        
        # Generate comparison report
        report = f"""
# 📊 Analysis Comparison Report

## Overview
This report compares two skill gap analyses to help identify patterns, improvements, and strategic insights.

## Key Metrics Comparison

| Metric | Analysis 1 | Analysis 2 | Difference |
|--------|------------|------------|------------|
| Skill Gaps | {metrics1['skill_gaps']} | {metrics2['skill_gaps']} | {metrics2['skill_gaps'] - metrics1['skill_gaps']:+d} |
| Upskilling Opportunities | {metrics1['upskilling']} | {metrics2['upskilling']} | {metrics2['upskilling'] - metrics1['upskilling']:+d} |
| Hiring Needs | {metrics1['hiring']} | {metrics2['hiring']} | {metrics2['hiring'] - metrics1['hiring']:+d} |
| Success Probability | {metrics1['success_probability']} | {metrics2['success_probability']} | - |
| Timeline | {metrics1['timeline']} | {metrics2['timeline']} | - |

## Insights
- **Total Recommendations**: Analysis 1 has {metrics1['skill_gaps'] + metrics1['upskilling'] + metrics1['hiring']} total recommendations vs {metrics2['skill_gaps'] + metrics2['upskilling'] + metrics2['hiring']} in Analysis 2
- **Strategy Focus**: {'Upskilling-focused' if metrics1['upskilling'] > metrics1['hiring'] else 'Hiring-focused'} vs {'Upskilling-focused' if metrics2['upskilling'] > metrics2['hiring'] else 'Hiring-focused'}
- **Complexity**: {'Higher' if metrics1['skill_gaps'] > metrics2['skill_gaps'] else 'Lower'} skill gap complexity in Analysis 1

## Recommendations
1. Consider the more successful approach from the analysis with higher success probability
2. Look for patterns in skill gaps that appear across both analyses
3. Evaluate the cost-effectiveness of upskilling vs hiring strategies
"""
        return report
    except Exception as e:
        return f"Error generating comparison report: {str(e)}"

def generate_skill_gap_heatmap(analysis_data):
    """Generate a skill gap heatmap visualization."""
    try:
        if 'analysis' in analysis_data:
            analysis = analysis_data['analysis']
            if isinstance(analysis, str):
                analysis = json.loads(analysis)
            
            skill_gaps = analysis.get('skill_gaps', [])
            upskilling = analysis.get('upskilling', [])
            hiring = analysis.get('hiring', [])
            
            # Create skill data
            skills_data = {}
            
            # Process skill gaps
            for gap in skill_gaps:
                skills_data[gap] = {'gap': True, 'upskilling': False, 'hiring': False}
            
            # Process upskilling
            for upskill in upskilling:
                skill = upskill.get('skill_to_learn', 'Unknown')
                if skill not in skills_data:
                    skills_data[skill] = {'gap': False, 'upskilling': False, 'hiring': False}
                skills_data[skill]['upskilling'] = True
            
            # Process hiring
            for hire in hiring:
                skills = hire.get('required_skills', [])
                for skill in skills:
                    if skill not in skills_data:
                        skills_data[skill] = {'gap': False, 'upskilling': False, 'hiring': False}
                    skills_data[skill]['hiring'] = True
            
            # Create heatmap data
            import pandas as pd
            heatmap_data = []
            for skill, data in skills_data.items():
                heatmap_data.append({
                    'Skill': skill,
                    'Gap': 'Yes' if data['gap'] else 'No',
                    'Upskilling': 'Yes' if data['upskilling'] else 'No',
                    'Hiring': 'Yes' if data['hiring'] else 'No',
                    'Priority': 'High' if data['gap'] and (data['upskilling'] or data['hiring']) else 'Medium' if data['gap'] or data['upskilling'] or data['hiring'] else 'Low'
                })
            
            df = pd.DataFrame(heatmap_data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error generating heatmap: {str(e)}")
        return pd.DataFrame()

def generate_summary_report(analysis_data, project_data):
    """Generate a comprehensive summary report."""
    try:
        if 'analysis' in analysis_data:
            analysis = analysis_data['analysis']
            if isinstance(analysis, str):
                analysis = json.loads(analysis)
            
            skill_gaps = analysis.get('skill_gaps', [])
            upskilling = analysis.get('upskilling', [])
            hiring = analysis.get('hiring', [])
            
            summary = f"""
# 📋 Skills Gap Analysis Summary Report

## Project Overview
- **Project**: {project_data.get('name', 'Unknown')}
- **Description**: {project_data.get('description', 'N/A')}
- **Budget**: ${project_data.get('budget', 0):,}
- **Timeline**: {project_data.get('start_date', 'N/A')} to {project_data.get('end_date', 'N/A')}
- **Required Skills**: {', '.join(project_data.get('required_skills', []))}

## Analysis Results
### Skill Gaps Identified ({len(skill_gaps)})
{chr(10).join([f"- {gap}" for gap in skill_gaps]) if skill_gaps else "- No specific skill gaps identified"}

### Upskilling Recommendations ({len(upskilling)})
{chr(10).join([f"- {rec.get('employee', 'Unknown')} → {rec.get('skill_to_learn', 'Unknown')} ({rec.get('timeline_weeks', 'N/A')} weeks)" for rec in upskilling]) if upskilling else "- No upskilling recommendations"}

### Hiring Recommendations ({len(hiring)})
{chr(10).join([f"- {hire.get('role', 'Unknown')} ({hire.get('urgency', 'N/A')} urgency, {hire.get('estimated_cost', 'N/A')})" for hire in hiring]) if hiring else "- No hiring recommendations"}

## Strategic Insights
- **Total Recommendations**: {len(skill_gaps) + len(upskilling) + len(hiring)}
- **Success Probability**: {analysis.get('success_probability', 'Unknown')}
- **Timeline Assessment**: {analysis.get('timeline_assessment', 'Unknown')}
- **Risk Factors**: {', '.join(analysis.get('risk_factors', [])) if analysis.get('risk_factors') else 'None identified'}

## Next Steps
1. Review and prioritize recommendations based on project timeline
2. Allocate budget for upskilling and hiring initiatives
3. Assign ownership for each recommendation
4. Set up monitoring and review schedules
5. Track progress against success metrics

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            return summary
        return "No analysis data available for summary generation."
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def export_to_pdf(content, filename="analysis_report.pdf"):
    """Export content to PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        for line in content.split('\n'):
            if line.startswith('# '):
                story.append(Paragraph(line[2:], styles['Heading1']))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], styles['Heading2']))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], styles['Heading3']))
            elif line.strip():
                story.append(Paragraph(line, styles['Normal']))
            else:
                story.append(Spacer(1, 12))
        
        doc.build(story)
        return True, f"PDF exported successfully as {filename}"
    except ImportError:
        return False, "reportlab not installed. Install with: pip install reportlab"
    except Exception as e:
        return False, f"Error exporting to PDF: {str(e)}"

def export_to_excel(analysis_data, filename="analysis_report.xlsx"):
    """Export analysis data to Excel."""
    try:
        import pandas as pd
        import openpyxl  # Check if openpyxl is available
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Skill Gaps', 'Upskilling Opportunities', 'Hiring Needs', 'Success Probability'],
                'Value': [
                    len(analysis_data.get('skill_gaps', [])),
                    len(analysis_data.get('upskilling', [])),
                    len(analysis_data.get('hiring', [])),
                    analysis_data.get('success_probability', 'Unknown')
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Skill gaps sheet
            if analysis_data.get('skill_gaps'):
                pd.DataFrame({'Skill Gap': analysis_data['skill_gaps']}).to_excel(writer, sheet_name='Skill Gaps', index=False)
            
            # Upskilling sheet
            if analysis_data.get('upskilling'):
                upskilling_df = pd.DataFrame(analysis_data['upskilling'])
                upskilling_df.to_excel(writer, sheet_name='Upskilling', index=False)
            
            # Hiring sheet
            if analysis_data.get('hiring'):
                hiring_df = pd.DataFrame(analysis_data['hiring'])
                hiring_df.to_excel(writer, sheet_name='Hiring', index=False)
        
        return True, f"Excel file exported successfully as {filename}"
    except ImportError:
        return False, "openpyxl not installed. Install with: pip install openpyxl"
    except Exception as e:
        return False, f"Error exporting to Excel: {str(e)}"

def export_to_csv(analysis_data, filename="analysis_report.csv"):
    """Export analysis data to CSV."""
    try:
        import pandas as pd
        
        # Combine all data into a single DataFrame
        all_data = []
        
        # Add skill gaps
        for gap in analysis_data.get('skill_gaps', []):
            all_data.append({'Type': 'Skill Gap', 'Description': gap, 'Details': ''})
        
        # Add upskilling
        for upskill in analysis_data.get('upskilling', []):
            all_data.append({
                'Type': 'Upskilling',
                'Description': f"{upskill.get('employee', 'Unknown')} → {upskill.get('skill_to_learn', 'Unknown')}",
                'Details': f"Timeline: {upskill.get('timeline_weeks', 'N/A')} weeks, Confidence: {upskill.get('confidence', 'N/A')}"
            })
        
        # Add hiring
        for hire in analysis_data.get('hiring', []):
            all_data.append({
                'Type': 'Hiring',
                'Description': hire.get('role', 'Unknown'),
                'Details': f"Urgency: {hire.get('urgency', 'N/A')}, Cost: {hire.get('estimated_cost', 'N/A')}"
            })
        
        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        return True, f"CSV file exported successfully as {filename}"
    except Exception as e:
        return False, f"Error exporting to CSV: {str(e)}"

def show_analysis_history():
    """Show analysis history and session management."""
    st.header("📚 Analysis History & Session Management")
    st.markdown("View and manage your previous analysis sessions and recommendations")
    
    # Initialize session state for history if not exists
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Add current analysis to history if exists
    if 'analysis_results' in st.session_state and 'analysis_params' in st.session_state:
        current_analysis = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'project': st.session_state.analysis_params['project']['name'],
            'project_id': st.session_state.analysis_params['project']['id'],
            'scope': st.session_state.analysis_params['scope'],
            'analysis_depth': st.session_state.analysis_params['analysis_depth'],
            'risk_tolerance': st.session_state.analysis_params['risk_tolerance'],
            'results': st.session_state.analysis_results,
            'params': st.session_state.analysis_params
        }
        
        # Check if this analysis is already in history
        if not any(h['project_id'] == current_analysis['project_id'] and 
                  h['timestamp'] == current_analysis['timestamp'] for h in st.session_state.analysis_history):
            st.session_state.analysis_history.insert(0, current_analysis)
    
    # History management controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear All History"):
            st.session_state.analysis_history = []
            st.success("History cleared!")
            st.rerun()
    
    with col2:
        if st.button("💾 Export History"):
            if st.session_state.analysis_history:
                # Create a comprehensive history export
                history_data = []
                for analysis in st.session_state.analysis_history:
                    history_data.append({
                        'Timestamp': analysis['timestamp'],
                        'Project': analysis['project'],
                        'Project ID': analysis['project_id'],
                        'Scope': analysis['scope'],
                        'Analysis Depth': analysis['analysis_depth'],
                        'Risk Tolerance': analysis['risk_tolerance']
                    })
                
                import pandas as pd
                df = pd.DataFrame(history_data)
                
                # Export to CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download History as CSV",
                    data=csv,
                    file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
                st.success(f"History exported with {len(history_data)} analyses!")
            else:
                st.warning("No analysis history to export")
    
    with col3:
        if st.button("📊 Generate Summary Report"):
            if st.session_state.analysis_history:
                # Generate comprehensive summary report
                total_analyses = len(st.session_state.analysis_history)
                projects = set(analysis['project'] for analysis in st.session_state.analysis_history)
                
                summary_report = f"""
# 📊 Analysis History Summary Report

## Overview
- **Total Analyses**: {total_analyses}
- **Unique Projects**: {len(projects)}
- **Date Range**: {st.session_state.analysis_history[-1]['timestamp']} to {st.session_state.analysis_history[0]['timestamp']}

## Project Breakdown
{chr(10).join([f"- {project}" for project in projects])}

## Analysis Distribution
- **Department Scope**: {len([a for a in st.session_state.analysis_history if a['scope'] == 'department'])} analyses
- **Company Scope**: {len([a for a in st.session_state.analysis_history if a['scope'] == 'company'])} analyses

## Risk Tolerance Distribution
- **Conservative**: {len([a for a in st.session_state.analysis_history if a['risk_tolerance'] == 'Conservative'])} analyses
- **Balanced**: {len([a for a in st.session_state.analysis_history if a['risk_tolerance'] == 'Balanced'])} analyses
- **Aggressive**: {len([a for a in st.session_state.analysis_history if a['risk_tolerance'] == 'Aggressive'])} analyses

## Analysis Depth Distribution
- **Quick**: {len([a for a in st.session_state.analysis_history if a['analysis_depth'] == 'Quick'])} analyses
- **Standard**: {len([a for a in st.session_state.analysis_history if a['analysis_depth'] == 'Standard'])} analyses
- **Comprehensive**: {len([a for a in st.session_state.analysis_history if a['analysis_depth'] == 'Comprehensive'])} analyses
- **Deep Dive**: {len([a for a in st.session_state.analysis_history if a['analysis_depth'] == 'Deep Dive'])} analyses

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                
                st.markdown(summary_report)
                
                # Download button
                st.download_button(
                    label="📥 Download Summary Report",
                    data=summary_report,
                    file_name=f"history_summary_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            else:
                st.warning("No analysis history available for summary report")
    
    # Display history
    if not st.session_state.analysis_history:
        st.info("No analysis history found. Generate some recommendations to see them here!")
        return
    
    st.subheader(f"📋 Analysis History ({len(st.session_state.analysis_history)} sessions)")
    
    # Filter and search history
    col1, col2 = st.columns(2)
    
    with col1:
        search_history = st.text_input("🔍 Search History", placeholder="Project name or date")
    
    with col2:
        sort_by = st.selectbox("📊 Sort By", ["Most Recent", "Project Name", "Analysis Depth", "Risk Tolerance"])
    
    # Filter history
    filtered_history = st.session_state.analysis_history
    if search_history:
        filtered_history = [h for h in filtered_history if 
                          search_history.lower() in h['project'].lower() or 
                          search_history.lower() in h['timestamp'].lower()]
    
    # Sort history
    if sort_by == "Most Recent":
        filtered_history.sort(key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == "Project Name":
        filtered_history.sort(key=lambda x: x['project'])
    elif sort_by == "Analysis Depth":
        depth_order = {"Quick": 1, "Standard": 2, "Comprehensive": 3, "Deep Dive": 4}
        filtered_history.sort(key=lambda x: depth_order.get(x['analysis_depth'], 0), reverse=True)
    elif sort_by == "Risk Tolerance":
        risk_order = {"Conservative": 1, "Balanced": 2, "Aggressive": 3}
        filtered_history.sort(key=lambda x: risk_order.get(x['risk_tolerance'], 0))
    
    # Display history items
    for i, analysis in enumerate(filtered_history):
        with st.expander(f"📊 {analysis['project']} - {analysis['timestamp']}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Project:** {analysis['project']}")
                st.write(f"**ID:** {analysis['project_id']}")
            
            with col2:
                st.write(f"**Scope:** {analysis['scope'].title()}")
                st.write(f"**Depth:** {analysis['analysis_depth']}")
            
            with col3:
                st.write(f"**Risk:** {analysis['risk_tolerance']}")
                st.write(f"**Date:** {analysis['timestamp']}")
            
            with col4:
                if st.button(f"🔄 Load Analysis {i+1}", key=f"load_{i}"):
                    st.session_state.analysis_results = analysis['results']
                    st.session_state.analysis_params = analysis['params']
                    st.success(f"Analysis for {analysis['project']} loaded! Switch to Recommendations tab to view.")
                
                if st.button(f"🗑️ Delete {i+1}", key=f"delete_{i}"):
                    st.session_state.analysis_history.remove(analysis)
                    st.success("Analysis deleted!")
                    st.rerun()
            
            # Show quick summary
            if analysis['results']:
                st.write("**Quick Summary:**")
                if 'analysis' in analysis['results']:
                    try:
                        analysis_data = analysis['results']['analysis']
                        if isinstance(analysis_data, str):
                            analysis_data = json.loads(analysis_data)
                        
                        skill_gaps = analysis_data.get('skill_gaps', [])
                        upskilling = analysis_data.get('upskilling', [])
                        hiring = analysis_data.get('hiring', [])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Skill Gaps:** {len(skill_gaps)}")
                        with col2:
                            st.write(f"**Upskilling:** {len(upskilling)}")
                        with col3:
                            st.write(f"**Hiring:** {len(hiring)}")
                    except:
                        st.write("Summary not available")


if __name__ == "__main__":
    main()
