import importlib
from typing import Any
from .api import call_genieacs, get_device_by_identifier, extract_path

async def list_onts():
    return await call_genieacs("GET", "/devices/", params={"projection": "_id,DeviceID.SerialNumber,_lastInform"})

async def get_params(sn_or_id):
    return await get_device_by_identifier(sn_or_id)

async def set_custom(sn_or_id, path, value=None, refresh=False):
    import asyncio
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
    return {"_id": dev_id, path: val if val else "Path not found."}

async def list_tasks(sn_or_id=None):
    import json
    params = {}
    if sn_or_id:
        device = await get_device_by_identifier(sn_or_id)
        params["query"] = json.dumps({"device": device["_id"]})
    return await call_genieacs("GET", "/tasks/", params=params)

async def list_faults(sn_or_id=None):
    import json
    params = {}
    if sn_or_id:
        device = await get_device_by_identifier(sn_or_id)
        params["query"] = json.dumps({"device": device["_id"]})
    return await call_genieacs("GET", "/faults/", params=params)

async def delete_task(task_id):
    await call_genieacs("DELETE", f"/tasks/{task_id}")
    return f"Task {task_id} removed."

async def reboot_device(sn_or_id):
    device = await get_device_by_identifier(sn_or_id)
    await call_genieacs("POST", f"/devices/{device['_id']}/tasks", data={"name": "reboot"}, params={"connection_request": ""})
    return f"Reboot command sent to {sn_or_id}."
