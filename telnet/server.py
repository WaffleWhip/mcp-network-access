"""Telnet Driver MCP - Pure Independent Telnet Driver"""
from fastmcp import FastMCP, Context
from typing import Optional, List, Literal

from src.telnet import login, send_command, send_button, is_logged_in, close_session

mcp = FastMCP("Telnet-Driver")

@mcp.tool()
async def olt_login(ctx: Context, host: str, user: str, password: str,
                    ep: Optional[str] = None, port: int = 23) -> dict:
    """
    Start a persistent Telnet session to an OLT.
    You need host, user, password. 'ep' is the enable password (optional).
    Example: olt_login(host="192.168.1.1", user="admin", password="secret")
    """
    try:
        enable_pwd = ep if ep else password
        res = await login(host, port, user, password, enable_pwd)
        return {"status": "success", "output": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def olt_send_command(ctx: Context, host: str, command: str = "",
                           commands: Optional[List[str]] = None) -> dict:
    """
    Send CLI command(s) to an active Telnet session.
    'command' for single command, 'commands' for multiple in sequence.
    Example: olt_send_command(host="192.168.1.1", command="show version")
    """
    if not is_logged_in(host):
        return {"status": "error", "message": f"NOT_LOGGED_IN: Please call olt_login first for {host}"}
    try:
        clean_commands = [c for c in (commands or []) if c and c.lower() != 'null']
        target_command = command if (command and command.lower() != 'null') else None
        res, err = await send_command(host, target_command, clean_commands)
        return {"status": "error" if err else "success", "output": res or err}
    except Exception as e:
        return {"status": "error", "message": str(e)}

ButtonKey = Literal["enter", "space", "quit", "esc", "up", "down", "left", "right", "tab"]

@mcp.tool()
async def olt_send_button(ctx: Context, host: str, button: ButtonKey = "enter") -> dict:
    """
    Send a predefined button press to interact with pagers or prompts.
    Choose one of: enter, space, quit, esc, up, down, left, right, tab
    Example: olt_send_button(host="192.168.1.1", button="enter")
    """
    if not is_logged_in(host):
        return {"status": "error", "message": "Session not found. Login first."}
    try:
        res, err = await send_button(host, button)
        return {"status": "error" if err else "success", "output": res or err}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002)