"""OLT MCP - Individual Tools: telnet_*, command_*, inventory_*"""

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


# ============ TELNET TOOLS ============


@mcp.tool()
async def telnet_create(
    host: str,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Create new telnet session to OLT host. If session already exists, will reconnect. Recommended: check telnet_status first to continue existing session."""
    if not hasattr(mcp, "_heartbeat_started"):
        asyncio.create_task(_heartbeat())
        mcp._heartbeat_started = True

    await wait_for_host(host, wait_for_previous)
    try:
        close_session(host)
        result = await vt_connect(host)
        return result
    finally:
        release_host(host)


@mcp.tool()
async def telnet_send(
    host: str,
    value: str,
    delay: float,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Send command(s) or buttons to OLT. Use comma as batch delimiter (e.g., 'cmd1,cmd2,(SPACE)'). Best for login sequences, known command paths, or pagination. delay=seconds between each batch (recommended 3s for stability). Returns output directly."""
    await wait_for_host(host, wait_for_previous)
    try:
        if not is_logged_in(host):
            await vt_connect(host)
            await asyncio.sleep(0.2)

        if "," in value:
            cmds = [c.strip() for c in value.split(",") if c.strip()]
            result, err = await send_command(host, commands=cmds, delay=delay)
        else:
            result, err = await send_command(host, command=value)

        if err:
            return {"error": err}
        return result
    finally:
        release_host(host)


@mcp.tool()
def telnet_status(
    host: str,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Check current telnet position/state. Use when agent needs to know current prompt or state."""
    return get_status(host)


@mcp.tool()
def telnet_buttons(
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """List all available buttons. Buttons can be used in batch commands via (NAME) placeholder, e.g., 'display version,(SPACE),q'."""
    return load_buttons()


# ============ COMMAND TOOLS ============


@mcp.tool()
def command_list(
    host: Optional[str] = None,
    syntax: Optional[str] = None,
    hint: Optional[str] = None,
    description: Optional[str] = None,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Search commands from knowledge base. At least 1 param required. Filters: host, syntax (partial match), hint (partial match), description (partial match)."""
    if not host and not syntax and not hint and not description:
        return {
            "error": "at least 1 param required: host, syntax, hint, or description"
        }
    knowledge = list_knowledge(
        host=host, syntax=syntax, hint=hint, description=description
    )
    if not knowledge:
        return ""
    return "\n".join(
        f"[{k['host']}] {k['syntax']}: {k['description']} (hints: {', '.join(k['hint'])})"
        for k in knowledge
    )


@mcp.tool()
def command_save(
    host: str,
    syntax: str,
    hint: str,
    description: str,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Save new command to knowledge base. ALL fields required."""
    if not host or not syntax or not hint or not description:
        return {"error": "host, syntax, hint, description all required"}
    hint_list = [h.strip() for h in hint.split(",") if h.strip()]
    return edit_knowledge("save", host, syntax, hint_list, description)


@mcp.tool()
def command_delete(
    host: str,
    syntax: str,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Delete command from knowledge base. host and syntax required."""
    if not host or not syntax:
        return {"error": "host and syntax required"}
    return edit_knowledge("delete", host, syntax)


# ============ INVENTORY TOOLS ============


@mcp.tool()
def inventory_list(
    name: Optional[str] = None,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """List OLT inventory. name optional."""
    inventory = list_inventory()
    if name:
        found = [i for i in inventory if i["name"] == name]
        return found[0] if found else {"error": f"OLT '{name}' not found"}
    return ", ".join(item["name"] for item in inventory) if inventory else ""


@mcp.tool()
def inventory_save(
    name: str,
    host: str,
    user: str,
    password: str,
    vendor: str,
    model: str,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Add new OLT to inventory. ALL fields required."""
    if not name or not host or not user or not password or not vendor or not model:
        return {"error": "name, host, user, password, vendor, model all required"}
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


@mcp.tool()
def inventory_update(
    name: str,
    host: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    vendor: Optional[str] = None,
    model: Optional[str] = None,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Update existing OLT. name required, others optional."""
    if not name:
        return {"error": "name required"}
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


@mcp.tool()
def inventory_delete(
    host: str,
    wait_for_previous: Optional[bool] = None,
) -> Any:
    """Delete OLT from inventory. host required."""
    if not host:
        return {"error": "host required"}
    return edit_inventory("delete", {"host": host})


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002, stateless_http=True)
