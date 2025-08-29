# GapLens Recommendation App

A focused Streamlit application for AI-powered skills gap analysis and team optimization recommendations.

## Features

- **Project Selection**: Choose from available projects for analysis
- **AI Analysis**: Generate comprehensive recommendations using multi-agent workflow
- **Scope Control**: Analyze within department or company-wide scope
- **Clean Output**: Focused, actionable recommendations without verbose logging

## Quick Start

1. **Start the Backend**:
   ```bash
   cd infrastructure
   python api.py
   ```

2. **Set Environment Variables**:
   ```bash
   export ANTHROPIC_API_KEY="your_api_key_here"
   # Or create a .env file with:
   # ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Run the Recommendation App**:
   ```bash
   streamlit run recommendation_app.py
   ```

## Usage

1. **Select Project**: Choose a project from the dropdown list
2. **Choose Scope**: Select department-only or company-wide analysis
3. **Generate Recommendations**: Click "Generate AI Recommendations"
4. **View Results**: See skills gap analysis and actionable recommendations

## What You'll Get

- **Skills Gap Analysis**: Identified missing skills and their criticality
- **Upskilling Recommendations**: Team members who can learn required skills
- **Internal Transfer Options**: Employees who can move between teams
- **Hiring Suggestions**: When external hiring is necessary
- **Implementation Plan**: Specific actions with timelines and milestones

## Technical Details

- **Multi-Agent Workflow**: Uses perception, analysis, and decision agents
- **Reasoning Patterns**: Each agent uses specialized reasoning (COT, REACT, TOT)
- **Memory System**: Persistent session storage and logging
- **API Integration**: Connects to FastAPI backend for data

## Troubleshooting

- **Backend Not Running**: Ensure `infrastructure/api.py` is running
- **API Key Missing**: Set `ANTHROPIC_API_KEY` environment variable
- **No Projects**: Check that the backend has project data loaded

## Differences from Full App

This app focuses solely on the recommendation functionality:
- ✅ Project selection and analysis
- ✅ AI-powered recommendations
- ✅ Clean, focused output
- ❌ Dashboard and other pages
- ❌ Verbose logging and debugging
- ❌ Complex navigation

Perfect for users who want to quickly get AI recommendations without the full system complexity.
