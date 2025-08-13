import asyncio
import os
import json
from dotenv import load_dotenv
from typing import Dict, List

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
else:
    print("Warning: GROQ_API_KEY not found in environment variables")

# ------------------ LLM ------------------
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# ------------------ Tool Wrapper ------------------
def make_tool_for_agent(name: str, agent):
    """Create a LangChain tool that wraps an MCP agent"""
    def tool_func(query: str) -> str:
        try:
            # print(f"DEBUG: Entering tool_func for {name}")
            # print(f"DEBUG: Query received: {query}")
            # print(f"DEBUG: Query type: {type(query)}")
            # print(f"DEBUG: Query repr: {repr(query)}")
            
            # Check if query is already a dict/list
            if isinstance(query, (dict, list)):
                print(f"DEBUG: Query is already structured data: {query}")
                # If it's already structured, use it directly
                if isinstance(query, list) and len(query) > 0:
                    messages = {"messages": query}
                else:
                    messages = {"messages": [{"role": "user", "content": str(query)}]}
            else:
                # Create the message structure
                messages = {"messages": [{"role": "user", "content": str(query)}]}
            
            print(f"DEBUG: Final messages structure: {messages}")
            
            # Use asyncio.run to handle the async call in a sync context
            result = asyncio.run(agent.ainvoke(messages))
            #print(f"DEBUG: Agent result: {result}")
            
            output = result.get("output", str(result))
            #print(f"DEBUG: Extracted output: {output}")
            return output
        except Exception as e:
            # print(f"DEBUG: Exception in tool_func: {type(e).__name__}: {str(e)}")
            # print(f"DEBUG: Exception details: {e}")
            import traceback
            traceback.print_exc()
            return f"Error querying {name}: {str(e)}"
    
    return Tool(
        name=name,
        func=tool_func,
        description=f"Query the {name} MCP server agent for data and analysis"
    )

# ------------------ MCP Agent Setup ------------------
async def setup_agents():
    """Setup MCP agents for different servers"""
    agents = {}
    
    # Create MCP client and get tools directly
    try:
        client = MultiServerMCPClient({
            "MainApp": {
                "url": "http://127.0.0.1:4200/mcp",
                "transport": "streamable_http"
            }
        })
        tools = await client.get_tools()
        agents["MainApp"] = {"client": client, "tools": tools}
        print("✓ MainApp MCP tools loaded successfully")
        print(f"✓ Available tools: {[tool.name for tool in tools]}")
    except Exception as e:
        print(f"Error creating MCP client: {e}")
        return {}
    
    return agents

async def analyze_project_gaps(project_id: str, agents: Dict):
    """Analyze project gaps using MCP agents"""
    # print(f"DEBUG: analyze_project_gaps called with project_id: {project_id}")
    # print(f"DEBUG: Available agents: {list(agents.keys())}")
    
    if not agents:
        print("No agents available for analysis")
        return None
    
    # Get the MCP tools directly
    main_app = agents.get("MainApp")
    if not main_app:
        print("MainApp not available")
        return None
    
    tools = main_app["tools"]
    #print(f"DEBUG: Using {len(tools)} MCP tools directly")
    
    # Create the main analysis agent with MCP tools
    #print("DEBUG: Creating react agent...")
    react_agent = create_react_agent(model=llm, tools=tools)
    #print("DEBUG: Creating agent executor...")
    
    # Analysis prompt
    input_text = f"""
    Analyze project '{project_id}' for skill gaps and resource needs.
    
    Step 1: Use the available tools to get employee data and skills
    Step 2: Use the available tools to get project requirements
    Step 3: Analyze team skills vs project requirements
    Step 4: Provide ONE recommendation (UPSKILL OR TRANSFER from other team OR HIRE) based on project timeline
    
    Output must be valid JSON with a single recommendation in this format:
    {{
        "recommendation": {{
            "type": "UPSKILL|TRANSFER|HIRE",
            "details": "specific recommendation details",
            "timeline": "estimated time",
            "risk_level": "low|medium|high",
            "reasoning": "explanation of the recommendation under 50 words"
        }}
    }}
    """
    
    #print(f"DEBUG: About to invoke executor with input: {input_text[:100]}...")
    
    try:
        #print("DEBUG: Executing agent...")
        #result = await executor.ainvoke({"input": input_text})
        result = await react_agent.ainvoke({"messages": input_text})

        #print(f"DEBUG: Execution result: {result}")
        print("Analysis completed successfully")
        recommendation = result["messages"][-1].content
        return recommendation

    except Exception as e:
        # print(f"DEBUG: Exception in executor.ainvoke: {type(e).__name__}: {str(e)}")
        # print(f"DEBUG: Exception details: {e}")
        import traceback
        traceback.print_exc()
        print(f"Error during analysis: {e}")
        return None

# ------------------ Main Entry ------------------
async def main():
    print("Starting Skill Gap Analysis System...\n")
    agents = await setup_agents()
    if not agents:
        print("Failed to setup any agents. Exiting.")
        return

    print(f"✓ Agents setup: {list(agents.keys())}\n")
    for project_id in ["proj1", "proj2", "proj3", "proj4", "proj5"]:
        result = await analyze_project_gaps(project_id, agents)
        print(f"Analysis for project {project_id}: {result}")

    #print("\n--- Analys    is Result ---")
    #print(json.dumps(result, indent=2) if result else "No result returned")

if __name__ == "__main__":
    asyncio.run(main())
