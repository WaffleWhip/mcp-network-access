"""Network Master Database - ONT Logic Only"""
from fastmcp import FastMCP, Context
from typing import Optional, Any

from src.ont import list_batches, get_summary, get_clusters, get_details, get_status
from src.skills import list_skills, read_skill

mcp = FastMCP("Network-Database")

@mcp.tool()
def db_ont_list(ctx: Context) -> Any:
    """List all available ONT historical snapshot batches.
    Example: db_ont_list()
    """
    return list_batches()

@mcp.tool()
def db_ont_summary(ctx: Context, batch: str) -> Any:
    """Get high-level stats for a specific ONT batch.
    Example: db_ont_summary(batch="batch_20260428")
    """
    return get_summary(batch)

@mcp.tool()
def db_ont_clusters(ctx: Context, batch: str, min_size: int = 2) -> Any:
    """Identify interference clusters in a batch.
    Example: db_ont_clusters(batch="batch_20260428", min_size=3)
    """
    return get_clusters(batch, min_size)

@mcp.tool()
def db_ont_details(ctx: Context, batch: str, cluster_id: int) -> Any:
    """Get the interference matrix and member list for a specific cluster.
    Example: db_ont_details(batch="batch_20260428", cluster_id=1)
    """
    return get_details(batch, cluster_id)

@mcp.tool()
def db_ont_status(ctx: Context, batch: str, sn: str) -> Any:
    """Get historical radio status and neighbors for one specific ONT.
    Example: db_ont_status(batch="batch_20260428", sn="ALCLB123456")
    """
    return get_status(batch, sn)

@mcp.tool()
def db_skills_list(ctx: Context) -> Any:
    """List all available SOP categories.
    Example: db_skills_list()
    """
    return list_skills()

@mcp.tool()
def db_skills_read(ctx: Context, category: str) -> Any:
    """Read the full content of an SOP category.
    Example: db_skills_read(category="olt-commands")
    """
    return read_skill(category)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8003)
