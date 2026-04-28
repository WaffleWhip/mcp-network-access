# GenieACS MCP

TR-069 interface for remote ONT management through GenieACS server.

## Tools

- `ont_list()`: List all ONTs that have informed the GenieACS server.
- `ont_params(sn_or_id)`: Dump full TR-069 parameter tree for a device.
- `ont_custom(sn_or_id, path, value, refresh)`: GET or SET specific TR-069 parameter (SSID, WiFi settings, etc).
- `ont_tasks(sn_or_id)`: Monitor live command queue (pending/processing tasks).
- `ont_faults(sn_or_id)`: View TR-069 protocol errors and fault logs.
- `ont_delete_task(task_id)`: Remove stuck task from command queue.
- `ont_reboot(sn_or_id)`: Remote power cycle (reboot) ONT device.

## Setup

```bash
cd genieacs
bash install/build.sh
bash install/systemd.sh
```
