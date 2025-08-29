# """
# Streamlit App for GapLens Skills Analysis System
# """

# import streamlit as st
# import requests
# import json
# from datetime import datetime, date
# from typing import Dict, List, Any
# import pandas as pd
# import os
# from pathlib import Path
# import sys
# import io
# from contextlib import redirect_stdout, redirect_stderr

# # Load environment variables from .env file
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except ImportError:
#     st.warning("python-dotenv not installed. Install with: pip install python-dotenv")

# # Page configuration
# st.set_page_config(
#     page_title="GapLens Skills Analysis",
#     page_icon="🔍",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # API configuration
# API_BASE_URL = "http://localhost:8000"

# # Memory system paths
# MEMORY_BASE_PATH = Path("infrastructure/memory")
# SESSIONS_PATH = MEMORY_BASE_PATH / "sessions"
# LOGS_PATH = MEMORY_BASE_PATH / "logs"

# def safe_content_display(content, max_length=500):
#     """Safely display content with proper type handling and length limiting."""
#     try:
#         if isinstance(content, str):
#             return content[:max_length] + "..." if len(content) > max_length else content
#         else:
#             content_str = str(content)
#             return content_str[:max_length] + "..." if len(content_str) > max_length else content_str
#     except Exception:
#         return str(content)[:max_length] + "..." if len(str(content)) > max_length else str(content)

# def check_api_connection():
#     """Check if the FastAPI backend is running."""
#     try:
#         response = requests.get(f"{API_BASE_URL}/", timeout=5)
#         return response.status_code == 200
#     except:
#         return False

# def get_api_data(endpoint: str) -> Dict[str, Any]:
#     """Get data from the FastAPI backend."""
#     try:
#         response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": f"API Error: {response.status_code}"}
#     except Exception as e:
#         return {"error": f"Connection Error: {str(e)}"}

# def load_session_data(session_id: str = None) -> Dict[str, Any]:
#     """Load session data from memory system."""
#     try:
#         if not SESSIONS_PATH.exists():
#             return {}
        
#         if session_id:
#             session_file = SESSIONS_PATH / f"{session_id}.json"
#             if session_file.exists():
#                 with open(session_file, 'r') as f:
#                     return json.load(f)
        
#         # Load most recent session
#         session_files = list(SESSIONS_PATH.glob("*.json"))
#         if session_files:
#             latest_file = max(session_files, key=lambda x: x.stat().st_mtime)
#             with open(latest_file, 'r') as f:
#                 return json.load(f)
        
#         return {}
#     except Exception as e:
#         st.error(f"Error loading session data: {e}")
#         return {}

# def get_reasoning_patterns() -> List[str]:
#     """Get available reasoning patterns."""
#     return ["REWOO", "REACT", "COT", "TOT", "AGENT"]

# def main():
#     """Main Streamlit application."""
#     st.title("🔍 GapLens Skills Analysis System")
#     st.markdown("AI-powered skills gap analysis and team optimization")
    
#     # Check API connection
#     if not check_api_connection():
#         st.error("❌ FastAPI backend is not running. Please start the backend server first.")
#         st.info("Run: `cd infrastructure && python api.py`")
#         return
    
#     # Sidebar navigation
#     st.sidebar.title("Navigation")
#     page = st.sidebar.selectbox(
#         "Choose a page:",
#         ["Dashboard", "AI Workflow", "Department Overview", "Project Analysis", "Team Skills", "Employee Database", "Recommendations"]
#     )
    
#     if page == "Dashboard":
#         show_dashboard()
#     elif page == "AI Workflow":
#         show_ai_workflow()
#     elif page == "Department Overview":
#         show_department_overview()
#     elif page == "Project Analysis":
#         show_project_analysis()
#     elif page == "Team Skills":
#         show_team_skills()
#     elif page == "Employee Database":
#         show_employee_database()
#     elif page == "Recommendations":
#         show_recommendations()

# def show_dashboard():
#     """Show the main dashboard."""
#     st.header(" Dashboard")
    
#     # Get summary data
#     projects_data = get_api_data("/api/projects")
#     employees_data = get_api_data("/api/employees")
#     teams_data = get_api_data("/api/teams")
#     departments_data = get_api_data("/api/departments")
    
#     # Create metrics
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         if "error" not in projects_data:
#             st.metric("Active Projects", len(projects_data))
#         else:
#             st.metric("Active Projects", "N/A")
   
#     with col2:
#         if "error" not in employees_data:
#             st.metric("Team Members", len(employees_data))
#         else:
#             st.metric("Team Members", "N/A")
   
#     with col3:
#         if "error" not in teams_data:
#             st.metric("Teams", len(teams_data))
#         else:
#             st.metric("Teams", "N/A")
   
#     with col4:
#         if "error" not in departments_data:
#             st.metric("Departments", departments_data.get("total_departments", "N/A"))
#         else:
#             st.metric("Departments", "N/A")
   
#     # Department breakdown
#     if "error" not in departments_data:
#         st.subheader(" Department Breakdown")
#         dept_cols = st.columns(len(departments_data.get("departments", {})))
        
#         for i, (dept_name, dept_info) in enumerate(departments_data.get("departments", {}).items()):
#             with dept_cols[i]:
#                 st.metric(dept_name, dept_info["count"])
   
#     # Recent projects
#     st.subheader(" Recent Projects")
#     if "error" not in projects_data:
#         projects_df = pd.DataFrame(projects_data)
#         st.dataframe(projects_df[["name", "status", "priority", "start_date", "budget"]], use_container_width=True)
#     else:
#         st.error("Failed to load projects data")

# def show_project_analysis():
#     """Show detailed project analysis."""
#     st.header(" Project Analysis")
    
#     projects_data = get_api_data("/api/projects")
#     if "error" in projects_data:
#         st.error("Failed to load projects data")
#         return
    
#     # Project selection
#     selected_project = st.selectbox(
#         "Select a project:",
#         projects_data,
#         format_func=lambda x: x["name"]
#     )
    
#     if selected_project:
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             st.subheader("Project Details")
#             st.write(f"**Name:** {selected_project['name']}")
#             st.write(f"**Description:** {selected_project['description']}")
#             st.write(f"**Timeline:** {selected_project['start_date']} to {selected_project['end_date']}")
#             st.write(f"**Budget:** ${selected_project['budget']:,}")
#             st.write(f"**Priority:** {selected_project['priority']}")
#             st.write(f"**Status:** {selected_project['status']}")
        
#         with col2:
#             st.subheader("Required Skills")
#             for skill in selected_project["required_skills"]:
#                 st.write(f"• {skill}")
        
#         # AI Reasoning Analysis
#         st.subheader(" AI-Powered Skills Analysis")
        
#         # Scope selection
#         scope = st.radio(
#             "Analysis Scope:",
#             ["Department Only", "Full Company"],
#             help="Department: Analyze skills within the project team's department only. Full Company: Consider all company skills."
#         )
        
#         scope_param = "department" if scope == "Department Only" else "company"
        
#         if st.button(" Analyze with AI Agents"):
#             with st.spinner(" AI agents are analyzing your project..."):
#                 try:
#                     # Import the latest workflow system
#                     from core.workflow import MultiAgentWorkflow
#                     from core import make_llm, make_reasoner
                    
#                     # Create LLMs with anthropic backend
#                     perception_llm = make_llm("anthropic")
#                     reasoner_llm = make_reasoner("anthropic")
                    
#                     # Prepare the analysis question
#                     analysis_question = f"Do we have enough skilled people to do this project?\n\nContext:\nProject: {selected_project['name']} - {selected_project['description']}\nRequired skills: {', '.join(selected_project['required_skills'])}\nTimeline: {selected_project['start_date']} to {selected_project['end_date']}\nBudget: ${selected_project['budget']:,}\nScope: {scope_param}"
                    
#                     # Show the analysis question
#                     st.subheader(" Analysis Question")
#                     st.write(analysis_question)
                    
