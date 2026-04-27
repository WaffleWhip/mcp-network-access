import json
from typing import Optional
from .api import call_genieacs, get_device_by_identifier


async def ont_list_faults(sn_or_id: Optional[str] = None) -> list:
    """TOOL: Protocol Error & Fault Diagnostics."""
    try:
        params = {}
        if sn_or_id:
            device = await get_device_by_identifier(sn_or_id)
            params["query"] = json.dumps({"device": device["_id"]})
        return await call_genieacs("GET", "/faults/", params=params)
    except Exception as e:
        return [{"error": str(e)}]