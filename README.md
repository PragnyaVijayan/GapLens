# 🔍 GapLens - Proactive Skill Gap Management System

An AI-powered proactive skill-gap management system that uses AI agents to detect upcoming skill gaps in projects and recommend whether to upskill, transfer, or hire employees.

## 🚀 Features

- **AI-Powered Analysis**: Uses LLMs to understand natural language project descriptions and extract skill requirements
- **Multi-Agent Architecture**: Coordinated agents for project intake, skill extraction, workforce analysis, gap detection, and recommendations
- **Structured Decision Making**: Generates confidence-scored recommendations with evidence and alternatives
- **Comprehensive Workflow**: End-to-end skill gap management from project ingestion to decision records
- **Modern UI**: FastAPI backend with Streamlit frontend for easy interaction
- **MCP Integration**: Ready for Model Context Protocol integration with external tools
- **Audit Trail**: Complete trace logging for all agent decisions and tool calls

## 🏗️ Architecture

The system follows a **layered cognitive model**:

- **Perception**: Ingest project definitions from Notion, Jira, Confluence, PDFs, etc.
- **Short-Term Memory**: Ephemeral state per project ingestion run
- **Long-Term Memory**: Store skill graphs, employee history, project history, decisions
- **Cognition**: Analyze skill gaps, make decisions, perform feasibility modeling
- **Action**: Generate training plans, transfers, job postings, schedule updates
- **Reflection**: Record outcomes, update skill levels, improve decision models

## 🤖 Agents

### 1. Project Intake Agent
- Ingests project definitions from various sources
- Extracts skill requirements using LLM processing
- Validates project data completeness

### 2. Skill Extraction Agent
- Processes natural language project descriptions
- Normalizes skills using canonical taxonomy
- Assesses required skill levels and constraints

### 3. Workforce Data Agent
- Manages employee skill data and availability
- Finds skill matches and assesses individual gaps
- Tracks training history and certifications

### 4. Gap Analysis Agent
- Identifies skill gaps between requirements and workforce
- Assesses gap impact and prioritizes based on project criticality
- Generates comprehensive gap reports

### 5. Recommendation Agent
- Generates structured recommendations for gap resolution
- Evaluates upskill, transfer, and hiring options
- Optimizes recommendations across multiple projects

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- pip or uv package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd GapLens

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

## 🚀 Quick Start

### 1. Run Demo Workflow
```bash
python main.py demo
```

This will:
- Run the complete skill gap management workflow
- Show results and next steps
- Demonstrate the system capabilities

### 2. Test Individual Components
```bash
# Test agents
python main.py test-agents

# Run workflow only
python main.py workflow

# Start API server
python main.py api

# Start Streamlit UI
python main.py ui
```

### 3. Access the System

- **FastAPI Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **API Health**: http://localhost:8000/health

## 📊 Usage Examples

### Running Gap Analysis
```python
from src.orchestrator import SkillGapOrchestrator

# Initialize orchestrator
orchestrator = SkillGapOrchestrator()

# Run complete workflow
results = await orchestrator.run_workflow()

# Check results
if results["success"]:
    summary = results["summary"]
    print(f"Projects analyzed: {summary['final_results']['projects_analyzed']}")
    print(f"Gaps identified: {summary['final_results']['gaps_identified']}")
```

### Using Individual Agents
```python
from src.agents import GapAnalysisAgent

# Initialize agent
agent = GapAnalysisAgent()

# Analyze gaps for a project
gaps = await agent._analyze_project_gaps({"project_id": "project_001"})
print(f"Found {gaps['data']['total_gaps']} skill gaps")
```

### API Integration
```python
import requests

# Run gap analysis
response = requests.post("http://localhost:8000/api/analysis/gaps", json={
    "project_id": "project_001",
    "include_recommendations": True
})

gaps_data = response.json()
print(f"Analysis completed: {gaps_data['total_gaps']} gaps found")
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# MCP Configuration (for future use)
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
```

### Workflow Configuration
```json
{
  "priority": "high",
  "include_optimization": true,
  "max_analysis_time": 300,
  "confidence_threshold": 0.8
}
```

## 📁 Project Structure

```
GapLens/
├── src/
│   ├── agents/                 # AI agent implementations
│   │   ├── project_intake_agent.py
│   │   ├── skill_extraction_agent.py
│   │   ├── workforce_data_agent.py
│   │   ├── gap_analysis_agent.py
│   │   └── recommendation_agent.py
│   ├── api/                    # FastAPI backend
│   │   └── main.py
│   ├── ui/                     # Streamlit frontend
│   │   └── streamlit_app.py
│   ├── models.py               # Data models and schemas
│   ├── mock_data.py            # Mock data and connectors
│   ├── mcp_base.py             # Base MCP server class
│   └── orchestrator.py         # LangGraph workflow orchestrator
├── main.py                     # Main entry point
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/workflow/status` - Workflow status
- `POST /api/workflow/run` - Run complete workflow

### Data Endpoints
- `GET /api/projects` - Get all projects
- `GET /api/employees` - Get all employees
- `GET /api/analysis/recommendations` - Get recommendations
- `GET /api/decisions` - Get decision records

### Analysis Endpoints
- `POST /api/analysis/gaps` - Run gap analysis
- `GET /api/dashboard/summary` - Get dashboard summary
- `GET /api/trace-logs` - Get audit trail

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_orchestrator.py
```

### Test Individual Components
```bash
# Test orchestrator
python -m pytest tests/test_orchestrator.py -v

# Test agents
python -m pytest tests/test_agents.py -v
```

## 🚧 Development

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding New Agents
1. Create agent class inheriting from `BaseMCPServer`
2. Implement required tools and methods
3. Add to `src/agents/__init__.py`
4. Update orchestrator workflow if needed
5. Add tests

### Adding New Data Sources
1. Create connector class
2. Implement data ingestion methods
3. Add to mock data or real connectors
4. Update relevant agents

## 🔮 Future Enhancements

- **Real LLM Integration**: Connect to OpenAI, Anthropic, or local LLMs
- **Vector Database**: Implement FAISS or Pinecone for skill embeddings
- **Real-time Updates**: WebSocket support for live project updates
- **Advanced Analytics**: Machine learning for skill gap prediction
- **Integration APIs**: Connect to real Notion, Jira, HRIS, LMS systems
- **Multi-tenant Support**: Organization and user management
- **Mobile App**: React Native mobile application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the API docs at `/docs`
- **Examples**: See the demo workflow and test files

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Uses [FastAPI](https://fastapi.tiangolo.com/) for high-performance API
- [Streamlit](https://streamlit.io/) for rapid UI development
- [Model Context Protocol](https://modelcontextprotocol.io/) for agent communication

---

**GapLens** - Making skill gap management proactive, intelligent, and actionable. 🚀 