#                     # Create and run the multi-agent workflow
#                     st.subheader(" Multi-Agent Workflow Execution")
                    
#                     try:
#                         # Initialize the workflow
#                         workflow = MultiAgentWorkflow(perception_llm, reasoner_llm)
                        
#                         # Run the complete workflow
#                         with st.expander(" Workflow Execution Details", expanded=True):
#                             st.write("**Running LangGraph-based multi-agent workflow...**")
#                             st.write("This workflow uses the latest agent architecture with:")
#                             st.write("• Perception Agent (REACT reasoning)")
#                             st.write("• Analysis Agent (REACT reasoning)")
#                             st.write("• Decision Agent (TOT reasoning)")
#                             st.write("• Orchestrator Agent (workflow management)")
                        
#                         # Execute the workflow
#                         result = workflow.run(analysis_question, verbose=True)
                        
#                         # Display results
#                         st.success(" AI Analysis Complete!")
                        
#                         # Show workflow summary
#                         st.subheader(" Workflow Summary")
#                         col1, col2, col3, col4 = st.columns(4)
                        
#                         with col1:
#                             st.metric("Intent", result.get('intent', 'Unknown'))
#                         with col2:
#                             st.metric("Entities", len(result.get('entities', [])))
#                         with col3:
#                             st.metric("Analysis", "✓" if result.get('analysis') else "✗")
#                         with col4:
#                             st.metric("Decision", "✓" if result.get('decision') else "✗")
                        
#                         # Show detailed results
#                         if result.get('analysis'):
#                             st.subheader(" Analysis Results")
#                             st.write(result['analysis'])
                        
#                         if result.get('decision'):
#                             st.subheader(" Final Recommendations")
#                             st.write(result['decision'])
                        
#                         # Show workflow state
#                         st.subheader(" Workflow State")
#                         st.json(result)
                        
#                     except Exception as e:
#                         st.error(f" Error running workflow: {e}")
#                         st.info(" Check the terminal for detailed workflow execution logs")
                    
#                 except Exception as e:
#                     st.error(f" Error running AI analysis: {e}")
#                     st.info(" Make sure you have the ANTHROPIC_API_KEY set in your environment")
        
#         # Skills gap analysis (basic)
#         st.subheader(" Basic Skills Gap Analysis")
#         if st.button("Analyze Skills Gap"):
#             with st.spinner("Analyzing..."):
#                 gap_analysis = get_api_data(f"/api/analysis/skill-gaps?project_id={selected_project['id']}")
#                 if "error" not in gap_analysis:
#                     display_skills_gap_analysis(gap_analysis)
#                 else:
#                     st.error("Failed to analyze skills gap")

# def show_team_skills():
#     """Show team skills overview."""
#     st.header(" Team Skills Overview")
    
#     teams_data = get_api_data("/api/teams")
#     employees_data = get_api_data("/api/employees")
    
#     if "error" in teams_data or "error" in employees_data:
#         st.error("Failed to load team or employee data")
#         return
    
#     # Team selection
#     selected_team = st.selectbox(
#         "Select a team:",
#         teams_data,
#         format_func=lambda x: x["name"]
#     )
    
#     if selected_team:
#         st.subheader(f"Team: {selected_team['name']}")
        
#         # Team members
#         team_members = [emp for emp in employees_data if emp["id"] in selected_team["members"]]
        
#         # Skills coverage
#         st.write("**Skills Coverage:**")
#         for skill, count in selected_team["skills_coverage"].items():
#             st.write(f"• {skill}: {count} team member(s)")
        
#         # Cross-department collaboration
#         st.subheader(" Cross-Department Collaboration")
#         dept_counts = {}
#         for member in team_members:
#             dept = member["department"]
#             dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
#         if len(dept_counts) > 1:
#             st.success(f"This team collaborates across {len(dept_counts)} departments!")
#             for dept, count in dept_counts.items():
#                 st.write(f"• {dept}: {count} member(s)")
#         else:
#             st.info("This is a single-department team")
        
#         # Department-specific skills analysis
#         st.subheader(" Department Skills Analysis")
        
#         # Get skills by department
#         dept_skills = {}
#         for member in team_members:
#             dept = member["department"]
#             if dept not in dept_skills:
#                 dept_skills[dept] = set()
#             for skill in member["skills"]:
#                 skill_name = skill["name"] if isinstance(skill, dict) else skill
#                 dept_skills[dept].add(skill_name)
        
#         # Show skills by department
#         for dept, skills in dept_skills.items():
#             with st.expander(f" {dept} Department Skills ({len(skills)} skills)"):
#                 # Sort skills alphabetically
#                 sorted_skills = sorted(skills)
#                 for skill in sorted_skills:
#                     st.write(f"• {skill}")
        
#         # Team member details
#         st.subheader("Team Members")
#         for member in team_members:
#             with st.expander(f"{member['name']} - {member['role']} ({member['department']})"):
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.write(f"**Department:** {member['department']}")
#                     st.write(f"**Experience:** {member['experience_years']} years")
#                     st.write(f"**Availability:** {member['availability']}")
#                     st.write(f"**Upskilling Capacity:** {member['upskilling_capacity']}")
#                 with col2:
#                     st.write("**Skills:**")
#                     for skill in member["skills"]:
#                         if isinstance(skill, dict):
#                             # Color code skill levels
#                             level = skill['level']
#                             if level == "expert":
#                                 st.write(f" {skill['name']} ({level})")
#                             elif level == "advanced":
#                                 st.write(f" {skill['name']} ({level})")
#                             elif level == "intermediate":
#                                 st.write(f" {skill['name']} ({level})")
#                             else:
#                                 st.write(f" {skill['name']} ({level})")
#                         else:
#                             st.write(f"• {skill}")
        
#         # Team skill gaps analysis
#         st.subheader(" Team Skill Analysis")
        
#         # Get all skills from team members
#         team_skills = set()
#         for member in team_members:
#             for skill in member["skills"]:
#                 skill_name = skill["name"] if isinstance(skill, dict) else skill
#                 team_skills.add(skill_name)
        
#         # Show skill distribution by level
#         skill_levels = {}
#         for member in team_members:
#             for skill in member["skills"]:
#                 if isinstance(skill, dict):
#                     skill_name = skill["name"]
#                     level = skill["level"]
#                     if skill_name not in skill_levels:
#                         skill_levels[skill_name] = {"expert": 0, "advanced": 0, "intermediate": 0, "beginner": 0}
#                     skill_levels[skill_name][level] += 1
        
#         if skill_levels:
#             st.write("**Skill Distribution by Level:**")
#             for skill_name, levels in skill_levels.items():
#                 total = sum(levels.values())
#                 if total > 1:  # Only show skills with multiple people
#                     st.write(f"**{skill_name}** ({total} people):")
#                     for level, count in levels.items():
#                         if count > 0:
#                             st.write(f"  {level.title()}: {count}")
        
#         # Team recommendations
#         st.subheader(" Team Recommendations")
        
#         # Identify potential skill gaps
#         if len(team_members) < 5:
#             st.info("Consider expanding the team for better skill coverage")
        
#         # Check for skill concentration
#         for skill, count in selected_team["skills_coverage"].items():
#             if count == 1:
#                 st.warning(f" {skill} has only 1 team member - consider cross-training")
        
#         # Suggest upskilling opportunities
#         high_capacity_members = [m for m in team_members if m["upskilling_capacity"] == "high"]
#         if high_capacity_members:
#             st.success(f" {len(high_capacity_members)} team members have high upskilling capacity")
#             for member in high_capacity_members:
#                 st.write(f"• {member['name']} can learn new skills quickly")
        
#         # Department-specific recommendations
#         st.subheader(" Department-Specific Insights")
        
