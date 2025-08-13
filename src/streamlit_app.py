import streamlit as st
import requests

st.set_page_config(page_title="GapLens Analysis", layout="wide")

API_BASE = "http://localhost:8000/api"

# Custom CSS
st.markdown("""
<style>
    body {
        font-family: 'Inter', sans-serif;
    }
    .recommendation-box {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .risk-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .risk-low { background-color: #2ECC71; color: white; }
    .risk-medium { background-color: #F1C40F; color: black; }
    .risk-high { background-color: #E74C3C; color: white; }
</style>
""", unsafe_allow_html=True)

# Fetch projects
projects = requests.get(f"{API_BASE}/projects").json()["projects"]
project_names = {p["name"]: p["id"] for p in projects}

st.title("📊 GapLens Project Analysis")

# Sidebar
st.sidebar.header("⚙️ Configuration")
selected_project_name = st.sidebar.selectbox("Select a project", list(project_names.keys()))
selected_project_id = project_names[selected_project_name]

if st.sidebar.button("Get Recommendation", use_container_width=True):
    with st.spinner("Analyzing project..."):
        rec = requests.post(f"{API_BASE}/recommendations", json={"project_id": selected_project_id}).json()
        st.session_state["recommendation"] = rec["recommendation"]

# Show recommendation
if "recommendation" in st.session_state:
    rec = st.session_state["recommendation"]
    print(f"DEBUG: Recommendation: {rec['recommendation']}")

    st.subheader(f"📋 Recommendation Details for {selected_project_name}")

    risk_class = f"risk-{rec['recommendation']['risk_level'].lower()}"
    st.markdown(f"<span class='risk-badge {risk_class}'>Risk: {rec['recommendation']['risk_level'].capitalize()}</span>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="recommendation-box">
        <p><strong>📌 Type:</strong> {rec['recommendation']['type']}</p>
        <p><strong>⏳ Timeline:</strong> {rec['recommendation']['timeline']}</p>
        <p><strong>📝 Details:</strong> {rec['recommendation']['details']}</p>
        <p><strong>💡 Reasoning:</strong> {rec['recommendation']['reasoning']}</p>
        <p><strong>👤 Employee Name:</strong> {rec['recommendation']['employee_name']}</p>
        <p><strong>👤 Employee Department:</strong> {rec['recommendation']['department']}</p>
        <p><strong> Project Start Date:</strong> {rec['recommendation']['project_start_date']}</p>
    </div>
    """, unsafe_allow_html=True)

# Project info
with st.expander("ℹ️ Project Information"):
    st.write({
        "Project ID": selected_project_id,
        "Project Name": selected_project_name
    })

# Health check
if st.sidebar.button("Check Health", use_container_width=True):
    health = requests.get("http://localhost:8000/health").json()
    st.sidebar.success(f"API Status: {health['status']}")
