"""GenieACS MCP Server - Modular Architecture"""
import os
from typing import Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / "genieacs" / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

from src.devices import ont_list_all, ont_get_all_params, ont_custom_parameter
from src.tasks import ont_list_tasks, ont_delete_task
from src.faults import ont_list_faults
from src.reboot import ont_reboot

mcp = FastMCP("GenieACS-MCP")

@mcp.tool()
async def ont_list(ctx: Context) -> Any:
    """List all ONTs that have informed the GenieACS server.
    Example: ont_list()
    """
    return await ont_list_all()

@mcp.tool()
async def ont_params(ctx: Context, sn_or_id: str) -> Any:
    """Dump the entire TR-069 parameter tree for a specific device.
    Example: ont_params(sn_or_id="ALCLB123456")
    """
    return await ont_get_all_params(sn_or_id)

@mcp.tool()
async def ont_custom(ctx: Context, sn_or_id: str, path: str,
                      value: Optional[str] = None, refresh: bool = False) -> Any:
    """GET or SET a specific TR-069 parameter (SSID, etc).
    Example: ont_custom(sn_or_id="ALCLB123456", path="Device.WiFi.SSID")
    """
    return await ont_custom_parameter(sn_or_id, path, value, refresh)

@mcp.tool()
async def ont_tasks(ctx: Context, sn_or_id: Optional[str] = None) -> Any:
    """Monitor the live command queue (pending/processing tasks).
    Example: ont_tasks()
    """
    return await ont_list_tasks(sn_or_id)

@mcp.tool()
async def ont_faults(ctx: Context, sn_or_id: Optional[str] = None) -> Any:
    """View TR-069 protocol errors and fault logs for diagnostics.
    Example: ont_faults()
    """
    return await ont_list_faults(sn_or_id)

@mcp.tool()
async def ont_delete_task(ctx: Context, task_id: str) -> Any:
    """Remove a stuck or unnecessary task from the command queue.
    Example: ont_delete_task(task_id="12345")
    """
    return await ont_delete_task(task_id)

@mcp.tool()
async def ont_reboot(ctx: Context, sn_or_id: str) -> Any:
    """Remote power cycle (reboot) an ONT device via TR-069.
    Example: ont_reboot(sn_or_id="ALCLB123456")
    """
    return await ont_reboot(sn_or_id)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)