#         # Analyze each department's contribution
#         for dept, skills in dept_skills.items():
#             dept_members = [m for m in team_members if m["department"] == dept]
#             if dept_members:
#                 with st.expander(f" {dept} Department Analysis"):
#                     st.write(f"**Members:** {len(dept_members)}")
#                     st.write(f"**Unique Skills:** {len(skills)}")
                    
#                     # Show top skills for this department
#                     st.write("**Key Skills:**")
#                     for skill in sorted(skills)[:5]:  # Show top 5
#                         st.write(f"• {skill}")
                    
#                     # Suggest cross-training opportunities
#                     if len(dept_members) > 1:
#                         st.info("Consider cross-training team members to share knowledge")
                    
#                     # Identify skill gaps within department
#                     if len(skills) < 10:  # Arbitrary threshold
#                         st.warning("Department has limited skill diversity - consider upskilling")

# def show_employee_database():
#     """Show employee database."""
#     st.header(" Employee Database")
    
#     employees_data = get_api_data("/api/employees")
#     if "error" in employees_data:
#         st.error("Failed to load employee data")
#         return
    
#     # Enhanced search and filter
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         search_term = st.text_input("Search employees:", placeholder="Name, role, or skill")
#     with col2:
#         department_filter = st.selectbox(
#             "Filter by department:",
#             ["All"] + list(set(emp["department"] for emp in employees_data))
#         )
#     with col3:
#         experience_filter = st.selectbox(
#             "Filter by experience level:",
#             ["All", "Junior (0-3 years)", "Mid (3-6 years)", "Senior (6+ years)"]
#         )
    
#     # Filter employees
#     filtered_employees = employees_data
#     if search_term:
#         filtered_employees = [
#             emp for emp in filtered_employees
#             if (search_term.lower() in emp["name"].lower() or
#                 search_term.lower() in emp["role"].lower() or
#                 any(search_term.lower() in skill["name"].lower() if isinstance(skill, dict) else search_term.lower() in skill.lower() 
#                     for skill in emp["skills"]))
#         ]
    
#     if department_filter != "All":
#         filtered_employees = [emp for emp in filtered_employees if emp["department"] == department_filter]
    
#     if experience_filter != "All":
#         if experience_filter == "Junior (0-3 years)":
#             filtered_employees = [emp for emp in filtered_employees if emp["experience_years"] < 3]
#         elif experience_filter == "Mid (3-6 years)":
#             filtered_employees = [emp for emp in filtered_employees if 3 <= emp["experience_years"] < 6]
#         elif experience_filter == "Senior (6+ years)":
#             filtered_employees = [emp for emp in filtered_employees if emp["experience_years"] >= 6]
    
#     # Display employees
#     st.write(f"**Found {len(filtered_employees)} employees**")
    
#     # Skills summary for filtered employees
#     if filtered_employees:
#         all_skills = {}
#         for emp in filtered_employees:
#             for skill in emp["skills"]:
#                 skill_name = skill["name"] if isinstance(skill, dict) else skill
#                 if skill_name not in all_skills:
#                     all_skills[skill_name] = {"count": 0, "levels": {}}
#                 all_skills[skill_name]["count"] += 1
                
#                 if isinstance(skill, dict):
#                     level = skill["level"]
#                     if level not in all_skills[skill_name]["levels"]:
#                         all_skills[skill_name]["levels"][level] = 0
#                     all_skills[skill_name]["levels"][level] += 1
    
#         # Show top skills
#         if all_skills:
#             st.subheader(" Skills Summary (Filtered Results)")
#             top_skills = sorted(all_skills.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
            
#             for skill_name, skill_info in top_skills:
#                 st.write(f"**{skill_name}**: {skill_info['count']} employees")
#                 if skill_info["levels"]:
#                     level_str = ", ".join([f"{level}: {count}" for level, count in skill_info["levels"].items()])
#                     st.write(f"  Levels: {level_str}")
    
#     # Employee details
#     for emp in filtered_employees:
#         with st.expander(f"{emp['name']} - {emp['role']} ({emp['department']})"):
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.write(f"**Experience:** {emp['experience_years']} years")
#                 st.write(f"**Location:** {emp['location']}")
#                 st.write(f"**Salary Range:** {emp['salary_range']}")
#                 st.write(f"**Upskilling Capacity:** {emp['upskilling_capacity']}")
                
#                 # Experience level indicator
#                 if emp['experience_years'] < 3:
#                     st.info(" Junior Level")
#                 elif emp['experience_years'] < 6:
#                     st.warning(" Mid Level")
#                 else:
#                     st.success(" Senior Level")
            
#             with col2:
#                 st.write("**Skills:**")
#                 for skill in emp["skills"]:
#                     if isinstance(skill, dict):
#                         # Color code skill levels
#                         level = skill['level']
#                         if level == "expert":
#                             st.write(f" {skill['name']} ({level}, {skill['years_experience']} years)")
#                         elif level == "advanced":
#                             st.write(f" {skill['name']} ({level}, {skill['years_experience']} years)")
#                         elif level == "intermediate":
#                             st.write(f" {skill['name']} ({level}, {skill['years_experience']} years)")
#                         else:
#                             st.write(f" {skill['name']} ({level}, {skill['years_experience']} years)")
#                     else:
#                         st.write(f"• {skill}")

# def show_ai_workflow():
#     """Show AI-powered project analysis using the multi-agent workflow."""
#     st.header(" AI-Powered Project Analysis")
    
#     st.info("This section runs the multi-agent workflow directly to analyze project skill requirements and team capabilities.")
    
#     # Debug: Show environment variables
#     with st.expander(" Debug: Environment Variables", expanded=False):
#         st.write("**ANTHROPIC_API_KEY:**", " Set" if os.getenv("ANTHROPIC_API_KEY") else " Not Set")
#         if os.getenv("ANTHROPIC_API_KEY"):
#             st.write("**Key length:**", len(os.getenv("ANTHROPIC_API_KEY")))
#             st.write("**Key preview:**", os.getenv("ANTHROPIC_API_KEY")[:20] + "..." if len(os.getenv("ANTHROPIC_API_KEY")) > 20 else "Full key shown")
#         st.write("**Current working directory:**", os.getcwd())
#         st.write("**Python path:**", os.environ.get("PYTHONPATH", "Not set"))
        
#         # Manual API key input as fallback
#         if not os.getenv("ANTHROPIC_API_KEY"):
#             st.warning(" ANTHROPIC_API_KEY not found in environment. You can manually enter it below:")
#             manual_key = st.text_input("Enter Anthropic API Key:", type="password", help="Enter your Anthropic API key if .env file is not loading")
#             if manual_key:
#                 os.environ["ANTHROPIC_API_KEY"] = manual_key
#                 st.success(" API key set manually")
#                 st.rerun()
    
#     # Project selection
#     projects_data = get_api_data("/api/projects")
#     if "error" in projects_data:
#         st.error("Failed to load projects data")
#         return
    
#     if not projects_data:
#         st.warning("No projects available for analysis")
#         return
    
#     selected_project = st.selectbox(
#         "Select a project to analyze:",
#         projects_data,
#         format_func=lambda x: f"{x['name']} ({x['status']})"
#     )
    
#     if selected_project:
#         st.subheader(f" Project: {selected_project['name']}")
        
#         # Show project details
#         col1, col2 = st.columns(2)
#         with col1:
#             st.write(f"**Description:** {selected_project['description']}")
#             st.write(f"**Timeline:** {selected_project['start_date']} to {selected_project['end_date']}")
#             st.write(f"**Budget:** ${selected_project['budget']:,}")
       
#         with col2:
#             st.write(f"**Priority:** {selected_project['priority']}")
#             st.write(f"**Status:** {selected_project['status']}")
#             st.write("**Required Skills:**")
#             for skill in selected_project["required_skills"]:
#                 st.write(f"• {skill}")
        
#         # Analysis options
#         st.subheader(" Analysis Options")
        
