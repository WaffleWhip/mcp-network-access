# MCP Network Access

Collection of Model Context Protocol (MCP) servers for telecommunication network management. Built with [FastMCP](https://gofastmcp.com).

## Architecture

- **telnet**: Direct CLI interaction with OLTs (Nokia, Huawei, ZTE, Fiberhome) via Telnet.
- **genieacs**: TR-069 interaction for ONT management via GenieACS.
- **databases**: Centralized inventory for OLT credentials, ONT data, and SOP knowledge base.

## Installation

Each MCP has an `install/` directory with:
- `build.sh`: Install dependencies and setup environment.
- `start.sh`: Start the MCP server (and full stack for genieacs).
- `systemd.sh`: Install as systemd service for auto-restart.
