# OLT MCP (Telnet)

Multi-vendor OLT terminal interaction via persistent Telnet sessions.

## Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/olt/install.sh | bash
```

## Core Tools

| Tool | Mode | Description |
|------|------|-------------|
| `inventory` | View/Edit | Manage OLT credentials and IPs (list, save, delete). |
| `telnet` | View | Open session and observe terminal state with dynamic length. |
| `telnet_send` | Action | Send commands or buttons (Batching supported with ", "). |
| `command` | Knowledge | Manage reusable post-login command sequences. |

## Usage Examples

### 1. Inventory & Login
```bash
# List all OLTs (Brief)
inventory(action="list")

# Get credentials for specific OLT
inventory(action="list", host="10.x.x.x", detail=True)

# Save/Update OLT
inventory(action="save", data={"name": "OLT-1", "host": "10.x.x.x", "user": "admin", "password": "pass", "vendor": "zte", "model": "C600"})
```

### 2. Operations
```bash
# Open session
telnet(host="10.x.x.x", length=50)

# Batch execution
telnet_send(host="10.x.x.x", type="command", value="admin, password, show card")

# Handle pagination
telnet_send(host="10.14.35.111", type="button", value="space")
```

### 3. Knowledge Management
```bash
# Save post-login sequence
command(
    action="save", 
    host="10.x.x.x", 
    syntax="show full config", 
    path="configure terminal, show running-config, [ENTER], [SPACE], exit", 
    description="Config dump"
)
```

---
Note: This system relies on AI agents to interpret terminal states from raw text output.

[Back to main README](../README.md)