#         analysis_type = st.selectbox(
#             "What would you like to analyze?",
#             [
#                 "Do we have enough skilled people to do this project?",
#                 "What are the skill gaps for this project?",
#                 "How can we optimize team composition for this project?",
#                 "What upskilling is needed for this project?",
#                 "Custom analysis..."
#             ]
#         )
        
#         custom_prompt = ""
#         if analysis_type == "Custom analysis...":
#             custom_prompt = st.text_area(
#                 "Enter your custom analysis question:",
#                 placeholder="e.g., Can we complete this project with our current team within the timeline?",
#                 height=100
#             )
#             analysis_type = custom_prompt if custom_prompt else "Do we have enough skilled people to do this project?"
        
#         # Scope selection
#         scope = st.radio(
#             "Analysis Scope:",
#             ["Department Only", "Full Company"],
#             help="Department: Analyze skills within the project team's department only. Full Company: Consider all company skills."
#         )
        
#         if st.button(" Run AI Analysis", type="primary"):
#             if not custom_prompt and analysis_type == "Custom analysis...":
#                 st.error("Please enter a custom analysis question")
#                 return
            
#             # Prepare the analysis question
#             project_context = f"Project: {selected_project['name']} - {selected_project['description']}"
#             project_skills = f"Required skills: {', '.join(selected_project['required_skills'])}"
#             project_timeline = f"Timeline: {selected_project['start_date']} to {selected_project['end_date']}"
#             project_budget = f"Budget: ${selected_project['budget']:,}"
            
#             analysis_question = f"{analysis_type}\n\nContext:\n{project_context}\n{project_skills}\n{project_timeline}\n{project_budget}\nScope: {scope}"
            
#             # Run the multi-agent workflow
#             with st.spinner(" AI agents are analyzing your project..."):
#                 try:
#                     # Import the latest workflow system
#                     from core.workflow import MultiAgentWorkflow
#                     from core import make_llm, make_reasoner
                    
#                     # Create LLMs with anthropic backend
#                     perception_llm = make_llm("anthropic")
#                     reasoner_llm = make_reasoner("anthropic")
                    
#                     # Show the analysis question
#                     st.subheader(" Analysis Question")
#                     st.write(analysis_question)
                    
#                     # Create and run the multi-agent workflow
#                     st.subheader(" Multi-Agent Workflow Execution")
                    
#                     try:
#                         # Initialize the workflow
#                         workflow = MultiAgentWorkflow(perception_llm, reasoner_llm)
                        
#                         # Run the complete workflow
#                         with st.expander(" Workflow Execution Details", expanded=True):
#                             st.write("**Running LangGraph-based multi-agent workflow...**")
#                             st.write("This workflow uses the latest agent architecture with:")
#                             st.write("• Perception Agent (REACT reasoning)")
#                             st.write("• Analysis Agent (REACT reasoning)")
#                             st.write("• Decision Agent (TOT reasoning)")
#                             st.write("• Orchestrator Agent (workflow management)")
                        
#                         # Execute the workflow
#                         result = workflow.run(analysis_question, verbose=True)
                        
#                         # Display results
#                         st.success(" AI Analysis Complete!")
                        
#                         # Show workflow summary
#                         st.subheader(" Workflow Summary")
#                         col1, col2, col3, col4 = st.columns(4)
                        
#                         with col1:
#                             st.metric("Intent", result.get('intent', 'Unknown'))
#                         with col2:
#                             st.metric("Entities", len(result.get('entities', [])))
#                         with col3:
#                             st.metric("Analysis", "✓" if result.get('analysis') else "✗")
#                         with col4:
#                             st.metric("Decision", "✓" if result.get('decision') else "✗")
                        
#                         # Show detailed results
#                         if result.get('analysis'):
#                             st.subheader(" Analysis Results")
#                             st.write(result['analysis'])
                        
#                         if result.get('decision'):
#                             st.subheader(" Final Recommendations")
#                             st.write(result['decision'])
                        
#                         # Show workflow state
#                         st.subheader(" Workflow State")
#                         st.json(result)
                        
#                     except Exception as e:
#                         st.error(f" Error running workflow: {e}")
#                         st.info(" Check the terminal for detailed workflow execution logs")
                    
#                 except Exception as e:
#                     st.error(f" Error running AI analysis: {e}")
#                     st.info(" Make sure you have the ANTHROPIC_API_KEY set in your environment")

# def show_recommendations():
#     """Show AI-generated recommendations using direct workflow execution."""
#     st.header("🎯 AI Recommendations")
    
#     st.info("This section runs the AI workflow directly and shows all LLM reasoning in the terminal.")
    
#     # Project selection
#     st.header("📋 Select Project for Analysis")
    
#     projects_data = get_api_data("/api/projects")
#     if "error" in projects_data:
#         st.error("Failed to load projects data")
#         return
    
#     if not projects_data:
#         st.warning("No projects available for analysis")
#         return
    
#     # Project selection with better formatting
#     selected_project = st.selectbox(
#         "Choose a project to analyze:",
#         projects_data,
#         format_func=lambda x: f"{x['name']} - {x['status']} (${x['budget']:,})"
#     )
    
#     if selected_project:
#         # Display project details
#         st.subheader("📊 Project Details")
        
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             st.write(f"**Project Name:** {selected_project['name']}")
#             st.write(f"**Description:** {selected_project['description']}")
            
#             # Format dates properly
#             try:
#                 if isinstance(selected_project['start_date'], str):
#                     start_date = datetime.strptime(selected_project['start_date'], '%Y-%m-%d').strftime('%B %d, %Y')
#                 else:
#                     start_date = selected_project['start_date'].strftime('%B %d, %Y')
                    
#                 if isinstance(selected_project['end_date'], str):
#                     end_date = datetime.strptime(selected_project['end_date'], '%Y-%m-%d').strftime('%B %d, %Y')
#                 else:
#                     end_date = selected_project['end_date'].strftime('%B %d, %Y')
                
#                 st.write(f"**Timeline:** {start_date} to {end_date}")
#             except Exception as e:
#                 st.write(f"**Timeline:** {selected_project['start_date']} to {selected_project['end_date']}")
            
#             st.write(f"**Budget:** ${selected_project['budget']:,}")
        
#         with col2:
#             st.write(f"**Priority:** {selected_project['priority']}")
#             st.write(f"**Status:** {selected_project['status']}")
#             st.write("**Required Skills:**")
#             for skill in selected_project["required_skills"]:
#                 st.write(f"• {skill}")
        
#         # Project Overview Summary
#         st.subheader("🔍 Project Overview")
#         required_skills_count = len(selected_project["required_skills"])
        
#         # Convert string dates to date objects for calculation
#         try:
#             if isinstance(selected_project['start_date'], str):
#                 start_date = datetime.strptime(selected_project['start_date'], '%Y-%m-%d').date()
#             else:
#                 start_date = selected_project['start_date']
                
#             if isinstance(selected_project['end_date'], str):
#                 end_date = datetime.strptime(selected_project['end_date'], '%Y-%m-%d').date()
#             else:
#                 end_date = selected_project['end_date']
            
#             timeline_months = (end_date - start_date).days // 30
#             timeline_text = f"approximately **{timeline_months} months**"
#         except Exception as e:
#             timeline_text = "the specified timeline"
        
#         st.write(f"This **{selected_project['priority']} priority** project requires **{required_skills_count} key skills** and will run for {timeline_text}.")
#         st.write(f"The project aims to: {selected_project['description']}")
        
#         if selected_project['budget'] > 500000:
#             st.info("💰 **High-budget project** - Consider comprehensive skill development and external hiring options.")
#         elif selected_project['budget'] > 200000:
#             st.info("💰 **Medium-budget project** - Balance between upskilling existing team and strategic hiring.")
#         else:
#             st.info("💰 **Budget-conscious project** - Focus on internal upskilling and team transfers where possible.")
        
