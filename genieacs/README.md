# GenieACS MCP

TR-069 interface for remote ONT management through GenieACS server.

## Quick Install

Run this one-line command on your server:

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/genieacs/install.sh | bash
```

## Tools

- `ont_list()`: List all ONTs that have informed the GenieACS server.
- `ont_params(sn_or_id)`: Dump full TR-069 parameter tree for a device.
- `ont_custom(sn_or_id, path, value, refresh)`: GET or SET specific TR-069 parameter.
- `ont_tasks(sn_or_id)`: Monitor live command queue.
- `ont_faults(sn_or_id)`: View fault logs.
- `ont_delete_task(task_id)`: Remove task from queue.
- `ont_reboot(sn_or_id)`: Remote power cycle ONT.

## Structure

- `server.py`: MCP Bridge server.
- `install.sh`: Unified installer (root requirement).
- `start.sh`: Startup wrapper for services (MongoDB, Redis, GenieACS, MCP).
- `genieacs/`: Core GenieACS source and data.

---
[Back to main README](../README.md)
