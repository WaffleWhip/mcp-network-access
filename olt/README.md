# OLT MCP

CLI terminal interaction for Multi-Vendor OLTs.

## Tools

- `vt_login`: Start persistent session (supports Nokia, Huawei, ZTE, Fiberhome).
- `vt_send_command`: Send CLI commands to active session.
- `vt_send_button`: Send raw button presses (Space/Enter/q).
- `vt_status`: Check session activity.
- `vt_logout`: Close session.

## Setup

```bash
cd olt
./install/deploy.sh
./install/systemd.sh
```
