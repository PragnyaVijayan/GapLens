"""
Router Agent - Accesses external data sources through FastAPI endpoints
"""

import aiohttp
import requests
from typing import Dict, List, Any, Optional
from config import EXTERNAL_API_ENDPOINTS, API_BASE_URL, API_TIMEOUT

class DataRouter:
    """Routes data requests to appropriate external sources."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or API_BASE_URL
        self.endpoints = EXTERNAL_API_ENDPOINTS
        self.timeout = API_TIMEOUT
    
    # Async methods for async contexts
    async def get_employee_skills(self) -> Dict[str, Any]:
        """Get employee skills data from external API."""
        return await self._make_async_request(self.endpoints['employee_skills'])
    
    async def get_project_requirements(self) -> Dict[str, Any]:
        """Get project requirements from external API."""
        return await self._make_async_request(self.endpoints['project_requirements'])
    
    async def get_team_composition(self) -> Dict[str, Any]:
        """Get team composition data from external API."""
        return await self._make_async_request(self.endpoints['team_composition'])
    
    async def get_skill_market_data(self) -> Dict[str, Any]:
        """Get skill market data from external API."""
        return await self._make_async_request(self.endpoints['skill_market_data'])
    
    async def analyze_skill_gaps(self, project_id: str) -> Dict[str, Any]:
        """Analyze skill gaps for a specific project."""
        return await self._make_async_request(f"/api/analysis/skill-gaps?project_id={project_id}")
    
    # Sync methods for non-async contexts
    def get_employee_skills_sync(self) -> Dict[str, Any]:
        """Get employee skills data synchronously."""
        return self._make_sync_request(self.endpoints['employee_skills'])
    
    def get_project_requirements_sync(self) -> Dict[str, Any]:
        """Get project requirements synchronously."""
        return self._make_sync_request(self.endpoints['project_requirements'])
    
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
            return {"error": f"Connection error: {str(e)}"}

# Global router instance
router = DataRouter()

def get_router() -> DataRouter:
    """Get the global router instance."""
    return router
