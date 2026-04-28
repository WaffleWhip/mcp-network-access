# Telnet MCP

CLI terminal interaction for Multi-Vendor OLTs.

## Tools

- `olt_login`: Start persistent session (supports Nokia, Huawei, ZTE, Fiberhome).
- `olt_send_command`: Send CLI commands to active session.
- `olt_send_button`: Send raw button presses (Space/Enter/q) for pagers.

## Setup

```bash
cd telnet
bash install/build.sh
bash install/systemd.sh
```