#         # Analysis scope selection
#         st.subheader("🎯 Analysis Scope")
#         scope = st.radio(
#             "Choose analysis scope:",
#             ["Department Only", "Full Company"],
#             help="Department: Analyze skills within the project team's department only. Full Company: Consider all company skills."
#         )
        
#         scope_param = "department" if scope == "Department Only" else "company"
        
#         # AI Analysis button
#         if st.button("🚀 Generate AI Recommendations", type="primary", use_container_width=True):
#             with st.spinner("🤖 AI agents are analyzing your project..."):
#                 try:
#                     # Import the full workflow system
#                     from core.workflow import MultiAgentWorkflow
#                     from core import make_llm, make_reasoner
                    
#                     # Create LLMs with anthropic backend
#                     perception_llm = make_llm("anthropic")
#                     reasoner_llm = make_reasoner("anthropic")
                    
#                     # Prepare the analysis question focused on the selected project
#                     analysis_question = f"""Analyze ONLY the skill gaps for this specific project and provide structured recommendations.

# Project ID: {selected_project.get('id', 'unknown')}
# Project Name: {selected_project['name']}
# Required Skills: {', '.join(selected_project['required_skills'])}
# Timeline: {selected_project['start_date']} to {selected_project['end_date']}
# Budget: ${selected_project['budget']:,}
# Scope: {scope_param}

# IMPORTANT: Focus ONLY on this specific project. Do NOT analyze all projects or other projects. Return ONLY a JSON object with upskilling, transfer, and hiring recommendations for this specific project. Focus on actionable solutions with timelines and success probabilities."""
                    
#                     # Show the analysis question
#                     with st.expander("🔍 Analysis Question", expanded=False):
#                         st.write(analysis_question)
                    
#                     # Create and run the multi-agent workflow
#                     st.subheader("🤖 Multi-Agent Workflow Execution")
                    
#                     # Get the project ID and scope for the workflow
#                     project_id = selected_project.get('id', 'unknown')
                    
#                     # Show workflow parameters
#                     with st.expander("🔍 Workflow Parameters", expanded=False):
#                         st.write(f"**Project ID:** {project_id}")
#                         st.write(f"**Project Name:** {selected_project['name']}")
#                         st.write(f"**Analysis Scope:** {scope_param}")
#                         st.write(f"**Required Skills:** {', '.join(selected_project['required_skills'])}")
                    
#                     workflow = MultiAgentWorkflow(perception_llm, reasoner_llm)
#                     result = workflow.run(analysis_question, project_id=project_id, scope=scope_param)
                    
#                     # Display results from the full workflow
#                     if result:
#                         # Show intent and entities
#                         if result.get('intent'):
#                             st.info(f"**Analysis Intent:** {result['intent']}")
                        
#                         if result.get('entities'):
#                             st.info(f"**Identified Entities:** {', '.join(result['entities'])}")
                        
#                         # Show analysis results in structured format
#                         if result.get('analysis'):
#                             st.subheader("📋 Skills Gap Analysis")
                            
#                             try:
#                                 analysis_data = json.loads(result['analysis']) if isinstance(result['analysis'], str) else result['analysis']
                                
#                                 # Display skill gaps
#                                 if analysis_data.get('skill_gaps'):
#                                     st.write("**Missing Skills:**")
#                                     for skill in analysis_data['skill_gaps']:
#                                         st.write(f"• {skill}")
                                
#                                 # Display upskilling recommendations
#                                 if analysis_data.get('upskilling'):
#                                     st.write("**Upskilling Recommendations:**")
#                                     for rec in analysis_data['upskilling']:
#                                         st.write(f"• **{rec.get('employee', 'Unknown')}** → {rec.get('skill_to_learn', 'Unknown')}")
#                                         st.write(f"  Timeline: {rec.get('timeline_weeks', 'Unknown')} weeks | Confidence: {rec.get('confidence', 'Unknown')}")
#                                         st.write(f"  Reason: {rec.get('reason', 'N/A')}")
#                                         st.write("")
                                
#                                 # Display internal transfer recommendations
#                                 if analysis_data.get('internal_transfers'):
#                                     st.write("**Internal Transfer Recommendations:**")
#                                     for rec in analysis_data['internal_transfers']:
#                                         st.write(f"• **{rec.get('employee', 'Unknown')}** from {rec.get('current_team', 'Unknown')}")
#                                         st.write(f"  Skills: {', '.join(rec.get('skills_brought', []))}")
#                                         st.write(f"  Availability: {rec.get('availability', 'Unknown')}")
#                                         st.write(f"  Reason: {rec.get('reason', 'N/A')}")
#                                         st.write("")
                                
#                                 # Display hiring recommendations
#                                 if analysis_data.get('hiring'):
#                                     st.write("**Hiring Recommendations:**")
#                                     for rec in analysis_data['hiring']:
#                                         st.write(f"• **{rec.get('role', 'Unknown')}**")
#                                         st.write(f"  Skills: {', '.join(rec.get('required_skills', []))}")
#                                         st.write(f"  Urgency: {rec.get('urgency', 'Unknown')}")
#                                         st.write(f"  Cost: {rec.get('estimated_cost', 'N/A')}")
#                                         st.write("")
                                
#                                 # Display other analysis data
#                                 if analysis_data.get('timeline_assessment'):
#                                     st.write(f"**Timeline Assessment:** {analysis_data['timeline_assessment']}")
                                
#                                 if analysis_data.get('risk_factors'):
#                                     st.write("**Risk Factors:**")
#                                     for risk in analysis_data['risk_factors']:
#                                         st.write(f"• {risk}")
                                
#                                 if analysis_data.get('success_probability'):
#                                     st.write(f"**Success Probability:** {analysis_data['success_probability']}")
                                    
#                             except (json.JSONDecodeError, TypeError):
#                                 # Fallback to raw display if JSON parsing fails
#                                 analysis_content = safe_content_display(result['analysis'])
#                                 st.write(analysis_content)
                        
#                         # Show final recommendations from decision agent
#                         if result.get('decision'):
#                             st.subheader("🎯 Final Recommendations (Decision Agent)")
                            
#                             try:
#                                 decision_data = json.loads(result['decision']) if isinstance(result['decision'], str) else result['decision']
                                
#                                 # Display decision summary
#                                 if decision_data.get('decision_summary'):
#                                     st.success(f"**Decision:** {decision_data['decision_summary']}")
                                
#                                 # Display primary strategy
#                                 if decision_data.get('primary_strategy'):
#                                     st.info(f"**Primary Strategy:** {decision_data['primary_strategy'].title()}")
                                
#                                 # Display action plan
#                                 if decision_data.get('action_plan'):
#                                     action_plan = decision_data['action_plan']
#                                     st.write("**Action Plan:**")
#                                     if action_plan.get('immediate_actions'):
#                                         st.write("**Immediate Actions:**")
#                                         for action in action_plan['immediate_actions']:
#                                             st.write(f"• {action}")
                                    
#                                     if action_plan.get('timeline_weeks'):
#                                         st.write(f"**Timeline:** {action_plan['timeline_weeks']} weeks")
                                    
#                                     if action_plan.get('key_milestones'):
#                                         st.write("**Key Milestones:**")
#                                         for milestone in action_plan['key_milestones']:
#                                             st.write(f"• {milestone}")
                                
#                                 # Display team assignment
#                                 if decision_data.get('team_assignment'):
#                                     team = decision_data['team_assignment']
#                                     st.write("**Team Assignment:**")
#                                     if team.get('primary_owner'):
#                                         st.write(f"**Primary Owner:** {team['primary_owner']}")
                                    
#                                     if team.get('support_team'):
#                                         st.write("**Support Team:**")
#                                         for member in team['support_team']:
#                                             st.write(f"• {member}")
                                    
#                                     if team.get('responsibilities'):
#                                         st.write("**Responsibilities:**")
#                                         for person, responsibility in team['responsibilities'].items():
#                                             st.write(f"• **{person}:** {responsibility}")
                                
