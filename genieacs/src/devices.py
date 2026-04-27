import asyncio
from typing import Optional
from .api import call_genieacs, get_device_by_identifier, extract_path


async def ont_list_all() -> list:
    """TOOL: Device Inventory Browser."""
    try:
        return await call_genieacs("GET", "/devices/", params={"projection": "_id,DeviceID.SerialNumber,_lastInform"})
    except Exception as e:
        return [{"error": str(e)}]


async def ont_get_all_params(sn_or_id: str) -> dict:
    """TOOL: Device Deep Discovery & Path Mapping."""
    try:
        return await get_device_by_identifier(sn_or_id)
    except Exception as e:
        return {"error": str(e)}


async def ont_custom_parameter(sn_or_id: str, path: str, value: Optional[str] = None, refresh: bool = False) -> dict:
    """TOOL: Direct Parameter Interaction (GET/SET)."""
    try:
        device = await get_device_by_identifier(sn_or_id)
        dev_id = device["_id"]
        if value is not None:
            task = {"name": "setParameterValues", "parameterValues": [[path, value, "xsd:string"]]}
            await call_genieacs("POST", f"/devices/{dev_id}/tasks", data=task, params={"connection_request": ""})
            return {"status": f"SET task for {path} queued."}
        if refresh:
            task = {"name": "refreshObject", "objectName": path}
            await call_genieacs("POST", f"/devices/{dev_id}/tasks", data=task, params={"connection_request": ""})
            await asyncio.sleep(5)
            device = await get_device_by_identifier(sn_or_id)
        val = extract_path(device, path)
        return {"_id": dev_id, path: val if val else "Path not found. Verify path via ont_get_all_params discovery tool."}
    except Exception as e:
        return {"error": str(e)}