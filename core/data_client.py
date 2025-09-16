"""
Data Client - Accesses server-side data through FastAPI endpoints
Mimics MCP (Model Context Protocol) pattern where agents access server-side resources
"""

import aiohttp
import requests
from typing import Dict, List, Any, Optional
from config import EXTERNAL_API_ENDPOINTS, API_BASE_URL, API_TIMEOUT

class DataClient:
    """Client for accessing server-side data through FastAPI endpoints."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or API_BASE_URL
        self.endpoints = EXTERNAL_API_ENDPOINTS
        self.timeout = API_TIMEOUT
    
    # Async methods for async contexts
    async def get_employee_skills(self) -> Dict[str, Any]:
        """Get employee skills data from server API."""
        return await self._make_async_request(self.endpoints['employee_skills'])
    
    async def get_project_requirements(self) -> Dict[str, Any]:
        """Get project requirements from server API."""
        return await self._make_async_request(self.endpoints['project_requirements'])
    
    async def get_project_by_id(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID from server API."""
        return await self._make_async_request(f"/api/projects/{project_id}")
    
    async def get_project_skill_gaps(self, project_id: str) -> Dict[str, Any]:
        """Get skill gap analysis for a specific project from server API."""
        return await self._make_async_request(f"/api/analysis/project/{project_id}/skill-gaps")
    
    async def get_team_composition(self) -> Dict[str, Any]:
        """Get team composition data from server API."""
        return await self._make_async_request(self.endpoints['team_composition'])
    
    async def get_skill_market_data(self) -> Dict[str, Any]:
        """Get skill market data from server API."""
        return await self._make_async_request(self.endpoints['skill_market_data'])
    
    async def analyze_skill_gaps(self, project_id: str) -> Dict[str, Any]:
        """Analyze skill gaps for a specific project via server API."""
        return await self._make_async_request(f"/api/analysis/skill-gaps?project_id={project_id}")
    
    # Sync methods for non-async contexts
    def get_employee_skills_sync(self) -> Dict[str, Any]:
        """Get employee skills data synchronously."""
        return self._make_sync_request(self.endpoints['employee_skills'])
    
    def get_project_requirements_sync(self) -> Dict[str, Any]:
        """Get project requirements synchronously."""
        return self._make_sync_request(self.endpoints['project_requirements'])
    
    def get_project_by_id_sync(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID synchronously."""
        return self._make_sync_request(f"/api/projects/{project_id}")
    
    def get_project_skill_gaps_sync(self, project_id: str) -> Dict[str, Any]:
        """Get skill gap analysis for a specific project synchronously."""
        return self._make_sync_request(f"/api/analysis/project/{project_id}/skill-gaps")
    
    def get_team_composition_sync(self) -> Dict[str, Any]:
        """Get team composition data synchronously."""
        return self._make_sync_request(self.endpoints['team_composition'])
    
    def get_skill_market_data_sync(self) -> Dict[str, Any]:
        """Get skill market data synchronously."""
        return self._make_sync_request(self.endpoints['skill_market_data'])
    
    # Private helper methods
    async def _make_async_request(self, endpoint: str) -> Dict[str, Any]:
        """Make an async HTTP request to the specified endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{endpoint}", timeout=self.timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Failed to fetch data: {response.status}"}
        except Exception as e:
            return {"error": f"Connection error: {str(e)}"}
    
    def _make_sync_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a synchronous HTTP request to the specified endpoint."""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to fetch data: {response.status_code}"}
        except Exception as e:
            print(f"⚠️ API connection failed: {e}")
            print("🔄 Falling back to mock data...")
            return self._get_mock_data(endpoint)
    
    def _get_mock_data(self, endpoint: str) -> Dict[str, Any]:
        """Get mock data when API is not available."""
        from infrastructure.mock_data import (
            mock_employees,
            mock_projects,
            mock_teams,
            mock_skill_market_data
        )
        
        if endpoint == "/api/employees/skills":
            return {
                "employees": mock_employees,
                "total_employees": len(mock_employees),
                "total_skills": sum(len(emp.get("skills", [])) for emp in mock_employees),
                "unique_skills": list(set(skill["name"] for emp in mock_employees for skill in emp.get("skills", [])))
            }
        elif endpoint == "/api/projects":
            return {
                "projects": mock_projects,
                "total_projects": len(mock_projects)
            }
        elif endpoint == "/api/teams/composition":
            return {
                "teams": mock_teams,
                "total_teams": len(mock_teams)
            }
        elif endpoint == "/api/skills/market-data":
            return mock_skill_market_data
        else:
            return {"error": f"No mock data available for endpoint: {endpoint}"}

# Global data client instance
data_client = DataClient()

def get_data_client() -> DataClient:
    """Get the global data client instance."""
    return data_client
