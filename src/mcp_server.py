from fastmcp import FastMCP
import json
import asyncio

# Employee Info Server
mcp_employee_info_server = FastMCP("Employee Info Server")

@mcp_employee_info_server.tool()
async def get_employees_info():
    """Get the employees info."""
    employees = [
        {
            "id": "emp1",
            "name": "John Doe",
            "team": "Engineering",
            "skills": [
                "2 years of experience deploying applications on AWS",
                "Proficient in building and managing Python-based backend services",
                "Experience with CI/CD pipelines and automated deployments"
            ],
            "current_project": "Cloud Migration"
        },
        {
            "id": "emp2",
            "name": "Jane Smith",
            "team": "DevOps",
            "skills": [
                "Skilled in configuring and managing Kubernetes clusters",
                "Experience in containerizing applications using Docker",
                "Familiar with AWS infrastructure and monitoring tools"
            ],
            "current_project": "AI Chatbot"
        },
        {
            "id": "emp3",
            "name": "Alice Johnson",
            "team": "HR",
            "skills": [
                "Experience managing employee onboarding and training programs",
                "Skilled in HR analytics and reporting",
                "Familiar with cloud-based HR platforms like Workday and BambooHR"
            ],
            "current_project": "Talent Acquisition Dashboard"
        },
        {
            "id": "emp4",
            "name": "Bob Lee",
            "team": "IT",
            "skills": [
                "Experienced in managing corporate networks and cloud infrastructure",
                "Ability to troubleshoot hardware and software issues across teams",
                "Skilled in setting up virtual machines and cloud security configurations"
            ],
            "current_project": "IT Infrastructure Upgrade"
        },
        {
            "id": "emp5",
            "name": "Clara Gomez",
            "team": "Design",
            "skills": [
                "Expert in UX/UI design and user research",
                "Proficient with Figma, Adobe XD, and cloud-based design collaboration tools",
                "Experience designing responsive web and mobile interfaces"
            ],
            "current_project": "Website Redesign"
        }
    ]
    print("Getting employees info")
    return json.dumps(employees)

# Project Info Server
mcp_project_info_server = FastMCP("Project Info Server")

@mcp_project_info_server.tool()
async def get_projects_info():
    """Get the projects info."""
    projects = [
        {
            "id": "proj1",
            "name": "Cloud Migration",
            "required_skills": [
                "Ability to provision and manage virtual servers on AWS",
                "Experience performing compute operations in the cloud",
                "Skills in maintaining data warehouses and cloud storage solutions"
            ],
            "timeline": "3 months",
            "description": "Migrate on-prem services to cloud"
        },
        {
            "id": "proj2",
            "name": "AI Chatbot",
            "required_skills": [
                "Experience developing Python applications integrated with AWS services",
                "Ability to set up and manage cloud-based compute and storage resources",
                "Familiarity with deploying AI/ML models in cloud environments"
            ],
            "timeline": "2 months",
            "description": "Build a chatbot using AI"
        },
        {
            "id": "proj3",
            "name": "Talent Acquisition Dashboard",
            "required_skills": [
                "Experience with HR analytics and reporting tools",
                "Ability to integrate cloud-based HR platforms",
                "Skills in designing interactive dashboards for HR teams"
            ],
            "timeline": "1.5 months",
            "description": "Create a dashboard to track hiring metrics and employee progress"
        },
        {
            "id": "proj4",
            "name": "IT Infrastructure Upgrade",
            "required_skills": [
                "Knowledge of corporate networking and cloud security practices",
                "Ability to deploy and manage virtual servers and storage",
                "Experience troubleshooting IT issues in hybrid cloud environments"
            ],
            "timeline": "4 months",
            "description": "Upgrade company IT systems and migrate legacy systems to cloud"
        },
        {
            "id": "proj5",
            "name": "Website Redesign",
            "required_skills": [
                "Proficiency in UX/UI design and user research",
                "Experience with cloud-based design collaboration tools",
                "Ability to create responsive web and mobile designs"
            ],
            "timeline": "2 months",
            "description": "Redesign company website to improve user experience and branding"
        }
    ]
    print("Getting projects info")
    return json.dumps(projects)

# Main MCP
main_mcp = FastMCP(name="MainApp")

async def setup():
    await main_mcp.import_server(mcp_employee_info_server, prefix="employee")
    await main_mcp.import_server(mcp_project_info_server, prefix="project")

if __name__ == "__main__":
    asyncio.run(setup())
    main_mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=4200,
        log_level="debug",
    )