#                                 # Display risk management
#                                 if decision_data.get('risk_management'):
#                                     risk_mgmt = decision_data['risk_management']
#                                     st.write("**Risk Management:**")
#                                     if risk_mgmt.get('primary_risks'):
#                                         st.write("**Primary Risks:**")
#                                         for risk in risk_mgmt['primary_risks']:
#                                             st.write(f"• {risk}")
                                    
#                                     if risk_mgmt.get('mitigation_strategies'):
#                                         st.write("**Mitigation Strategies:**")
#                                         for strategy in risk_mgmt['mitigation_strategies']:
#                                             st.write(f"• {strategy}")
                                
#                                 # Display success criteria
#                                 if decision_data.get('success_criteria'):
#                                     success = decision_data['success_criteria']
#                                     st.write("**Success Criteria:**")
#                                     if success.get('quantitative'):
#                                         st.write("**Quantitative:**")
#                                         for metric in success['quantitative']:
#                                             st.write(f"• {metric}")
                                    
#                                     if success.get('qualitative'):
#                                         st.write("**Qualitative:**")
#                                         for outcome in success['qualitative']:
#                                             st.write(f"• {outcome}")
                                
#                                 # Display next review date
#                                 if decision_data.get('next_review_date'):
#                                     st.write(f"**Next Review Date:** {decision_data['next_review_date']}")
                                    
#                             except (json.JSONDecodeError, TypeError):
#                                 # Fallback to raw display if JSON parsing fails
#                                 decision_content = safe_content_display(result['decision'])
#                                 st.write(decision_content)
                        
#                         # Show workflow summary
#                         with st.expander("📊 Workflow Summary", expanded=False):
#                             st.json(result)
                        
#                         st.success("✅ Multi-agent workflow completed successfully!")
                            
#                         # Next steps
#                         st.subheader("🔄 Next Steps")
#                         st.write("1. **Review Recommendations**: Carefully consider each recommendation based on your team's capacity and timeline")
#                         st.write("2. **Prioritize Actions**: Start with high-confidence, high-impact recommendations")
#                         st.write("3. **Plan Implementation**: Create detailed action plans with timelines and responsibilities")
#                         st.write("4. **Monitor Progress**: Track skill development and adjust plans as needed")
#                         st.write("5. **Regular Reviews**: Schedule periodic assessments to ensure project readiness")
                    
#                     else:
#                         st.error("❌ No results generated from multi-agent workflow")
                        
#                 except Exception as e:
#                     st.error(f"❌ Error running multi-agent workflow: {e}")
#                     st.info("Make sure you have the ANTHROPIC_API_KEY set in your environment")
                    
#                     # Show environment check
#                     with st.expander("🔧 Environment Check", expanded=False):
#                         st.write("**ANTHROPIC_API_KEY:**", "✅ Set" if os.getenv("ANTHROPIC_API_KEY") else "❌ Not Set")
#                         if os.getenv("ANTHROPIC_API_KEY"):
#                             st.write("**Key length:**", len(os.getenv("ANTHROPIC_API_KEY")))
#                         st.write("**Current working directory:**", os.getcwd())
                        
#                         # Manual API key input as fallback
#                         if not os.getenv("ANTHROPIC_API_KEY"):
#                             st.warning("ANTHROPIC_API_KEY not found. You can manually enter it below:")
#                             manual_key = st.text_input("Enter Anthropic API Key:", type="password")
#                             if manual_key:
#                                 os.environ["ANTHROPIC_API_KEY"] = manual_key
#                                 st.success("API key set manually")
#                                 st.rerun()

# def display_recommendations_summary(analysis_data: Dict[str, Any]):
#     """Display a summary of AI recommendations."""
#     st.success(" AI Recommendations Generated!")
    
#     project = analysis_data["project"]
#     recommendations = analysis_data["recommendations"]
#     analysis_summary = analysis_data["analysis_summary"]
    
#     # Project summary
#     st.subheader(f" Project: {project['name']}")
#     st.write(f"**Description:** {project['description']}")
#     st.write(f"**Timeline:** {project['start_date']} to {project['end_date']}")
#     st.write(f"**Budget:** ${project['budget']:,}")
    
#     # Quick stats
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("Total Recommendations", analysis_summary["total_recommendations"])
#     with col2:
#         st.metric("Upskilling", analysis_summary["upskill_count"])
#     with col3:
#         st.metric("Transfers", analysis_summary["transfer_count"])
#     with col4:
#         st.metric("Hiring", analysis_summary["hire_count"])
    
#     # Priority-based recommendations
#     st.subheader(" Priority Recommendations")
    
#     if recommendations:
#         # Group by priority
#         high_priority = [r for r in recommendations if r["priority"] == "high"]
#         medium_priority = [r for r in recommendations if r["priority"] == "medium"]
#         low_priority = [r for r in recommendations if r["priority"] == "low"]
        
#         if high_priority:
#             st.subheader(" High Priority")
#             for rec in high_priority:
#                 display_recommendation_card(rec, "high")
        
#         if medium_priority:
#             st.subheader(" Medium Priority")
#             for rec in medium_priority:
#                 display_recommendation_card(rec, "medium")
        
#         if low_priority:
#             st.subheader(" Low Priority")
#             for rec in low_priority:
#                 display_recommendation_card(rec, "low")
        
#         if not any([high_priority, medium_priority, low_priority]):
#             st.info("No priority-based recommendations available.")
#     else:
#         st.info("No recommendations available for this project. \n Skills needed are already available.")
#         return
    
#     # Action plan
#     st.subheader(" Action Plan")
    
#     if recommendations:
#         if analysis_summary["upskill_count"] > 0:
#             st.info(" **Immediate Actions for Upskilling:**")
#             upskill_recs = [r for r in recommendations if r["type"] == "upskill"]
#             for rec in upskill_recs:
#                 st.write(f"• Start training {rec['employee']} in {', '.join(rec.get('skills_to_learn', []))}")
        
#         if analysis_summary["transfer_count"] > 0:
#             st.info(" **Actions for Transfers:**")
#             transfer_recs = [r for r in recommendations if r["type"] == "transfer"]
#             for rec in transfer_recs:
#                 st.write(f"• Coordinate with HR to transfer {rec['employee']} to the project team")
        
#         if analysis_summary["hire_count"] > 0:
#             st.info(" **Actions for Hiring:**")
#             hire_recs = [r for r in recommendations if r["type"] == "hire"]
#             for rec in hire_recs:
#                 st.write(f"• Begin recruitment process for specialized skills")
        
#         st.success(" Use these recommendations to optimize your team composition and project success!")
#     else:
#         st.info("No action items available for this project.")
    
#     # Success metrics
#     st.subheader(" Success Metrics")
    
#     if recommendations:
#         total_success_prob = sum(r["success_probability"] for r in recommendations)
#         avg_success_prob = total_success_prob / len(recommendations)
        
#         col1, col2 = st.columns(2)
#         with col1:
#             st.metric("Average Success Probability", f"{avg_success_prob*100:.1f}%")
            
#             # Calculate estimated costs
#             total_cost = sum(r.get("estimated_cost", 0) for r in recommendations if r["type"] == "hire")
#             if total_cost > 0:
#                 st.metric("Total Hiring Costs", f"${total_cost:,}")
#             else:
#                 st.metric("Total Hiring Costs", "$0")
        
#         with col2:
#             # Calculate timeline
#             training_times = [r.get("estimated_training_time", 0) for r in recommendations if r["type"] in ["upskill", "transfer"]]
#             if training_times:
#                 max_timeline = max(training_times)
#                 st.metric("Longest Training Time", f"{max_timeline} weeks")
#             else:
#                 st.metric("Longest Training Time", "N/A")
            
#             # Risk assessment
#             high_risk_count = len([r for r in recommendations if r["risk"] == "high"])
#             if high_risk_count > 0:
#                 st.warning(f" {high_risk_count} high-risk recommendations")
#     else:
#         st.info("No success metrics available for this project.")

