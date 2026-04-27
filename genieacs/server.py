"""GenieACS MCP Server - Modular Architecture"""
import os
from typing import Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP

# Define paths
BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / "genieacs" / ".env"

# Load environment from the new backend folder structure
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    # Fallback to local .env if exists
    load_dotenv()

# Import logic from modular source files
from src.devices import ont_list_all, ont_get_all_params, ont_custom_parameter
from src.tasks import ont_list_tasks, ont_delete_task
from src.faults import ont_list_faults
from src.reboot import ont_reboot

mcp = FastMCP("GenieACS-Ultimate")

@mcp.tool()
async def ont_list() -> Any:
    """List all ONTs that have currently informed the GenieACS server."""
    return await ont_list_all()

@mcp.tool()
async def ont_params(sn_or_id: str) -> Any:
    """Discovery Tool: Dumps the entire TR-069 parameter tree for a specific device."""
    return await ont_get_all_params(sn_or_id)

@mcp.tool()
async def ont_custom(sn_or_id: str, path: str, value: Optional[str] = None, refresh: bool = False) -> Any:
    """Direct TR-069 Parameter Interaction. Use to GET or SET specific values (SSID, etc)."""
    return await ont_custom_parameter(sn_or_id, path, value, refresh)

@mcp.tool()
async def ont_tasks(sn_or_id: Optional[str] = None) -> Any:
    """Monitor the live command queue (pending/processing tasks)."""
    return await ont_list_tasks(sn_or_id)

@mcp.tool()
async def ont_faults(sn_or_id: Optional[str] = None) -> Any:
    """View TR-069 protocol errors and fault logs for diagnostics."""
    return await list_faults(sn_or_id)

@mcp.tool()
async def ont_delete_task_tool(task_id: str) -> Any:
    """Remove a stuck or unnecessary task from the command queue."""
    return await ont_delete_task(task_id)

@mcp.tool()
async def ont_reboot_tool(sn_or_id: str) -> Any:
    """Remote Power Cycle (Reboot) the ONT device via TR-069."""
    return await ont_reboot(sn_or_id)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
