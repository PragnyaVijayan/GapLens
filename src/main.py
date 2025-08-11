from langchain_ollama import OllamaLLM
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from typing import Dict, List, Optional
import json

# --- Mock Data ---
MOCK_DATA = {
    "employees": [
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
    ],
    "projects": [
        {
            "id": "proj1",
            "name": "Cloud Migration",
            "required_skills": ["aws", "kubernetes"],
            "timeline": "3 months",
            "description": "Migrate on-prem services to cloud"
        }
    ]
}

# --- Tool Functions ---
def get_employee_skills(employee_id: str) -> List[str]:
    print(f"Getting skills for employee: {employee_id}")
    try:
        employee = next((e for e in MOCK_DATA["employees"] if e["id"] == employee_id), None)
        return employee["skills"] if employee else []
    except Exception as e:
        print(f"Error in get_employee_skills: {e}")
        return []

def get_project_requirements(project_id: str) -> Dict:
    print(f"Getting requirements for project: {project_id}")
    try:
        return next((p for p in MOCK_DATA["projects"] if p["id"] == project_id), {})
    except Exception as e:
        print(f"Error in get_project_requirements: {e}")
        return {}

def find_skill_matches(skill: str) -> List[Dict]:
    print(f"Finding matches for skill: {skill}")
    try:
        return [e for e in MOCK_DATA["employees"] if skill in e["skills"]]
    except Exception as e:
        print(f"Error in find_skill_matches: {e}")
        return []

# --- Tools ---


tools = [
    Tool(
        name="get_employee_skills",
        func=get_employee_skills,
        description="Gets the skills of a specific employee. Input: employee_id"
    ),
    Tool(
        name="get_project_requirements",
        func=get_project_requirements,
        description="Gets the requirements of a specific project. Input: project_id"
    ),
    Tool(
        name="find_skill_matches",
        func=find_skill_matches,
        description="Finds all employees who have a specific skill. Input: skill_name"
    )
]

# --- LLM & Parser ---
llm = OllamaLLM(model="mistral")

response_schemas = [
    ResponseSchema(
        name="recommendation",
        description="The final structured recommendation as a JSON object"
    )
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# --- Prompt Template ---
prompt = PromptTemplate.from_template("""
You are a Skill Gap Analyzer helping managers make decisions about team resources.

{format_instructions}

You MUST respond with a JSON object containing a 'recommendation' field with ONE of these exact formats:

1. For upskilling:
{{
  "recommendation": {{
    "type": "UPSKILL",
    "employee_name": "John Doe",
    "current_skills": ["python", "aws"],
    "skill_to_learn": "kubernetes",
    "training_time": "3 weeks",
    "reason": "John already has related cloud skills and can quickly learn Kubernetes.",
    "risk_level": "low"
  }}
}}

2. For transfers:
{{
  "recommendation": {{
    "type": "TRANSFER",
    "employee_name": "Jane Smith",
    "current_team": "DevOps",
    "skills": ["kubernetes", "docker"],
    "notice_period": "2 weeks",
    "impact": "Minimal impact on current project.",
    "risk_level": "medium"
  }}
}}

3. For hiring:
{{
  "recommendation": {{
    "type": "HIRE",
    "required_skills": ["aws", "kubernetes"],
    "experience_level": "senior",
    "must_have_skills": ["kubernetes"],
    "nice_to_have_skills": ["aws"],
    "time_to_hire": "1-2 months",
    "risk_level": "medium"
  }}
}}

Use tools if needed. Output must start with Final Answer: followed by the JSON object.
Current objective: {input}

{agent_scratchpad}
""")

# --- Analysis Function ---
def analyze_project_gaps(project_id: str) -> Optional[Dict]:
    print(f"\nStarting analysis for project '{project_id}'...")

    try:
        project = get_project_requirements(project_id)
        if not project:
            print(f"Project {project_id} not found.")
            return None

        format_instructions = output_parser.get_format_instructions()

        format_instructions = output_parser.get_format_instructions()

        # Fix: Inject required template variables
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt.partial(
                format_instructions=format_instructions,
                tools="\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
                tool_names=", ".join([tool.name for tool in tools])
            )
        )

        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        result = executor.invoke({
            "input": f"""Analyze project '{project_id}'.
            Step 1: Get project requirements.
            Step 2: Check team skills.
            Step 3: Recommend ONE option based on the project timeline ({project['timeline']}).
            Step 4: Final output must be valid JSON with a single recommendation."""
        })

        # --- Debug: Raw Output ---
        raw_output = result.get("output", "")
        print("\n--- Raw LLM Output ---")
        print(raw_output)

        # --- Parse Output ---
        parsed_output = output_parser.parse(raw_output)
        return parsed_output["recommendation"]

    except Exception as e:
        print(f"Error in analyze_project_gaps: {e}")
        return None

# --- Entry Point ---
def main():
    print("Starting Skill Gap Analysis System...\n")
    result = analyze_project_gaps("proj1")
    if result:
        print("\n--- Final Structured Recommendation ---")
        print(json.dumps(result, indent=2))
    else:
        print("\nAnalysis failed.")

if __name__ == "__main__":
    main()