# def display_recommendation_card(rec: Dict[str, Any], priority: str):
#     """Display a single recommendation as a card."""
#     # Validate required fields
#     if not rec or "type" not in rec:
#         st.error("Invalid recommendation data")
#         return
    
#     # Color coding based on priority
#     if priority == "high":
#         border_color = " "
#         bg_color = "#ffebee"
#     elif priority == "medium":
#         border_color = " "
#         bg_color = "#fff3e0"
#     else:
#         border_color = " "
#         bg_color = "#e8f5e8"
    
#     # Create a styled card
#     with st.container():
#         st.markdown(f"""
#         <div style="
#             border: 2px solid {bg_color};
#             border-radius: 10px;
#             padding: 15px;
#             margin: 10px 0;
#             background-color: {bg_color}20;
#         ">
#             <h4>{border_color} {rec.get('type', 'Unknown').title()} Recommendation</h4>
#             <p><strong>Reason:</strong> {rec.get('reason', 'N/A')}</p>
#             <p><strong>Details:</strong> {rec.get('details', 'N/A')}</p>
#             <p><strong>Risk:</strong> {rec.get('risk', 'Unknown').title()} | <strong>Success:</strong> {rec.get('success_probability', 0)*100:.0f}%</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         # Show additional details in expandable section
#         with st.expander(" Detailed Information"):
#             if rec["type"] == "upskill":
#                 st.write(f"**Employee:** {rec.get('employee', 'N/A')}")
#                 current_skills = rec.get('current_skills', [])
#                 if current_skills:
#                     st.write(f"**Current Skills:** {', '.join(current_skills)}")
#                 else:
#                     st.write("**Current Skills:** N/A")
                
#                 skills_to_learn = rec.get('skills_to_learn', [])
#                 if skills_to_learn:
#                     st.write(f"**Skills to Learn:** {', '.join(skills_to_learn)}")
#                 else:
#                     st.write("**Skills to Learn:** N/A")
                
#                 st.write(f"**Training Time:** {rec.get('estimated_training_time', 'N/A')}")
            
#             elif rec["type"] == "transfer":
#                 st.write(f"**Employee:** {rec.get('employee', 'N/A')}")
#                 current_skills = rec.get('current_skills', [])
#                 if current_skills:
#                     st.write(f"**Current Skills:** {', '.join(current_skills)}")
#                 else:
#                     st.write("**Current Skills:** N/A")
                
#                 skills_to_learn = rec.get('skills_to_learn', [])
#                 if skills_to_learn:
#                     st.write(f"**Skills to Learn:** {', '.join(skills_to_learn)}")
#                 else:
#                     st.write("**Skills to Learn:** N/A")
                
#                 st.write(f"**Training Time:** {rec.get('estimated_training_time', 'N/A')}")
            
#             elif rec["type"] == "hire":
#                 st.write(f"**Estimated Cost:** ${rec.get('estimated_cost', 0):,}")
#                 st.write(f"**Timeline:** {rec.get('timeline', 'N/A')}")
#                 skills_to_learn = rec.get('skills_to_learn', [])
#                 if skills_to_learn:
#                     st.write(f"**Skills Required:** {', '.join(skills_to_learn)}")
#                 else:
#                     st.write("**Skills Required:** N/A")
            
#             else:
#                 st.write("**Unknown recommendation type**")

# def show_department_overview():
#     """Show comprehensive department overview."""
#     st.header(" Department Overview")
    
#     # Get department data
#     dept_overview = get_api_data("/api/analysis/department-overview")
#     departments_data = get_api_data("/api/departments")
    
#     if "error" in dept_overview or "error" in departments_data:
#         st.error("Failed to load department data")
#         return
    
#     # Department summary cards
#     st.subheader(" Department Summary")
    
#     # Create department cards in a grid
#     dept_data = dept_overview.get("departments", {})
#     dept_names = list(dept_data.keys())
    
#     # Calculate grid layout
#     cols_per_row = 3
#     for i in range(0, len(dept_names), cols_per_row):
#         row_depts = dept_names[i:i + cols_per_row]
#         cols = st.columns(len(row_depts))
        
#         for j, dept_name in enumerate(row_depts):
#             with cols[j]:
#                 dept_info = dept_data[dept_name]
#                 st.metric(
#                     label=dept_name,
#                     value=dept_info["count"],
#                     delta=f"${dept_info['avg_salary']}k avg"
#                 )
                
#                 # Experience level breakdown
#                 exp_levels = dept_info["experience_levels"]
#                 st.write(f"**Experience:** {exp_levels['junior']}J, {exp_levels['mid']}M, {exp_levels['senior']}S")
    
#     # Detailed department analysis
#     st.subheader(" Detailed Analysis")
    
#     selected_dept = st.selectbox(
#         "Select Department for Detailed View:",
#         dept_names
#     )
    
#     if selected_dept:
#         dept_info = dept_data[selected_dept]
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.write(f"**Total Employees:** {dept_info['count']}")
#             st.write(f"**Average Salary:** ${dept_info['avg_salary']}k")
#             st.write(f"**Total Skills:** {len(dept_info['skills'])}")
            
#             # Experience level chart
#             exp_levels = dept_info["experience_levels"]
#             st.write("**Experience Distribution:**")
#             for level, count in exp_levels.items():
#                 if count > 0:
#                     st.progress(count / dept_info['count'])
#                     st.write(f"{level.title()}: {count}")
        
#         with col2:
#             st.write("**Roles in Department:**")
#             for role in dept_info["roles"]:
#                 st.write(f"• {role}")
            
#             st.write("**Key Skills:**")
#             # Show top skills (limit to 10)
#             skills_to_show = dept_info["skills"][:10]
#             for skill in skills_to_show:
#                 st.write(f"• {skill}")
            
#             if len(dept_info["skills"]) > 10:
#                 st.write(f"... and {len(dept_info['skills']) - 10} more skills")
    
#     # Skills heatmap across departments
#     st.subheader(" Skills Heatmap Across Departments")
    
#     # Create skills matrix
#     all_skills = set()
#     for dept_info in dept_data.values():
#         all_skills.update(dept_info["skills"])
    
#     skills_matrix = {}
#     for skill in sorted(all_skills):
#         skills_matrix[skill] = {}
#         for dept_name in dept_names:
#             skills_matrix[skill][dept_name] = skill in dept_data[dept_name]["skills"]
    
#     # Convert to DataFrame for display
#     skills_df = pd.DataFrame(skills_matrix).T
    
#     # Create a styled heatmap
#     def color_skills(val):
#         return 'background-color: #90EE90' if val else 'background-color: #FFB6C1'
    
#     st.dataframe(skills_df.style.applymap(color_skills), use_container_width=True)
    
#     # Department comparison
#     st.subheader(" Department Comparison")
    
#     # Salary comparison
#     salary_data = []
#     for dept_name in dept_names:
#         dept_info = dept_data[dept_name]
#         salary_data.append({
#             "Department": dept_name,
#             "Employee Count": dept_info["count"],
#             "Avg Salary ($k)": dept_info["avg_salary"],
#             "Total Skills": len(dept_info["skills"])
#         })
    
#     comparison_df = pd.DataFrame(salary_data)
#     st.dataframe(comparison_df, use_container_width=True)

# def display_skills_gap_analysis(analysis_data: Dict[str, Any]):
#     """Display skills gap analysis results."""
#     st.success("Skills gap analysis completed!")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.metric("Required Skills", len(analysis_data["required_skills"]))
#         st.metric("Available Skills", len(analysis_data["available_skills"]))
    
#     with col2:
#         st.metric("Skill Gaps", analysis_data["gap_count"])
#         st.metric("Coverage", f"{analysis_data['coverage_percentage']}%")
    
