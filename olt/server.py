"""OLT MCP - Terminal Driver & Knowledge Base"""

from fastmcp import FastMCP
from typing import Optional, List, Any
import asyncio

from src.telnet import (
    connect as vt_connect,
    send_command,
    send_button,
    close_session,
    is_logged_in,
    _heartbeat,
    get_last_buffer,
    set_preferred_length,
)
from src.database import list_inventory, list_knowledge, edit_inventory, edit_knowledge

mcp = FastMCP("OLT-MCP")


def wrap_result(host: str, note: Optional[str] = None) -> str:
    """Returns raw terminal state."""
    terminal_text = get_last_buffer(host)
    if note:
        return f"{terminal_text}\n\n---\nNOTE: {note}"
    return terminal_text


@mcp.tool()
def inventory(
    action: str = "list",
    host: Optional[str] = None,
    data: Optional[dict] = None,
    detail: bool = False,
) -> Any:
    """Manage OLT inventory (credentials and IPs).

    - action="list": returns name, host, vendor, model.
    - action="list" + detail=True: returns user + password (requires host).
    - action="save" + data={name, host, user, password, vendor, model}: Add/Update OLT.
    - action="delete" + host: Remove OLT.
    """
    try:
        if action == "list":
            result = list_inventory(host)
            if detail and not host:
                return "Error: detail=True requires host parameter"
            if not detail:
                for item in result:
                    item.pop("user", None)
                    item.pop("password", None)
            return result
        elif action == "save":
            if not data:
                return "Error: data dict required for save"
            return edit_inventory("save", data)
        elif action == "delete":
            if not host:
                return "Error: host required for delete"
            from src.config import INFRA_DB

            conn = __import__("sqlite3").connect(INFRA_DB)
            conn.execute("DELETE FROM olt_credentials WHERE host = ?", (host,))
            conn.commit()
            conn.close()
            return f"Success: Inventory '{host}' deleted"
        return "Error: invalid action"
    except Exception as e:
        return str(e)


@mcp.tool()
def command(
    action: str,
    host: str,
    syntax: Optional[str] = None,
    path: Optional[str] = None,
    description: str = "",
) -> Any:
    """Knowledge Base of operational hints and recipes.

    AI GUIDELINE: Always check for hints before discovering new commands.
    If a hint exists, YOU must execute the steps manually via telnet_send.

    - action="list": Get hints/recipes for this host.
    - action="save": Store a verified hint (e.g. syntax="show version", path="config, show version").
    - action="delete": Remove a hint.

    NOTE: If output needs pagination, include buttons in your manual execution.
    """
    try:
        if action == "list":
            return list_knowledge(host)
        elif action == "save":
            if not syntax or not path:
                return "Error: syntax and path required"
            return edit_knowledge("save", host, syntax, path.split(", "), description)
        elif action == "delete":
            if not syntax:
                return "Error: syntax required"
            return edit_knowledge("delete", host, syntax)
        return "Error: invalid action"
    except Exception as e:
        return str(e)


@mcp.tool()
async def telnet(
    host: str, port: int = 23, length: int = 20, force: bool = False
) -> Any:
    """Open telnet connection to OLT.

    IMPORTANT: Session persists between calls. Use force=True ONLY if stuck or
    need fresh connection. Check is_logged_in status first.

    - length: Number of terminal lines to return (default 20, max 100).
    - force: Force close existing session and start fresh (default False).
             USE WHEN: previous session stuck, login failed, or OLT not responding.
    """
    if not hasattr(mcp, "_heartbeat_started"):
        asyncio.create_task(_heartbeat())
        mcp._heartbeat_started = True
    try:
        if force:
            close_session(host)
        if not is_logged_in(host):
            await vt_connect(host, port)

        set_preferred_length(host, length)
        return wrap_result(host)
    except Exception as e:
        return str(e)


@mcp.tool()
async def telnet_send(host: str, type: str, value: str) -> Any:
    """Send command or button to OLT terminal.

    IMPORTANT: Session must exist first. If "NOT_CONNECTED", call telnet() first.

    LOGIN FLOW for each vendor:
    - ZTE: username -> password (wait for prompt after each)
    - HUAWEI: username -> password
    - FIBERHOME: Login: -> Password: (use 'admin'/'admin' or check inventory)
    - NOKIA: username -> password

    TROUBLESHOOTING:
    - If stuck at username prompt after login: OLT device-side session active.
      Use telnet(host, force=True) to force fresh connection.
    - If "Login failed" or "locked": Too many failed attempts. Wait 5-10 min
      or use telnet(host, force=True) to get fresh session.

    - BATCHING: Separate multiple commands with ", ".
      Example: "enable, show running, quit"
    - PAGINATION: Include [SPACE] after commands that paginate.
      Example: "show card, [SPACE], q"
    - TYPE: 'command' for text input, 'button' for special keys.
      Buttons: 'enter', 'space', 'q' (quit)
    """

    try:
        if not is_logged_in(host):
            await vt_connect(host)
            await asyncio.sleep(0.2)

        if type == "button":
            btn_map = {"space": " ", "enter": "\n", "q": "q"}
            btn = btn_map.get(value.lower(), "\n")
            await send_command(host, commands=[btn])
            return wrap_result(host)
        else:
            if "," in value:
                cmds = [c.strip() for c in value.split(",") if c.strip()]
                await send_command(host, commands=cmds)
                target_cmd = cmds[-1]
            else:
                await send_command(host, command=value)
                target_cmd = value

            knowledge = list_knowledge(host)
            known_syntaxes = [k["syntax"].lower() for k in knowledge]
            buffer = get_last_buffer(host)
            last_line = buffer.strip().split("\n")[-1]
            is_operational = any(p in last_line for p in ["#", ">"])

            inventory_data = list_inventory(host)
            creds = []
            if inventory_data:
                olt = inventory_data[0]
                creds = [
                    str(olt.get("user", "")).lower(),
                    str(olt.get("password", "")).lower(),
                ]

            is_cred = target_cmd.lower() in creds
            is_discovery = target_cmd.strip() in ["?", ""]

            note = None
            if (
                is_operational
                and target_cmd.lower() not in known_syntaxes
                and not is_cred
                and not is_discovery
            ):
                note = f"New command '{target_cmd}' discovered. Save it using the 'command' tool if it worked."

            return wrap_result(host, note=note)

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002, stateless_http=True)
