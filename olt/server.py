"""OLT MCP - 3 Tools: telnet, command, inventory"""

import os, yaml
from pathlib import Path
from fastmcp import FastMCP
from typing import Optional, List, Any
import asyncio

from src.telnet import (
    connect as vt_connect,
    send_command,
    close_session,
    is_logged_in,
    _heartbeat,
    get_status,
    set_wait,
    get_btn_map,
)
from src.database import (
    list_inventory,
    list_knowledge,
    edit_inventory,
    edit_knowledge,
)

mcp = FastMCP("olt")

BUTTONS_FILE = Path(__file__).parent / "storage" / "buttons.yaml"

HOST_LOCKS = {}
HOST_PENDING = {}


def load_buttons():
    if BUTTONS_FILE.exists():
        with open(BUTTONS_FILE) as f:
            return yaml.safe_load(f)
    return {}


async def wait_for_host(host: str, wait_for_previous: Optional[bool]):
    if not wait_for_previous:
        return
    if host not in HOST_LOCKS:
        HOST_LOCKS[host] = asyncio.Lock()
    lock = HOST_LOCKS[host]
    if lock.locked():
        HOST_PENDING[host] = True
        await lock.acquire()
        HOST_PENDING[host] = False
    else:
        await lock.acquire()


def release_host(host: str):
    if host in HOST_LOCKS and HOST_LOCKS[host].locked():
        HOST_LOCKS[host].release()


# ============ TELNET ============


@mcp.tool()
async def telnet(
    action: str,
    host: Optional[str] = None,
    value: Optional[str] = None,
    seconds: Optional[float] = None,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Telnet tool with sub-commands: create, send, wait, status, buttons

    - create: Create new session (host required)
    - send: Send command(s) or buttons (host, value required)
    - wait: Set wait time in seconds (host, seconds required)
    - status: Check session status (host required)
    - buttons: Show valid buttons (no params)
    """
    if not hasattr(mcp, "_heartbeat_started"):
        asyncio.create_task(_heartbeat())
        mcp._heartbeat_started = True

    try:
        if action in ("create", "send"):
            if not host:
                return {"error": "host required"}
            await wait_for_host(host, wait_for_previous)

        if action == "create":
            if not host:
                return {"error": "host required for create"}
            close_session(host)
            result = await vt_connect(host)
            return result

        elif action == "send":
            if not host or not value:
                return {"error": "host and value required for send"}
            if not is_logged_in(host):
                await vt_connect(host)
                await asyncio.sleep(0.2)

            if "," in value:
                cmds = [c.strip() for c in value.split(",") if c.strip()]
                result, err = await send_command(host, commands=cmds)
            else:
                result, err = await send_command(host, command=value)

            if err:
                return {"error": err}
            return result

        elif action == "wait":
            if not host or seconds is None:
                return {"error": "host and seconds required for wait"}
            return set_wait(host, seconds)

        elif action == "status":
            if not host:
                return {"error": "host required for status"}
            return get_status(host)

        elif action == "buttons":
            return load_buttons()

        return {
            "error": f"Unknown action: {action}. Valid: create, send, wait, status, buttons"
        }

    finally:
        if action in ("create", "send"):
            release_host(host)


# ============ COMMAND ============


@mcp.tool()
def command(
    action: str,
    host: Optional[str] = None,
    syntax: Optional[str] = None,
    hint: Optional[str] = None,
    description: Optional[str] = None,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Command knowledge base with actions: list, save, update, delete

    - list: List commands (host required, syntax optional)
    - save: Save new command (host, syntax, hint, description required)
    - update: Update command (host, syntax required)
    - delete: Delete command (host, syntax required)
    """
    if action == "list":
        if not host:
            return {"error": "host required"}
        knowledge = list_knowledge(host)
        if syntax:
            found = [k for k in knowledge if k["syntax"] == syntax]
            return found[0] if found else {"error": f"Command '{syntax}' not found"}
        return ", ".join(k["syntax"] for k in knowledge) if knowledge else ""

    elif action == "save":
        if not host or not syntax or not hint or not description:
            return {"error": "host, syntax, hint, description all required for save"}
        hint_list = [h.strip() for h in hint.split(",") if h.strip()]
        return edit_knowledge("save", host, syntax, hint_list, description)

    elif action == "update":
        if not host or not syntax:
            return {"error": "host and syntax required for update"}
        hint_list = [h.strip() for h in hint.split(",") if h.strip()] if hint else None
        return edit_knowledge("update", host, syntax, hint_list, description or "")

    elif action == "delete":
        if not host or not syntax:
            return {"error": "host and syntax required for delete"}
        return edit_knowledge("delete", host, syntax)

    return {"error": f"Unknown action: {action}. Valid: list, save, update, delete"}


# ============ INVENTORY ============


@mcp.tool()
def inventory(
    action: str,
    name: Optional[str] = None,
    host: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    vendor: Optional[str] = None,
    model: Optional[str] = None,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Inventory with actions: list, save, update, delete

    - list: List OLTs (name optional)
    - save: Add new OLT (all fields required)
    - update: Update OLT (name required)
    - delete: Delete OLT (host required)
    """
    if action == "list":
        inventory = list_inventory()
        if name:
            found = [i for i in inventory if i["name"] == name]
            return found[0] if found else {"error": f"OLT '{name}' not found"}
        return ", ".join(item["name"] for item in inventory) if inventory else ""

    elif action == "save":
        if not name or not host or not user or not password or not vendor or not model:
            return {
                "error": "name, host, user, password, vendor, model all required for save"
            }
        return edit_inventory(
            "save",
            {
                "name": name,
                "host": host,
                "user": user,
                "password": password,
                "vendor": vendor,
                "model": model,
            },
        )

    elif action == "update":
        if not name:
            return {"error": "name required for update"}
        data = {"name": name}
        if host:
            data["host"] = host
        if user:
            data["user"] = user
        if password:
            data["password"] = password
        if vendor:
            data["vendor"] = vendor
        if model:
            data["model"] = model
        return edit_inventory("update", data)

    elif action == "delete":
        if not host:
            return {"error": "host required for delete"}
        return edit_inventory("delete", {"host": host})

    return {"error": f"Unknown action: {action}. Valid: list, save, update, delete"}


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002, stateless_http=True)
