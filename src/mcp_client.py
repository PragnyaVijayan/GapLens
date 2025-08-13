import os
from dotenv import load_dotenv
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
else:
    print("Warning: GROQ_API_KEY not found in environment variables")

async def main():
    client = MultiServerMCPClient(
        {
            # "Employee Info Server": {
            #     "url": "http://localhost:8000/mcp",
            #     "transport": "streamable_http"
            # },
            # "Project Data Server": {
            #     "url": "http://localhost:8000/mcp",
            #     "transport": "streamable_http"
            # }

            "MainApp": {
                "url": "http://localhost:4200/mcp",
                "transport": "streamable_http"
            }
        }
    )

    tools = await client.get_tools()
    model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    agent = create_react_agent(model, tools)

    # Debug: print tools loaded
    print(f"Loaded tools: {[tool.name for tool in tools]}")

    user_message = {"role": "user", "content": "who are all the employees?"}
    print("Calling agent.ainvoke with message:", user_message)

    try:
        employee_response = await agent.ainvoke({"messages": [user_message]})
        #print("Employee response:", employee_response.get("output"))
        # print("Employee response (full):", employee_response)
        # print("Employee response (output):", employee_response.get("output"))
        print("Employee response (text):", employee_response["messages"][-1].content)


    except Exception as e:
        print("Error during agent.ainvoke:", e)
        raise

    # Repeat with projects query
    project_message = {"role": "user", "content": "what are all the projects?"}
    print("Calling agent.ainvoke with message:", project_message)

    try:
        project_response = await agent.ainvoke({"messages": [project_message]})
        #print("Project response:", project_response.get("output"))
        #print("Project response (full):", project_response) 
        print("Project response (text):", project_response["messages"][-1].content)
    except Exception as e:
        print("Error during agent.ainvoke:", e)
        raise

asyncio.run(main())
