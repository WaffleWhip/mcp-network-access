# OLT Manager MCP

Multi-vendor OLT terminal interaction via persistent, reactive Telnet sessions. Designed for high-speed AI agent autonomy and human-like interaction.

## Quick Install

Run this one-line command on your server:

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/olt/install.sh | bash
```

## Core Tools

| Tool | Mode | Description |
|------|------|-------------|
| `list` | View | Browse OLT inventory and retrieve credentials. |
| `telnet` | View | Initialize session and observe terminal state with dynamic length. |
| `telnet_send` | Action | Send commands or buttons (Batching supported). |
| `command` | Knowledge | Save and reuse discovered post-login command sequences. |

## Usage Examples

### 1. Discovery & Login
```bash
# Browse OLTs
list() 

# Get credentials for specific OLT
list(host="10.x.x.x", detail=True)

# Open session (default view 20 lines)
telnet(host="10.x.x.x")

# High-speed Batch Login
telnet_send(host="10.x.x.x", type="command", value="admin, password")
```

### 2. Operations & Navigation
```bash
# Send command and see 50 lines of output
telnet(host="10.x.x.x", length=50)
telnet_send(host="10.x.x.x", type="command", value="show card")

# Handle pagination (--More--)
telnet_send(host="10.x.x.x", type="button", value="space")

# Interactive Help
telnet_send(host="10.x.x.x", type="command", value="?")
```

### 3. Knowledge Management (Automation Paths)
Save working post-login sequences including complex navigation and button presses.

```bash
# Save complex path: Enter config -> Run Command -> Confirm -> Page Down -> Exit
command(
    action="save", 
    host="10.x.x.x", 
    syntax="show full config", 
    path="configure terminal, show running-config, [ENTER], [SPACE], [SPACE], exit", 
    description="Full config dump with pagination handling"
)

# List saved shortcuts
command(action="list", host="10.x.x.x")
```

## Features

- **Reactive Driver:** No fixed wait times; reacts instantly to OLT prompt events.
- **Human-Like Output:** Pure raw terminal text normalization (renders correctly in CLI).
- **Auto-Connect:** `telnet_send` automatically restores dead sessions.
- **Silent Auth:** Credentials sent via batch do not trigger "New Command" notes.
- **SQLite WAL Mode:** Optimized for concurrent access by multiple agents.

---
*Note: This system relies on AI agents to interpret terminal states from raw text output.*
