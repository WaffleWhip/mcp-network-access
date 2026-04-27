"""OLT Driver MCP - Pure Independent Terminal Driver"""
from fastmcp import FastMCP, Context
from typing import Optional, List

# Import logic directly from vt.py
from src.vt import login, send_command, send_button, is_logged_in, close_session

mcp = FastMCP("Ultimate-OLT-Driver")

@mcp.tool()
async def vt_login(ctx: Context, host: str, user: str, password: str, 
                   ep: Optional[str] = None, port: int = 23) -> dict:
    """
    Start a persistent Telnet session to an OLT.
    AI MUST provide host, user, and password (fetch from database MCP first).
    'ep' is the enable password (optional).
    """
    try:
        enable_pwd = ep if ep else password
        res = await login(host, port, user, password, enable_pwd)
        return {"status": "success", "output": res}
    except Exception as e: 
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def vt_send_command(ctx: Context, host: str, command: str = "", 
                          commands: Optional[List[str]] = None) -> dict:
    """
    Send CLI command(s) to an active terminal session.
    - 'command': The primary string command to send (e.g. "show version").
    - 'commands': Optional list of strings to send multiple commands.
    """
    if not is_logged_in(host): 
        return {"status": "error", "message": f"NOT_LOGGED_IN: Please call vt_login first for {host}"}
    try:
        clean_commands = [c for c in (commands or []) if c and c.lower() != 'null']
        target_command = command if (command and command.lower() != 'null') else None
        res, err = await send_command(host, target_command, clean_commands)
        return {"status": "error" if err else "success", "output": res or err}
    except Exception as e: 
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def vt_send_button(ctx: Context, host: str, button: str = " ") -> dict:
    """
    Send a raw terminal button press (Space, Enter, q).
    Use button=' ' (space) to scroll through --More-- pagers.
    """
    if not is_logged_in(host):
        return {"status": "error", "message": "Session not found. Login first."}
    try:
        res, err = await send_button(host, button)
        return {"status": "error" if err else "success", "output": res or err}
    except Exception as e: 
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def vt_status(host: str) -> dict:
    """Check if the session for a specific host is currently active."""
    return {"status": "success", "logged_in": is_logged_in(host)}

@mcp.tool()
async def vt_logout(host: str) -> dict:
    """Close and clean up an active terminal session."""
    close_session(host)
    return {"status": "success", "message": f"Session for {host} closed"}

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002)
