# GenieACS MCP

TR-069 interface for remote ONT management through GenieACS server.

## Quick Install

Run this one-line command on your server:

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/genieacs/install.sh | bash
```

## Tools

- `ont_list()`: List all ONTs.
- `ont_params(sn_or_id)`: Dump device parameters.
- `ont_custom(sn_or_id, path, value, refresh)`: GET or SET parameter.
- `ont_tasks(sn_or_id)`: Monitor command queue.
- `ont_faults(sn_or_id)`: View fault logs.
- `ont_delete_task(task_id)`: Remove task.
- `ont_reboot(sn_or_id)`: Reboot device.

## Structure

- `server.py`: MCP Bridge.
- `install.sh`: Unified installer.
- `start.sh`: Startup wrapper.
- `genieacs/`: Source and data.

---
[Back to main README](../README.md)
