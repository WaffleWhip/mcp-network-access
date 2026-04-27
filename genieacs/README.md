# GenieACS MCP

TR-069 interface for remote ONT management.

## Tools

- `ont_list`: List all informed ONTs.
- `ont_params`: Dump full TR-069 parameter tree.
- `ont_custom`: GET/SET specific parameters (e.g., SSID).
- `ont_tasks`: Monitor command queue.
- `ont_faults`: View protocol errors.
- `ont_reboot`: Remote power cycle.

## Setup

```bash
cd genieacs
./install/deploy.sh
./install/systemd.sh
```