#     # Skills breakdown
#     st.subheader("Skills Breakdown")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.write("**Required Skills:**")
#         for skill in analysis_data["required_skills"]:
#             st.write(f"• {skill}")
    
#     with col2:
#         st.write("**Available Skills:**")
#         for skill in analysis_data["available_skills"]:
#             st.write(f"• {skill}")
    
#     # Skill gaps
#     if analysis_data["skill_gaps"]:
#         st.subheader(" Identified Skill Gaps")
#         for skill in analysis_data["skill_gaps"]:
#             st.error(f"Missing: {skill}")
#     else:
#         st.success(" No skill gaps identified!")

# def display_ai_reasoning_analysis(analysis_data: Dict[str, Any]):
#     """Display AI reasoning analysis with agent workflow."""
#     # Validate required data
#     if not analysis_data:
#         st.error("No analysis data available")
#         return
    
#     project = analysis_data.get("project")
#     team_analysis = analysis_data.get("team_analysis")
#     reasoning_steps = analysis_data.get("reasoning_steps", [])
#     recommendations = analysis_data.get("recommendations", [])
#     analysis_summary = analysis_data.get("analysis_summary", {})
    
#     if not project or not team_analysis:
#         st.error("Invalid analysis data structure")
#         return
    
#     st.success(" AI Analysis Complete!")
    
#     st.subheader(f" Analysis Results for: {project.get('name', 'Unknown Project')}")
    
#     # Team analysis metrics
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("Team Size", team_analysis.get("team_size", 0))
#     with col2:
#         st.metric("Departments", len(team_analysis.get("departments", [])))
#     with col3:
#         st.metric("Skill Coverage", f"{team_analysis.get('coverage_percentage', 0)}%")
#     with col4:
#         st.metric("Skill Gaps", len(team_analysis.get("skill_gaps", [])))
    
#     # AI Agent Workflow
#     st.subheader(" AI Agent Workflow")
    
#     if reasoning_steps:
#         for step in reasoning_steps:
#             step_num = step.get("step", "?")
#             agent = step.get("agent", "Unknown Agent")
#             action = step.get("action", "Unknown Action")
#             details = step.get("details", "No details available")
            
#             with st.expander(f"Step {step_num}: {agent} - {action}"):
#                 st.write(f"**Action:** {action}")
#                 st.write(f"**Details:** {details}")
                
#                 # Add some visual flair based on agent type
#                 if "Perception" in agent:
#                     st.info(" Perception Agent analyzing requirements...")
#                 elif "Research" in agent:
#                     st.info(" Research Agent gathering data...")
#                 elif "Analysis" in agent:
#                     st.info(" Analysis Agent processing information...")
#                 elif "Decision" in agent:
#                     st.info(" Decision Agent making recommendations...")
#     else:
#         st.info("No reasoning steps available")
    
#     # Recommendations
#     st.subheader(" Strategic Recommendations")
    
#     if recommendations:
#         # Summary metrics
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Upskilling", analysis_summary.get("upskill_count", 0))
#         with col2:
#             st.metric("Transfers", analysis_summary.get("transfer_count", 0))
#         with col3:
#             st.metric("Hiring", analysis_summary.get("hire_count", 0))
        
#         # Display each recommendation
#         for i, rec in enumerate(recommendations, 1):
#             if not rec or "type" not in rec:
#                 continue
                
#             # Color code by type
#             if rec["type"] == "upskill":
#                 st.success(f" **Recommendation {i}: Upskill {rec.get('employee', 'Unknown Employee')}**")
#             elif rec["type"] == "transfer":
#                 st.warning(f" **Recommendation {i}: Transfer {rec.get('employee', 'Unknown Employee')}**")
#             elif rec["type"] == "hire":
#                 st.error(f" **Recommendation {i}: Hire New Employee**")
            
#             with st.expander(f"Details for Recommendation {i}"):
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write(f"**Priority:** {rec.get('priority', 'Unknown').title()}")
#                     st.write(f"**Reason:** {rec.get('reason', 'N/A')}")
#                     st.write(f"**Details:** {rec.get('details', 'N/A')}")
#                     st.write(f"**Risk:** {rec.get('risk', 'Unknown').title()}")
#                     st.write(f"**Success Probability:** {rec.get('success_probability', 0)*100:.0f}%")
                
#                 with col2:
#                     if rec["type"] == "upskill":
#                         current_skills = rec.get('current_skills', [])
#                         if current_skills:
#                             st.write("**Current Skills:**")
#                             for skill in current_skills:
#                                 st.write(f"• {skill}")
#                         else:
#                             st.write("**Current Skills:** N/A")
                        
#                         skills_to_learn = rec.get('skills_to_learn', [])
#                         if skills_to_learn:
#                             st.write("**Skills to Learn:**")
#                             for skill in skills_to_learn:
#                                 st.write(f"• {skill}")
#                         else:
#                             st.write("**Skills to Learn:** N/A")
                        
#                         st.write(f"**Training Time:** {rec.get('estimated_training_time', 'N/A')}")
                    
#                     elif rec["type"] == "transfer":
#                         st.write("**Employee:** " + rec.get("employee", "N/A"))
#                         current_skills = rec.get('current_skills', [])
#                         if current_skills:
#                             st.write("**Current Skills:**")
#                             for skill in current_skills:
#                                 st.write(f"• {skill}")
#                         else:
#                             st.write("**Current Skills:** N/A")
                        
#                         skills_to_learn = rec.get('skills_to_learn', [])
#                         if skills_to_learn:
#                             st.write("**Skills to Learn:**")
#                             for skill in skills_to_learn:
#                                 st.write(f"• {skill}")
#                         else:
#                             st.write("**Skills to Learn:** N/A")
                        
#                         st.write(f"**Training Time:** {rec.get('estimated_training_time', 'N/A')}")
                    
#                     elif rec["type"] == "hire":
#                         st.write(f"**Estimated Cost:** ${rec.get('estimated_cost', 0):,}")
#                         st.write(f"**Timeline:** {rec.get('timeline', 'N/A')}")
#     else:
#         st.info("No recommendations available")
    
#     # Team skills vs required skills
#     st.subheader(" Skills Analysis")
    
#     required_skills = team_analysis.get("required_skills", [])
#     team_skills = team_analysis.get("team_skills", [])
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.write("**Required Skills:**")
#         if required_skills:
#             for skill in required_skills:
#                 if skill in team_skills:
#                     st.success(f" {skill}")
#                 else:
#                     st.error(f" {skill}")
#         else:
#             st.write("No required skills specified")
    
#     with col2:
#         st.write("**Team Skills:**")
#         if team_skills:
#             for skill in team_skills:
#                 if skill in required_skills:
#                     st.success(f" {skill}")
#                 else:
#                     st.info(f" {skill} (extra)")
#         else:
#             st.write("No team skills available")
    
#     # Department breakdown
#     departments = team_analysis.get("departments", [])
#     if departments:
#         st.subheader(" Team Department Breakdown")
#         dept_cols = st.columns(len(departments))
        
#         for i, dept in enumerate(departments):
#             with dept_cols[i]:
#                 st.metric(dept, "Team Member")
    
#     # Action items
#     st.subheader(" Next Steps")
    
#     if recommendations:
#         upskill_count = analysis_summary.get("upskill_count", 0)
#         transfer_count = analysis_summary.get("transfer_count", 0)
#         hire_count = analysis_summary.get("hire_count", 0)
        
#         if upskill_count > 0:
#             st.info(" **Upskilling Actions:** Start training programs for identified employees")
        
#         if transfer_count > 0:
#             st.info(" **Transfer Actions:** Coordinate with HR for employee transfers")
        
#         if hire_count > 0:
#             st.info(" **Hiring Actions:** Begin recruitment process for specialized skills")
        
#         st.success(" AI analysis complete! Use these recommendations to optimize your team composition.")
#     else:
#         st.info("No action items available")

# if __name__ == "__main__":
#     main()
