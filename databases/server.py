"""Network Master Database - Flat Architecture"""
from fastmcp import FastMCP
from typing import Optional, Any

# Import modular logic
from src.olt import list_olts, save_olt, delete_olt, list_cmds, save_cmd
from src.ont import list_batches, get_summary, get_clusters, get_details, get_status
from src.skills import list_skills, read_skill

mcp = FastMCP("Network-Master-Database")

# --- OLT SECTION ---
@mcp.tool()
def db_olt_list() -> Any:
    """List all registered OLTs in the centralized infrastructure database."""
    return list_olts()

@mcp.tool()
def db_olt_save(name: str, host: str, user: str, password: str, vendor: str, model: Optional[str] = None) -> Any:
    """Create or update OLT credentials in the database."""
    return save_olt(name, host, user, password, vendor, model)

@mcp.tool()
def db_olt_delete(name: str) -> Any:
    """Remove an OLT from the infrastructure database."""
    return delete_olt(name)

@mcp.tool()
def db_olt_cmds_list(vendor: Optional[str] = None, model: Optional[str] = None) -> Any:
    """Search for CLI commands in the knowledge base using hierarchical filtering (Brand > Model)."""
    return list_cmds(vendor, model)

@mcp.tool()
def db_olt_cmds_save(vendor: str, model: str, command_syntax: str, execution_mode: str, description: str) -> Any:
    """Save a newly discovered CLI command to the knowledge base."""
    return save_cmd(vendor, model, command_syntax, execution_mode, description)

# --- ONT SECTION ---
@mcp.tool()
def db_ont_list() -> Any:
    """List all available ONT historical snapshot batches."""
    return list_batches()

@mcp.tool()
def db_ont_summary(batch: str) -> Any:
    """Get high-level stats for a specific ONT batch."""
    return get_summary(batch)

@mcp.tool()
def db_ont_clusters(batch: str, min_size: int = 2) -> Any:
    """Identify interference clusters in a batch."""
    return get_clusters(batch, min_size)

@mcp.tool()
def db_ont_details(batch: str, cluster_id: int) -> Any:
    """Get the interference matrix and member list for a specific cluster."""
    return get_details(batch, cluster_id)

@mcp.tool()
def db_ont_status(batch: str, sn: str) -> Any:
    """Get historical radio status and neighbors for one specific ONT."""
    return get_status(batch, sn)

# --- SKILLS SECTION ---
@mcp.tool()
def db_skills_list() -> Any:
    """List all available Standard Operating Procedure (SOP) categories."""
    return list_skills()

@mcp.tool()
def db_skills_read(category: str) -> Any:
    """Read the full content of an SOP category."""
    return read_skill(category)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8003)
