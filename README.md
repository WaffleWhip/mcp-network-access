# MCP for OLT and ONT Management

Collection of Model Context Protocol (MCP) servers for telecommunication network management.

## Architecture

- [8001: GenieACS MCP](./genieacs/README.md) - TR-069 interaction for ONT management.
- [8002: OLT MCP (Telnet)](./olt/README.md) - Direct CLI interaction with OLTs.

### Archive
- [8003: Databases MCP (Archived)](./databases/README.md) - Centralized inventory and SOP knowledge base.

## One-Line Installation

### GenieACS MCP (Port 8001)
```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/genieacs/install.sh | bash
```

### OLT MCP (Port 8002)
```bash
curl -sSL https://raw.githubusercontent.com/WaffleWhip/mcp-network-access/main/olt/install.sh | bash
```

---
Manual deployment scripts are available in each subdirectory.
