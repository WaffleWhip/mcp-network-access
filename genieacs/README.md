# GenieACS MCP

TR-069 bridge for ONT management via GenieACS server.

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/genieacs/install.sh | bash
```

## Tools

| Tool | Description |
|------|-------------|
| `ont_list` | List all ONTs |
| `ont_params` | Dump device parameters |
| `ont_custom` | GET or SET TR-069 parameter |
| `ont_tasks` | Monitor command queue |
| `ont_faults` | View fault logs |
| `ont_delete_task` | Remove task from queue |
| `ont_reboot` | Reboot ONT device |

## Includes

- GenieACS server (MongoDB + Redis)
- MCP bridge on port 8001

## Files

```
genieacs/
├── server.py          # MCP server
├── src/               # Source modules
├── genieacs/          # GenieACS server
└── install.sh         # Systemd + deps installer
```
