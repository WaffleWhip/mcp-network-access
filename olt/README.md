# OLT MCP

Telnet CLI management for OLTs (Nokia, Huawei, ZTE, Fiberhome).

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/olt/install.sh | bash
```

## Tools

### Telnet

| Tool | Description |
|------|-------------|
| `telnet_create` | Create telnet session (max 10s timeout). Recommended: check status first to continue existing session. |
| `telnet_send` | Send command(s) or buttons. Use comma as batch delimiter (e.g., `cmd1,cmd2,(SPACE)`). Best for login sequences, known command paths, or pagination. delay=seconds between each batch (recommended 3s). Returns output directly. |
| `telnet_status` | Check current telnet position/state. Use when agent needs to know current prompt. |
| `telnet_buttons` | List available buttons. Buttons can be used in batch via (NAME) placeholder, e.g., `display version,(SPACE),q`. |

### Command Knowledge Base

| Tool | Description |
|------|-------------|
| `command_list` | Search commands. At least 1 param required: host, syntax, hint, or description. |
| `command_save` | Save command. All fields required: host, syntax, hint, description. |
| `command_delete` | Delete command. Requires: host, syntax. |

### Inventory

| Tool | Description |
|------|-------------|
| `inventory_list` | List OLT inventory. name optional. |
| `inventory_save` | Add OLT. Required: name, host, user, password, vendor, model. |
| `inventory_update` | Update OLT. name required, others optional. |
| `inventory_delete` | Delete OLT. Requires: host. |

## Examples

```python
# Check existing session first (recommended)
telnet_status(host="10.0.0.1")

# Create new session
telnet_create(host="10.0.0.1")

# Send single command
telnet_send(host="10.0.0.1", value="show version", delay=3)

# Batch commands (login + navigation)
telnet_send(host="10.0.0.1", value="admin,password,(ENTER),enable,(ENTER),show version,(ENTER)", delay=3)

# Check current position
telnet_status(host="10.0.0.1")

# Save command to knowledge base
command_save(host="10.0.0.1", syntax="show ont info 0/1/1", 
             hint="show ont info", description="Show ONT info for GPON port")

# Search commands
command_list(host="10.0.0.1", syntax="show ont")
```

## Buttons

Buttons can be used in batch commands using (NAME) placeholder:

| Button | Action |
|--------|--------|
| `(ENTER)` | Send newline |
| `(SPACE)` | Send space |
| `(ESC)` | Escape key |
| `(TAB)` | Tab key |
| `(UP)` | Arrow up |
| `(DOWN)` | Arrow down |
| `(LEFT)` | Arrow left |
| `(RIGHT)` | Arrow right |
| `(BACKSPACE)` | Backspace |

## Architecture

```
OpenCode Agent → MCP Server (port 8002) → OLT Devices (telnet)
                         ↓
                  SQLite Database
                  (commands + inventory)
```

## Files

```
olt/
├── server.py          # MCP server (FastMCP)
├── src/
│   ├── telnet.py      # Telnet driver
│   ├── database.py    # SQLite layer
│   └── config.py      # Config
├── storage/
│   ├── buttons.yaml   # Button mappings
│   └── olt.db         # SQLite database
└── install.sh         # Systemd + UV installer
```
