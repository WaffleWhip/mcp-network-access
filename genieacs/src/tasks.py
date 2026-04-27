import json
from typing import Optional
from .api import call_genieacs, get_device_by_identifier


async def ont_list_tasks(sn_or_id: Optional[str] = None) -> list:
    """TOOL: Task Queue Monitor."""
    try:
        params = {}
        if sn_or_id:
            device = await get_device_by_identifier(sn_or_id)
            params["query"] = json.dumps({"device": device["_id"]})
        return await call_genieacs("GET", "/tasks/", params=params)
    except Exception as e:
        return [{"error": str(e)}]


async def ont_delete_task(task_id: str) -> str:
    """TOOL: Queue Manager (Cleanup)."""
    try:
        await call_genieacs("DELETE", f"/tasks/{task_id}")
        return f"Task {task_id} successfully removed from queue."
    except Exception as e:
        return f"Error: {str(e)}"