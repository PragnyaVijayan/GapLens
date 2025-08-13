from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import json
import os
from dotenv import load_dotenv

from langchain.tools import Tool
from langchain.schema import HumanMessage
from langchain.agents import AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

app = FastAPI(title="GapLens API", description="API for project gap analysis")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM setup
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# Global variable to store agents
agents = {}

class RecommendationRequest(BaseModel):
    project_id: str

class RecommendationResponse(BaseModel):
    project_id: str
    recommendation: Dict[str, Any]

async def setup_agents():
    """Setup MCP agents for different servers"""
    agents = {}
    
    try:
        print("🔌 Attempting to connect to MCP server at http://127.0.0.1:4200/mcp")
        client = MultiServerMCPClient({
            "MainApp": {
                "url": "http://127.0.0.1:4200/mcp",
                "transport": "streamable_http"
            }
        })
        
        print("📡 Getting MCP tools...")
        tools = await client.get_tools()
        agents["MainApp"] = {"client": client, "tools": tools}
        print("✓ MainApp MCP tools loaded successfully")
        print(f"✓ Available tools: {[tool.name for tool in tools]}")
        return agents
        
    except Exception as e:
        print(f"❌ Error creating MCP client: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return {}

@app.on_event("startup")
async def startup_event():
    """Initialize MCP agents on startup"""
    global agents
    print("🚀 Starting up GapLens API server...")
    agents = await setup_agents()
    if not agents:
        print("⚠️ Warning: Failed to setup MCP agents")
        print("⚠️ The API will not be able to provide recommendations")
    else:
        print("✅ MCP agents initialized successfully")

async def analyze_project_gaps(project_id: str, agents: Dict):
    """Analyze project gaps using MCP agents"""
    if not agents:
        raise HTTPException(status_code=500, detail="No agents available for analysis")
    
    main_app = agents.get("MainApp")
    if not main_app:
        raise HTTPException(status_code=500, detail="MainApp not available")
    
    tools = main_app["tools"]
    
    # Create the main analysis agent with MCP tools
    react_agent = create_react_agent(model=llm, tools=tools)
    
    # Analysis prompt
    input_text = f"""
    Analyze project '{project_id}' for skill gaps and resource needs.
    
    Step 1: Use the available tools to get employee data and skills
    Step 2: Use the available tools to get project requirements
    Step 3: Analyze team/employee skills vs project requirements
    Step 4: Provide ONE recommendation (UPSKILL OR TRANSFER from other team OR HIRE) based on project timeline
    Step 5: Include the name and department of the employee who is recommended for the project
    Step 6: Estimate time it will take to be ready for the project vs the project start date

    Ensure that the responses not have any keys (like "proj1" or "employee1")
    Output must be valid JSON with a single recommendation in this format:
    {{
        "recommendation": {{
            "type": "UPSKILL|TRANSFER|HIRE",
            "details": "specific recommendation details",
            "timeline": "estimated time",
            "risk_level": "low|medium|high",
            "reasoning": "explanation of the recommendation under 50 words",
            "employee_name": "employee name",
            "department": "employee department",
            "project_start_date": "project start date"
        }}
    }}
    """
    
    try:
        result = await react_agent.ainvoke({"messages": input_text})
        recommendation = result["messages"][-1].content
        
        # Try to parse the recommendation as JSON
        try:
            parsed_rec = json.loads(recommendation)
            return parsed_rec
        except json.JSONDecodeError:
            # If it's not valid JSON, return as text
            return {"recommendation": {"type": "ANALYSIS", "details": recommendation, "timeline": "N/A", "risk_level": "N/A", "reasoning": "Raw analysis result"}}
            
    except Exception as e:
        print(f"❌ Error in analyze_project_gaps: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")

@app.get("/api/projects")
async def get_projects():
    """Get all available projects (mocked for now)"""
    projects = [
        {"id": "proj1", "name": "Cloud Migration"},
        {"id": "proj2", "name": "AI Chatbot"},
        {"id": "proj3", "name": "Talent Acquisition Dashboard"},
        {"id": "proj4", "name": "IT Infrastructure Upgrade"},
        {"id": "proj5", "name": "Website Redesign"}
    ]
    return {"projects": projects}

@app.post("/api/recommendations", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """Get recommendation for a specific project"""
    if not agents:
        raise HTTPException(status_code=500, detail="MCP agents not initialized. Cannot provide recommendations.")
    
    try:
        print(f" Analyzing project: {request.project_id}")
        recommendation = await analyze_project_gaps(request.project_id, agents)
        return RecommendationResponse(
            project_id=request.project_id,
            recommendation=recommendation
        )
    except Exception as e:
        print(f"❌ Error in get_recommendation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "agents_loaded": len(agents) > 0,
        "agent_count": len(agents),
        "agent_names": list(agents.keys()) if agents else []
    }

@app.get("/debug/agents")
async def debug_agents():
    """Debug endpoint to check agent status"""
    if not agents:
        return {"error": "No agents loaded"}
    
    debug_info = {}
    for name, agent_data in agents.items():
        tools = agent_data.get("tools", [])
        debug_info[name] = {
            "tools_count": len(tools),
            "tool_names": [tool.name for tool in tools] if tools else []
        }
    
    return debug_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
