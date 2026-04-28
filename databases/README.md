# Databases MCP

Central inventory and knowledge base for network operations.

## Tools

- `db_olt_list`: List all registered OLTs.
- `db_olt_save`: Add or update OLT credentials.
- `db_olt_delete`: Remove an OLT.
- `db_olt_cmds_list`: Search CLI command syntax by Brand/Model.
- `db_skills_list`: List available SOP categories.
- `db_skills_read`: Read full SOP content.

## Setup

```bash
cd databases
bash install/build.sh
bash install/systemd.sh
```
