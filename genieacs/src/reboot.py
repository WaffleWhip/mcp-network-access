from .api import call_genieacs, get_device_by_identifier


async def ont_reboot(sn_or_id: str) -> str:
    """TOOL: Remote Power Cycle."""
    try:
        device = await get_device_by_identifier(sn_or_id)
        await call_genieacs("POST", f"/devices/{device['_id']}/tasks", data={"name": "reboot"}, params={"connection_request": ""})
        return f"Reboot command sent to {sn_or_id}."
    except Exception as e:
        return f"Error: {str(e)}"