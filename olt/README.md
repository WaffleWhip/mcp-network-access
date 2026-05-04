# OLT MCP (Telnet)

Multi-vendor OLT terminal interaction via persistent Telnet sessions.

## Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/olt/install.sh | bash
```

## Core Tools

| Tool | Mode | Description |
|------|------|-------------|
| `inventory` | View/Edit | Manage OLT credentials and IPs. |
| `telnet` | View | Open session and observe terminal state. |
| `telnet_send` | Action | Send commands or buttons manually. |
| `command` | Knowledge | Knowledge base of operational hints and recipes. |

## Knowledge Base (Hints)

This system uses a **Knowledge-First** approach. Before executing a command, the agent checks for a "Hint" (a recipe of proven steps).

1. **Check Hint:** `command(action="list", host="10.x.x.x")`
2. **Execute Manually:** If a hint like `config, show version` exists, the agent must type those steps manually via `telnet_send`.
3. **Contribute:** If the agent discovers a new working sequence, it saves it as a Hint for others.

---
Note: This system relies on AI agents to interpret terminal states and execute steps manually.

[Back to main README](../README.md)
