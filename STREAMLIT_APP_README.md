# GapLens Streamlit App - Updated for LangGraph Workflow

## Overview

The Streamlit app has been updated to use the current LangGraph-based multi-agent orchestration system. This provides a cleaner separation between what's displayed in the UI and what's logged to the terminal.

## Key Changes

### 1. **LangGraph Workflow Integration**
- Replaced the legacy orchestrator approach with the current LangGraph workflow
- Uses `MultiAgentWorkflow` from `core.workflow`
- Integrates with the existing agent system (Perception, Analysis, Decision)

### 2. **Output Separation**
- **UI Display**: Shows only essential information (recommendations, summary, key metrics)
- **Terminal Output**: Detailed execution logs, agent interactions, and technical details
- **Content Truncation**: Long outputs are truncated in UI with a note to check terminal

### 3. **New Navigation Structure**
- **Dashboard**: Overview and system information
- **AI Analysis**: Main interface for running LangGraph workflows
- **Project Analysis**: Project-specific analysis using LangGraph
- **Department Overview**: Department insights
- **Team Skills**: Team analysis
- **Employee Database**: Employee management

## How to Use

### 1. **Start the App**
```bash
streamlit run streamlit_app.py
```

### 2. **Set Up API Keys**
- Ensure `ANTHROPIC_API_KEY` is set in your environment
- The app will show if the key is configured correctly
- Manual key input is available as a fallback

### 3. **Run AI Analysis**
1. Go to **"AI Analysis"** page
2. Select a predefined question or enter a custom one
3. Choose your AI backend (anthropic, groq, or fake for testing)
4. Click **"Run AI Analysis"** to execute the LangGraph workflow

### 4. **Test the Workflow**
- Use the **"Test Workflow"** button to verify the system works
- This runs with the fake backend to avoid API calls
- Check the terminal for detailed execution logs

### 5. **Project Analysis**
1. Go to **"Project Analysis"** page
2. Select a project from the dropdown
3. Choose analysis scope and backend
4. Run the LangGraph workflow for project-specific insights

## What You'll See

### In the UI (Streamlit App)
- ✅ **Analysis Summary**: Key metrics and status
- 🎯 **AI Recommendations**: Main actionable insights
- 🧠 **Analysis Details**: Core analysis results
- 🔧 **Technical Details**: Developer information (expandable)

### In the Terminal
- 🔍 **Workflow Execution Logs**: Step-by-step agent execution
- 👁️ **Perception Agent**: Input analysis and entity extraction
- 🧠 **Analysis Agent**: Skills gap analysis and insights
- 🎯 **Decision Agent**: Final recommendations
- 🎼 **Orchestrator**: Workflow coordination
- 📊 **Memory System**: Session tracking and storage

## Backend Options

### 1. **Anthropic** (Recommended)
- Uses Claude models for high-quality analysis
- Requires `ANTHROPIC_API_KEY`
- Best for production use

### 2. **Groq**
- Fast inference with Groq models
- Requires `GROQ_API_KEY`
- Good for quick testing

### 3. **Fake** (Testing)
- Simulated responses without API calls
- Perfect for development and testing
- No API keys required

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Check your `.env` file
   - Use the manual key input in the debug section
   - Verify the key is valid

2. **Workflow Fails**
   - Check the terminal for detailed error logs
   - Use the test workflow button to verify system health
   - Ensure all dependencies are installed

3. **No Output in UI**
   - Check the terminal for execution logs
   - Verify the workflow completed successfully
   - Look for error messages in the terminal

### Debug Information

The app includes a debug section that shows:
- Environment variable status
- Current working directory
- API key configuration
- System status

## Architecture

```
Streamlit App → LangGraph Workflow → Multi-Agent System
     ↓                    ↓                    ↓
UI Display ← Parsed Results ← Agent Coordination
     ↓                    ↓                    ↓
User Interface    Terminal Logs    Memory System
```

## Benefits of the New System

1. **Cleaner UI**: Only essential information is displayed
2. **Better Debugging**: Detailed logs in terminal for developers
3. **Current Integration**: Uses the latest LangGraph workflow system
4. **Flexible Backends**: Support for multiple AI providers
5. **Testing Support**: Built-in testing with fake backend
6. **Memory Integration**: Full session tracking and persistence

## Next Steps

1. **Test the System**: Use the test workflow button first
2. **Run Simple Analysis**: Try predefined questions
3. **Custom Analysis**: Enter your own skills gap questions
4. **Project Analysis**: Analyze specific projects
5. **Monitor Terminal**: Check logs for detailed execution information

The updated app provides a much cleaner user experience while maintaining full transparency through terminal logging for developers and power users.
