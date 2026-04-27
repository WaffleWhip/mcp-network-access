import os
import httpx
import json
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

GENIEACS_URL = os.getenv("GENIEACS_URL", "http://127.0.0.1:7557")
GENIEACS_AUTH = None
if os.getenv("GENIEACS_USER") and os.getenv("GENIEACS_PASS"):
    GENIEACS_AUTH = (os.getenv("GENIEACS_USER"), os.getenv("GENIEACS_PASS"))


async def call_genieacs(method: str, path: str, data: Any = None, params: dict = None):
    url = f"{GENIEACS_URL}{path}"
    async with httpx.AsyncClient(auth=GENIEACS_AUTH, timeout=30.0) as client:
        if method == "GET": response = await client.get(url, params=params)
        elif method == "POST": response = await client.post(url, json=data, params=params)
        elif method == "DELETE": response = await client.delete(url, params=params)
        else: raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json() if response.status_code != 204 else None


async def get_device_by_identifier(identifier: str) -> dict:
    query = {"$or": [{"_id": identifier}, {"DeviceID.SerialNumber": identifier}, {"_id": {"$regex": identifier}}]}
    devices = await call_genieacs("GET", "/devices/", params={"query": json.dumps(query)})
    if not devices: raise ValueError(f"Device '{identifier}' not found.")
    return devices[0]


def extract_path(device: dict, path: str) -> Any:
    current = device
    for part in path.split('.'):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current