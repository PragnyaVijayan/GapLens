from fastmcp import FastMCP
import json
import asyncio

mcp_employee_info_server = FastMCP("Employee Info Server")

@mcp_employee_info_server.tool()
async def get_employees_info():
    """Get the employees info."""
    employees = [
        {
            "id": "emp1",
            "name": "John Doe",
            "team": "Engineering",
            "skills": ["python", "aws"],
            "current_project": "ProjectA"
        },
        {
            "id": "emp2",
            "name": "Jane Smith",
            "team": "DevOps",
            "skills": ["kubernetes", "docker"],
            "current_project": "ProjectB"
        }
    ]
    print("Getting employees info")
    return json.dumps(employees)

mcp_project_info_server = FastMCP("Project Info Server")

@mcp_project_info_server.tool()
async def get_projects_info():
    """Get the projects info."""
    projects = [
        {
            "id": "proj1",
            "name": "Cloud Migration",
            "required_skills": ["aws", "kubernetes"],
            "timeline": "3 months",
            "description": "Migrate on-prem services to cloud"
        },
        {
            "id": "proj2",
            "name": "AI Chatbot",
            "required_skills": ["python", "aws"],
            "timeline": "2 months",
            "description": "Build a chatbot using AI"
        }
    ]
    print("Getting projects info")
    return json.dumps(projects)

main_mcp = FastMCP(name="MainApp")

async def setup():
    await main_mcp.import_server(mcp_employee_info_server, prefix="employee")
    await main_mcp.import_server(mcp_project_info_server, prefix="project")

if __name__ == "__main__":
    asyncio.run(setup())
    main_mcp.run(
        transport="http",
        host="127.0.0.1",
        port=4200,
        #path="/my-custom-path",
        log_level="debug",
    )
