"""
gephi_export.py — GraphRAG AI Travel Planner: GraphML Exporter for Gephi
=========================================================================
Connects to the Neo4j graph database, exports the full knowledge graph as
a GraphML file (`travel_graph.graphml`), which can be loaded directly into
Gephi for macro-level network analysis, community detection, and visualization.

The export uses the NetworkX library to build a Python graph object from
Neo4j data, then serializes it as standards-compliant GraphML.

Features:
  - Exports all nodes with their label, name, and properties as GraphML attributes
  - Exports all directed relationships with type as edge attribute
  - Assigns numeric IDs for full Gephi compatibility
  - Handles multi-label Neo4j nodes gracefully

Usage:
  python gephi_export.py
  python gephi_export.py --output my_custom_export.graphml
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import networkx as nx
from neo4j import GraphDatabase, Driver

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("gephi_export")

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "TravelGraph2026!")

OUTPUT_FILE = Path("travel_graph.graphml")


# ---------------------------------------------------------------------------
# Cypher queries
# ---------------------------------------------------------------------------

# Export all nodes (excluding internal Neo4j __Entity__ labels for cleanliness)
NODE_QUERY = """
MATCH (n)
WHERE NOT '__Entity__' IN labels(n)
  AND NOT 'Document' IN labels(n)
RETURN
  id(n)          AS neo4j_id,
  labels(n)      AS labels,
  properties(n)  AS props
ORDER BY id(n)
"""

# Export all relationships between those nodes
RELATIONSHIP_QUERY = """
MATCH (source)-[r]->(target)
WHERE NOT '__Entity__' IN labels(source)
  AND NOT '__Entity__' IN labels(target)
  AND NOT 'Document' IN labels(source)
  AND NOT 'Document' IN labels(target)
RETURN
  id(source)     AS source_neo4j_id,
  id(target)     AS target_neo4j_id,
  type(r)        AS rel_type,
  properties(r)  AS props,
  id(r)          AS rel_id
