from mcp.server.fastmcp import FastMCP
import json

mcp=FastMCP("Database")

@mcp.tool()
async def get_employees_info(location:str)->str:
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
    
    print(employees)
    return json.dumps(employees)


@mcp.tool()
async def get_projects_info(location:str)->str:
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
    print(projects)
    return json.dumps(projects)

if __name__=="__main__":
    mcp.run(transport="streamable-http")