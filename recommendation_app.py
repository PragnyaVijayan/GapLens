"""
Focused Recommendation App for GapLens Skills Analysis System
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import os
from pathlib import Path
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("python-dotenv not installed. Install with: pip install python-dotenv")

# Page configuration
st.set_page_config(
    page_title="GapLens Recommendations",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

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

def safe_content_display(content, max_length=1000):
    """Safely display content with proper type handling and length limiting."""
    try:
        if isinstance(content, str):
            return content[:max_length] + "..." if len(content) > max_length else content
        else:
            content_str = str(content)
            return content_str[:max_length] + "..." if len(content_str) > max_length else content_str
    except Exception:
        return str(content)[:max_length] + "..." if len(str(content)) > max_length else str(content)

def main():
    """Main Streamlit application."""
    st.title("🎯 GapLens AI Recommendations")
    st.markdown("AI-powered skills gap analysis and team optimization recommendations")
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ FastAPI backend is not running. Please start the backend server first.")
        st.info("Run: `cd infrastructure && python api.py`")
        return
    
    # Project selection
    st.header("📋 Select Project for Analysis")
    
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
        format_func=lambda x: f"{x['name']} - {x['status']} (${x['budget']:,})"
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
            
            st.write(f"**Budget:** ${selected_project['budget']:,}")
        
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
        
        if selected_project['budget'] > 500000:
            st.info("💰 **High-budget project** - Consider comprehensive skill development and external hiring options.")
        elif selected_project['budget'] > 200000:
            st.info("💰 **Medium-budget project** - Balance between upskilling existing team and strategic hiring.")
        else:
            st.info("💰 **Budget-conscious project** - Focus on internal upskilling and team transfers where possible.")
        
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
                        
                        # Show analysis results in structured format
                        if result.get('analysis'):
                            st.subheader("📋 Skills Gap Analysis")
                            
                            try:
                                analysis_data = json.loads(result['analysis']) if isinstance(result['analysis'], str) else result['analysis']
                                
                                # Display skill gaps
                                if analysis_data.get('skill_gaps'):
                                    st.write("**Missing Skills:**")
                                    for skill in analysis_data['skill_gaps']:
                                        st.write(f"• {skill}")
                                
                                # Display upskilling recommendations
                                if analysis_data.get('upskilling'):
                                    st.write("**Upskilling Recommendations:**")
                                    for rec in analysis_data['upskilling']:
                                        st.write(f"• **{rec.get('employee', 'Unknown')}** → {rec.get('skill_to_learn', 'Unknown')}")
                                        st.write(f"  Timeline: {rec.get('timeline_weeks', 'Unknown')} weeks | Confidence: {rec.get('confidence', 'Unknown')}")
                                        st.write(f"  Reason: {rec.get('reason', 'N/A')}")
                                        st.write("")
                                
                                # Display internal transfer recommendations
                                if analysis_data.get('internal_transfers'):
                                    st.write("**Internal Transfer Recommendations:**")
                                    for rec in analysis_data['internal_transfers']:
                                        st.write(f"• **{rec.get('employee', 'Unknown')}** from {rec.get('current_team', 'Unknown')}")
                                        st.write(f"  Skills: {', '.join(rec.get('skills_brought', []))}")
                                        st.write(f"  Availability: {rec.get('availability', 'Unknown')}")
                                        st.write(f"  Reason: {rec.get('reason', 'N/A')}")
                                        st.write("")
                                
                                # Display hiring recommendations
                                if analysis_data.get('hiring'):
                                    st.write("**Hiring Recommendations:**")
                                    for rec in analysis_data['hiring']:
                                        st.write(f"• **{rec.get('role', 'Unknown')}**")
                                        st.write(f"  Skills: {', '.join(rec.get('required_skills', []))}")
                                        st.write(f"  Urgency: {rec.get('urgency', 'Unknown')}")
                                        st.write(f"  Cost: {rec.get('estimated_cost', 'N/A')}")
                                        st.write("")
                                
                                # Display other analysis data
                                if analysis_data.get('timeline_assessment'):
                                    st.write(f"**Timeline Assessment:** {analysis_data['timeline_assessment']}")
                                
                                if analysis_data.get('risk_factors'):
                                    st.write("**Risk Factors:**")
                                    for risk in analysis_data['risk_factors']:
                                        st.write(f"• {risk}")
                                
                                if analysis_data.get('success_probability'):
                                    st.write(f"**Success Probability:** {analysis_data['success_probability']}")
                                    
                            except (json.JSONDecodeError, TypeError):
                                # Fallback to raw display if JSON parsing fails
                                analysis_content = safe_content_display(result['analysis'])
                                st.write(analysis_content)
                        
                        # Show final recommendations from decision agent
                        if result.get('decision'):
                            st.subheader("🎯 Final Recommendations (Decision Agent)")
                            
                            try:
                                decision_data = json.loads(result['decision']) if isinstance(result['decision'], str) else result['decision']
                                
                                # Display decision summary
                                if decision_data.get('decision_summary'):
                                    st.success(f"**Decision:** {decision_data['decision_summary']}")
                                
                                # Display primary strategy
                                if decision_data.get('primary_strategy'):
                                    st.info(f"**Primary Strategy:** {decision_data['primary_strategy'].title()}")
                                
                                # Display action plan
                                if decision_data.get('action_plan'):
                                    action_plan = decision_data['action_plan']
                                    st.write("**Action Plan:**")
                                    if action_plan.get('immediate_actions'):
                                        st.write("**Immediate Actions:**")
                                        for action in action_plan['immediate_actions']:
                                            st.write(f"• {action}")
                                    
                                    if action_plan.get('timeline_weeks'):
                                        st.write(f"**Timeline:** {action_plan['timeline_weeks']} weeks")
                                    
                                    if action_plan.get('key_milestones'):
                                        st.write("**Key Milestones:**")
                                        for milestone in action_plan['key_milestones']:
                                            st.write(f"• {milestone}")
                                
                                # Display team assignment
                                if decision_data.get('team_assignment'):
                                    team = decision_data['team_assignment']
                                    st.write("**Team Assignment:**")
                                    if team.get('primary_owner'):
                                        st.write(f"**Primary Owner:** {team['primary_owner']}")
                                    
                                    if team.get('support_team'):
                                        st.write("**Support Team:**")
                                        for member in team['support_team']:
                                            st.write(f"• {member}")
                                    
                                    if team.get('responsibilities'):
                                        st.write("**Responsibilities:**")
                                        for person, responsibility in team['responsibilities'].items():
                                            st.write(f"• **{person}:** {responsibility}")
                                
                                # Display risk management
                                if decision_data.get('risk_management'):
                                    risk_mgmt = decision_data['risk_management']
                                    st.write("**Risk Management:**")
                                    if risk_mgmt.get('primary_risks'):
                                        st.write("**Primary Risks:**")
                                        for risk in risk_mgmt['primary_risks']:
                                            st.write(f"• {risk}")
                                    
                                    if risk_mgmt.get('mitigation_strategies'):
                                        st.write("**Mitigation Strategies:**")
                                        for strategy in risk_mgmt['mitigation_strategies']:
                                            st.write(f"• {strategy}")
                                
                                # Display success criteria
                                if decision_data.get('success_criteria'):
                                    success = decision_data['success_criteria']
                                    st.write("**Success Criteria:**")
                                    if success.get('quantitative'):
                                        st.write("**Quantitative:**")
                                        for metric in success['quantitative']:
                                            st.write(f"• {metric}")
                                    
                                    if success.get('qualitative'):
                                        st.write("**Qualitative:**")
                                        for outcome in success['qualitative']:
                                            st.write(f"• {outcome}")
                                
                                # Display next review date
                                if decision_data.get('next_review_date'):
                                    st.write(f"**Next Review Date:** {decision_data['next_review_date']}")
                                    
                            except (json.JSONDecodeError, TypeError):
                                # Fallback to raw display if JSON parsing fails
                                decision_content = safe_content_display(result['decision'])
                                st.write(decision_content)
                        
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

if __name__ == "__main__":
    main()
