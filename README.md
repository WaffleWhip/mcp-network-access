# MCP Network Access

Collection of Model Context Protocol (MCP) servers for telecommunication network management. Built with [FastMCP](https://gofastmcp.com).

## Architecture

- **Databases MCP**: Centralized inventory for OLT credentials and SOP knowledge base.
- **GenieACS MCP**: TR-069 interaction for ONT management (SSID, WiFi, Diagnostics).
- **OLT MCP**: Direct CLI interaction with OLTs (Nokia, Huawei, ZTE, Fiberhome) via Telnet/SSH.

## Getting Started

Each service contains an `install/` directory with:
- `deploy.sh`: Environment setup (venv, dependencies).
- `systemd.sh`: Service automation.

Refer to individual READMEs in each directory for tool documentation.
