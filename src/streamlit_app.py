import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_projects() -> List[Dict[str, Any]]:
    """Fetch available projects from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/projects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Raw API response: {data}")  # Debug line
            
            projects = data.get("projects", [])
            print(f"DEBUG: Projects from API: {projects}")  # Debug line
            
            # Ensure each project has the required structure
            formatted_projects = []
            for project in projects:
                if isinstance(project, dict):
                    # If it's already a dict, ensure it has name and id
                    if "name" not in project and "id" not in project:
                        # If it's just a string, convert to proper format
                        project_name = str(project)
                        formatted_projects.append({
                            "id": project_name,
                            "name": project_name
                        })
                    else:
                        formatted_projects.append(project)
                else:
                    # If it's a string, convert to proper format
                    project_name = str(project)
                    formatted_projects.append({
                        "id": project_name,
                        "name": project_name
                    })
            
            #print(f"DEBUG: Formatted projects: {formatted_projects}")  # Debug line
            return formatted_projects
        else:
            st.error(f"Failed to fetch projects: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_recommendation(project_id: str) -> Dict[str, Any]:
    """Fetch recommendation for a specific project"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/recommendations",
            json={"project_id": project_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            st.error("Validation error: Invalid project ID format")
            return {}
        else:
            st.error(f"Failed to get recommendation: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting recommendation: {str(e)}")
        return {}

def display_recommendation(recommendation_data):
    """Display the recommendation in a nice Streamlit card format."""
    
    if not recommendation_data:
        st.warning("No recommendation data available")
        return
    
    # Extract recommendation safely
    outer_rec = recommendation_data.get("recommendation", {})
    recommendation = outer_rec.get("recommendation", {})  # Nested key
    
    if not recommendation:
        st.warning("Recommendation details are missing")
        return
    
    st.markdown("### 📋 Recommendation Details")
    
    # Two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        rec_type = recommendation.get("type", "N/A")
        type_icons = {
            "UPSKILL": "🎯",
            "TRANSFER": "🔄",
            "HIRE": "👥"
        }
        icon = type_icons.get(rec_type, "📝")
        st.markdown(f"{icon} **Type:** {rec_type}")
        
        timeline = recommendation.get("timeline", "N/A")
        st.metric(f"⏱️ Timeline for {rec_type}", timeline)
    
    with col2:
        risk_level = recommendation.get("risk_level", "N/A").lower()
        risk_colors = {
            "low": ("🟢", st.success),
            "medium": ("🟡", st.warning),
            "high": ("🔴", st.error)
        }
        icon, st_func = risk_colors.get(risk_level, ("⚪", st.info))
        st_func(f"{icon} **Risk Level:** {risk_level.capitalize()}")
    
    st.markdown("---")
    
    details = recommendation.get("details", "No details provided")
    reasoning = recommendation.get("reasoning", "No reasoning provided")
    
    st.markdown(f"**📝 Details:** {details}")
    st.markdown(f"**💭 Reasoning:** {reasoning}")



def main():
    st.set_page_config(
        page_title="GapLens - Project Gap Analysis",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🔍 GapLens - Project Gap Analysis")
    st.markdown("Analyze skill gaps and get recommendations for your projects")
    
    # Check API health
    if not check_api_health():
        st.error("❌ API server is not running. Please start the server first.")
        st.info("To start the server, run: `python src/api_server.py`")
        return
    
    st.success("✅ Connected to API server")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Fetch projects
    st.sidebar.markdown("### 📁 Available Projects")
    
    if st.sidebar.button("🔄 Refresh Projects"):
        st.rerun()
    
    projects = get_projects()
    #print(f"DEBUG: Projects returned from get_projects: {projects}")  # Debug line
    
    # Add debug info in the sidebar
    # st.sidebar.markdown(f"**Debug Info:** {len(projects)} projects found")
    # if projects:
    #     st.sidebar.markdown("**Project IDs:** " + ", ".join([p.get("id", str(p)) for p in projects]))
    
    if not projects:
        st.sidebar.warning("No projects found")
        return
    
    # Project selection - show names but track full objects
    selected_project = st.sidebar.selectbox(
        "Select a project:",
        projects,
        index=0 if projects else None,
        format_func=lambda project: project.get("name", str(project))
    )
    
    # Extract project_id for API calls
    project_id = selected_project.get("id") if isinstance(selected_project, dict) else str(selected_project)
    project_name = selected_project.get("name") if isinstance(selected_project, dict) else str(selected_project)
    
    st.sidebar.markdown(f"**Selected:** {project_name}")
    
    # Main content area
    st.markdown("---")
    
    if selected_project:
        st.header(f"📊 Analysis for {project_name}")
        
        # Get recommendation button
        if st.button("🚀 Get Recommendation", type="primary"):
            with st.spinner("Analyzing project gaps..."):
                recommendation_data = get_recommendation(project_id)  # Use project_id, not full object
                print(f"DEBUG: Recommendation data: {recommendation_data}")  # Debug line
                if recommendation_data:
                    st.success("✅ Analysis completed!")
                    display_recommendation(recommendation_data)
                else:
                    st.error("❌ Failed to get recommendation")
        
        # Show project info
        st.markdown("### 📋 Project Information")
        st.info(f"Project ID: **{project_id}**")
        st.info(f"Project Name: **{project_name}**")
        st.info("Click the button above to analyze this project and get recommendations.")
        
        # Add some helpful information
        st.markdown("---")
        st.markdown("### 💡 How it works")
        st.markdown("""
        1. **Project Selection**: Choose a project from the dropdown in the sidebar
        2. **Analysis**: Click 'Get Recommendation' to analyze skill gaps
        3. **Results**: View detailed recommendations including:
           - Recommendation type (Upskill/Transfer/Hire)
           - Timeline estimates
           - Risk assessment
           - Detailed reasoning
        """)
        
        # Add refresh option
        if st.button("🔄 Refresh Analysis"):
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by GapLens - Intelligent Project Gap Analysis*")

if __name__ == "__main__":
    main() 
