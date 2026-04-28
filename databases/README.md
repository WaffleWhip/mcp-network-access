# Databases MCP

Central inventory and knowledge base for network operations.

## Tools

- `db_olt_list()`: List all registered OLTs with credentials.
- `db_olt_save(name, host, user, password, vendor, model)`: Add or update OLT credentials.
- `db_olt_delete(name)`: Remove an OLT from inventory.
- `db_olt_cmds_list(vendor, model)`: Search CLI command syntax by OLT brand/model.
- `db_ont_list()`: List available ONT historical snapshot batches.
- `db_ont_summary(batch)`: Get high-level stats for ONT batch (total ONTs, clusters, impacted count).
- `db_ont_clusters(batch, min_size)`: Identify interference clusters in ONT batch.
- `db_ont_details(batch, cluster_id)`: Get interference matrix and member list for a cluster.
- `db_ont_status(batch, sn)`: Get historical radio status and neighbors for specific ONT.
- `db_skills_list()`: List available SOP categories.
- `db_skills_read(category)`: Read full SOP content.

## Setup

```bash
cd databases
bash install/build.sh     # Install dependencies
bash install/start.sh     # Start MCP server (or manual test)
bash install/systemd.sh   # Install as systemd service
```
