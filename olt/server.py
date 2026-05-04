"""OLT Manager - Terminal Driver & Knowledge Base"""
from fastmcp import FastMCP
from typing import Optional, Any
import asyncio

from src.telnet import (
    connect as vt_connect, send_command, send_button, close_session, 
    is_logged_in, _heartbeat, get_last_buffer, set_preferred_length
)
from src.database import list_inventory, list_knowledge, edit_inventory, edit_knowledge

mcp = FastMCP("OLT-Manager")

def wrap_result(host: str, note: Optional[str] = None) -> str:
    """Returns raw terminal state based on preferred line length."""
    terminal_text = get_last_buffer(host)
    if note:
        return f"{terminal_text}\n\n---\nNOTE: {note}"
    return terminal_text

@mcp.tool()
def list(host: Optional[str] = None, detail: bool = False) -> Any:
    """List OLTs from inventory.
    
    - list(): returns name, host, vendor, model.
    - list(host="10.x.x.x", detail=True): returns user + password for one OLT.
    """
    try:
        result = list_inventory(host)
        if detail and not host:
            return "Error: host required for detail view"
        if not detail:
            for item in result:
                item.pop('user', None)
                item.pop('password', None)
        return result
    except Exception as e: return str(e)

@mcp.tool()
def command(action: str, host: str, syntax: Optional[str] = None,
             path: Optional[str] = None, description: str = "") -> Any:
    """Manage OLT command sequences. 
    NOTE: 'path' should contain steps executed AFTER login.
    
    - action="list": See sequences for this host.
    - action="save": syntax="show version", path="config, show version"
    """
    try:
        if action == "list":
            return list_knowledge(host)
        elif action == "save":
            if not syntax or not path:
                return "Error: syntax and path required"
            return edit_knowledge("save", host, syntax, path.split(", "), description)
        elif action == "delete":
            if not syntax: return "Error: syntax required"
            return edit_knowledge("delete", host, syntax)
        return "Error: invalid action"
    except Exception as e: return str(e)

@mcp.tool()
async def telnet(host: str, port: int = 23, length: int = 20) -> Any:
    """Open connection and set terminal view settings.
    
    - length: How many lines of output to show (default 20).
    Returns current screen state.
    """
    if not hasattr(mcp, "_heartbeat_started"):
        asyncio.create_task(_heartbeat())
        mcp._heartbeat_started = True
    try:
        if not is_logged_in(host):
            await vt_connect(host, port)
        
        set_preferred_length(host, length)
        return wrap_result(host)
    except Exception as e: return str(e)

@mcp.tool()
async def telnet_send(host: str, type: str, value: str) -> Any:
    """Send command or button to terminal.
    
    - BATCHING: Separate multiple commands with ", ".
    - TYPE: 'command' for text, 'button' for 'space', 'enter', 'q'.
    """
    try:
        if not is_logged_in(host):
            return "Error: NOT_CONNECTED. Call telnet first."

        if type == "button":
            btn_map = {"space": " ", "enter": "\n", "q": "q"}
            btn = btn_map.get(value.lower(), "\n")
            await send_command(host, commands=[btn])
            return wrap_result(host)
        else:
            # Execute command(s)
            if "," in value:
                cmds = [c.strip() for c in value.split(",") if c.strip()]
                await send_command(host, commands=cmds)
                target_cmd = cmds[-1]
            else:
                await send_command(host, command=value)
                target_cmd = value

            # AI-DECISION KNOWLEDGE CHECK (No hardcoded error patterns)
            knowledge = list_knowledge(host)
            known_syntaxes = [k['syntax'].lower() for k in knowledge]
            
            # Check prompt state
            buffer = get_last_buffer(host)
            last_line = buffer.strip().split('\n')[-1]
            is_operational = any(p in last_line for p in ["#", ">"])

            # Credential check
            inventory = list_inventory(host)
            creds = []
            if inventory:
                olt = inventory[0]
                creds = [str(olt.get('user','')).lower(), str(olt.get('password','')).lower()]
            
            is_cred = target_cmd.lower() in creds
            is_discovery = target_cmd.strip() in ["?", ""]

            note = None
            # Only suggest save if post-login and not already known
            if is_operational and target_cmd.lower() not in known_syntaxes and not is_cred and not is_discovery:
                note = f"New command '{target_cmd}' discovered. You decide: if this worked, save it using the 'command' tool."
            
            return wrap_result(host, note=note)

    except Exception as e: return str(e)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002, stateless_http=True)
