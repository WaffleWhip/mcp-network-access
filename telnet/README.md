# Telnet MCP

CLI terminal interaction for Multi-Vendor OLTs via persistent Telnet sessions.

## Tools

- `olt_login(host, user, password)`: Start persistent session to OLT. Supports Nokia ISAM, Huawei MA5600/MA5800, ZTE C300/C600, Fiberhome AN5116/AN6000.
- `olt_send_command(host, command)`: Send CLI command to active session. Session persists until timeout.
- `olt_send_button(host, button)`: Send raw button press for pager navigation. Options: enter, space, quit, esc, up, down, left, right, tab.

## Setup

```bash
cd telnet
bash install/build.sh
bash install/systemd.sh
```