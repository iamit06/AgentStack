from typing import Optional, Dict, Any
from crewai_tools import BaseTool
import os
import requests
from json import JSONDecodeError
from agentstack.exceptions import ToolError


class PipedreamClient:
    """Client for interacting with Pipedream API"""
    def __init__(self, api_key: str):
        self.base_url = "https://api.pipedream.com/v1/connect"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def list_apps(self, query: str = None) -> dict:
        """List available Pipedream apps"""
        params = {"q": query} if query else {}
        return self._request("GET", "/apps", params=params)

    def list_components(self, app: str) -> dict:
        """List available components for an app"""
        return self._request("GET", f"/actions?app={app}")

    def get_component_definition(self, key: str) -> dict:
        """Get component definition and props"""
        return self._request("GET", f"/components/{key}")

    def run_action(self, component_id: str, inputs: Dict[str, Any]) -> dict:
        """Execute a Pipedream component action"""
        return self._request("POST", "/actions/run", json={
            "id": component_id,
            "configured_props": inputs
        })

    def deploy_source(self, component_id: str, webhook_url: str, config: Dict[str, Any]) -> dict:
        """Deploy a Pipedream component source"""
        return self._request("POST", "/triggers/deploy", json={
            "id": component_id,
            "webhook_url": webhook_url,
            "configured_props": config
        })

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make request to Pipedream API"""
        response = requests.request(method, f"{self.base_url}{path}",
                                 headers=self.headers, **kwargs)
        if not response.ok:
            raise PipedreamToolError(f"API request failed: {response.text}")
        try:
            return response.json()
        except JSONDecodeError:
            raise PipedreamToolError("Invalid JSON response from Pipedream API")


class PipedreamToolError(ToolError):
    """Specific exception for Pipedream tool errors"""
    pass


class PipedreamListAppsTool(BaseTool):
    name: str = "List Pipedream Apps"
    description: str = "List available Pipedream apps with optional search query"

    def __init__(self, api_key: str):
        self.client = PipedreamClient(api_key)
        super().__init__()

    def _execute(self, query: str = None) -> str:
        """List available Pipedream apps with optional search query"""
        return self.client.list_apps(query)["data"]


class PipedreamListComponentsTool(BaseTool):
    name: str = "List Pipedream Components"
    description: str = "List available components for a Pipedream app"

    def __init__(self, api_key: str):
        self.client = PipedreamClient(api_key)
        super().__init__()

    def _execute(self, app: str) -> str:
        """List available components for the specified app"""
        return self.client.list_components(app)["data"]


class PipedreamGetPropsTool(BaseTool):
    name: str = "Get Pipedream Component Properties"
    description: str = "Get component definition and configuration options"

    def __init__(self, api_key: str):
        self.client = PipedreamClient(api_key)
        super().__init__()

    def _execute(self, key: str) -> str:
        """Get component definition and configuration options"""
        return self.client.get_component_definition(key)["data"]


class PipedreamActionTool(BaseTool):
    name: str = "Execute Pipedream Action"
    description: str = "Execute a Pipedream component action with specified inputs"

    def __init__(self, api_key: str):
        self.client = PipedreamClient(api_key)
        super().__init__()

    def _execute(self, component_id: str, inputs: Dict[str, Any]) -> str:
        """
        Execute a Pipedream component action.

        Args:
            component_id: The ID of the Pipedream component to execute
            inputs: Dictionary of input parameters for the component

        Returns:
            str: JSON response from the component execution

        Raises:
            PipedreamToolError: If the API request fails or returns an error
        """
        return self.client.run_action(component_id, inputs)


class PipedreamSourceTool(BaseTool):
    name: str = "Deploy Pipedream Source"
    description: str = "Deploy a Pipedream source component with webhook configuration"

    def __init__(self, api_key: str):
        self.client = PipedreamClient(api_key)
        super().__init__()

    def _execute(self, component_id: str, webhook_url: str, config: Dict[str, Any]) -> str:
        """
        Deploy a Pipedream component source.

        Args:
            component_id: The ID of the Pipedream component to deploy
            webhook_url: The URL where events will be sent
            config: Dictionary of configuration parameters for the component

        Returns:
            str: JSON response from the component deployment

        Raises:
            PipedreamToolError: If the API request fails or returns an error
        """
        return self.client.deploy_source(component_id, webhook_url, config)