ORDER BY id(r)
"""


# ---------------------------------------------------------------------------
# Helper: flatten Neo4j properties to GraphML-compatible strings
# ---------------------------------------------------------------------------

def _flatten_props(props: Dict[str, Any]) -> Dict[str, str]:
    """Convert all property values to strings for GraphML compatibility."""
    flat: Dict[str, str] = {}
    for key, val in props.items():
        if val is None:
            continue
        if isinstance(val, list):
            flat[key] = ", ".join(str(v) for v in val)
        elif isinstance(val, bool):
            flat[key] = str(val).lower()
        else:
            flat[key] = str(val)
    return flat


# ---------------------------------------------------------------------------
# Core export function
# ---------------------------------------------------------------------------

def export_to_graphml(driver: Driver, output_path: Path) -> None:
    log.info("Building NetworkX DiGraph from Neo4j …")
    G = nx.DiGraph()
    G.graph["name"] = "GraphRAG AI Travel Planner Knowledge Graph"
    G.graph["description"] = (
        "Knowledge graph of Tuscany travel entities: Locations, Accommodations, "
        "Activities, Wines, and Cuisines with their semantic relationships."
    )

    # ── 1. Load nodes ──────────────────────────────────────────────────────
    node_count = 0
    with driver.session() as session:
        result = session.run(NODE_QUERY)
        for record in result:
            neo4j_id: int = record["neo4j_id"]
            labels: List[str] = record["labels"] or ["Unknown"]
            props: Dict[str, Any] = record["props"] or {}

            # Pick primary label (exclude __Entity__, _Chunk, etc.)
            primary_labels = [l for l in labels if not l.startswith("_")]
            primary_label = primary_labels[0] if primary_labels else "Node"

            node_name = props.get("name") or props.get("id") or f"node_{neo4j_id}"

            # Build node attribute dict
            node_attrs: Dict[str, str] = {
                "label": primary_label,
                "name": str(node_name),
                "neo4j_id": str(neo4j_id),
                "all_labels": "|".join(labels),
            }
            node_attrs.update(_flatten_props(props))

            G.add_node(str(neo4j_id), **node_attrs)
            node_count += 1

    log.info("  Loaded %d nodes", node_count)

    # ── 2. Load relationships ──────────────────────────────────────────────
    edge_count = 0
    with driver.session() as session:
        result = session.run(RELATIONSHIP_QUERY)
        for record in result:
            source_id = str(record["source_neo4j_id"])
            target_id = str(record["target_neo4j_id"])
            rel_type: str = record["rel_type"]
            rel_props: Dict[str, Any] = record["props"] or {}
            rel_id = record["rel_id"]

            # Skip if source or target node wasn't exported (e.g. Document nodes)
            if source_id not in G.nodes or target_id not in G.nodes:
                continue

            edge_attrs: Dict[str, str] = {
                "label": rel_type,
                "relationship_type": rel_type,
                "neo4j_rel_id": str(rel_id),
            }
            edge_attrs.update(_flatten_props(rel_props))

            G.add_edge(source_id, target_id, **edge_attrs)
            edge_count += 1

    log.info("  Loaded %d relationships", edge_count)

    # ── 3. Graph statistics ────────────────────────────────────────────────
    log.info("Graph statistics:")
    log.info("  Nodes          : %d", G.number_of_nodes())
    log.info("  Edges          : %d", G.number_of_edges())
    log.info("  Is connected   : %s", nx.is_weakly_connected(G) if G.number_of_nodes() > 0 else "N/A")

    if G.number_of_nodes() > 0:
        # Degree centrality
        centrality = nx.degree_centrality(G)
        top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        log.info("  Top 5 nodes by degree centrality:")
        for node_id, score in top_nodes:
            name = G.nodes[node_id].get("name", node_id)
            label = G.nodes[node_id].get("label", "?")
            log.info("    [%s] %s — %.4f", label, name, score)

    # ── 4. Write GraphML ───────────────────────────────────────────────────
    log.info("Writing GraphML to %s …", output_path)
    nx.write_graphml(G, str(output_path), encoding="utf-8", prettyprint=True)
    file_size_kb = output_path.stat().st_size / 1024
    log.info("GraphML export complete ✓ (%.1f KB)", file_size_kb)


# ---------------------------------------------------------------------------
# Gephi usage instructions
# ---------------------------------------------------------------------------

def print_gephi_instructions(output_path: Path) -> None:
    log.info("─" * 60)
    log.info("GEPHI IMPORT INSTRUCTIONS")
    log.info("─" * 60)
    log.info("1. Open Gephi (https://gephi.org)")
    log.info("2. File → Open → select: %s", output_path.resolve())
    log.info("3. In the 'Import Report': choose 'Directed Graph'")
    log.info("4. Go to 'Data Laboratory' tab to inspect node/edge attributes")
    log.info("5. Switch to 'Overview' tab for graph visualization")
    log.info("6. Recommended layout: Force Atlas 2 or Yifan Hu Proportional")
    log.info("7. Color nodes by 'label' attribute to distinguish entity types")
    log.info("8. Resize nodes by 'Degree' for hub identification")
    log.info("─" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(output_path: Path = OUTPUT_FILE) -> None:
    log.info("═" * 60)
    log.info("GraphRAG AI Travel Planner — Gephi GraphML Exporter")
    log.info("═" * 60)

    log.info("Connecting to Neo4j at %s …", NEO4J_URI)
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        )
        driver.verify_connectivity()
        log.info("Neo4j connection verified ✓")
    except Exception as exc:
        log.error("Failed to connect to Neo4j: %s", exc)
        log.error("Ensure Neo4j is running: docker-compose up -d")
        sys.exit(1)

    try:
        export_to_graphml(driver, output_path)
        print_gephi_instructions(output_path)
    finally:
        driver.close()

    log.info("═" * 60)
    log.info("Gephi export pipeline complete ✓")
    log.info("Output: %s", output_path.resolve())
    log.info("═" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Neo4j travel knowledge graph to GraphML for Gephi"
    )
    parser.add_argument(
        "--output", type=Path, default=OUTPUT_FILE,
        help="Output GraphML file path (default: travel_graph.graphml)"
    )
    args = parser.parse_args()
    main(args.output)
