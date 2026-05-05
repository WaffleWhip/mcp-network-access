# OLT MCP

Telnet CLI management for OLTs (Nokia, Huawei, ZTE, Fiberhome).

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/olt/install.sh | bash
```

## Tools

| Tool | Actions | Description |
|------|---------|-------------|
| `telnet` | create, send, wait, status, buttons | Telnet session management |
| `command` | list, save, update, delete | Command knowledge base |
| `inventory` | list, save, update, delete | OLT inventory |

## Examples

```python
# Connect to OLT
telnet(action="create", host="10.0.0.1")

# Login
telnet(action="send", value="admin,password123")

# Send command
telnet(action="send", value="show version")

# Save command to DB
command(action="save", host="10.0.0.1", syntax="show version",
        hint="show version", description="Show system version")
```

## Files

```
olt/
├── server.py          # MCP server
├── src/               # Source modules
├── storage/            # Data (buttons.yaml, olt.db)
└── install.sh          # Systemd + UV installer
```
