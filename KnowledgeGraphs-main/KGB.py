import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pyvis.network import Network
import pandas as pd
import os

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

os.makedirs("output", exist_ok=True)

# ---------------------------------------------------------------------------
# Define entity and relationship data using pandas DataFrames
# ---------------------------------------------------------------------------

entities_data = pd.DataFrame([
    {"name": "Alice",     "type": "Person"},
    {"name": "Bob",       "type": "Person"},
    {"name": "OpenAI",    "type": "Company"},
    {"name": "Microsoft", "type": "Company"},
    {"name": "GitHub",    "type": "Company"},
])

relationships_data = pd.DataFrame([
    {"source": "Alice",     "target": "OpenAI",    "relationship": "works_at"},
    {"source": "Bob",       "target": "Microsoft", "relationship": "works_at"},
    {"source": "Alice",     "target": "Bob",       "relationship": "knows"},
    {"source": "Microsoft", "target": "GitHub",    "relationship": "acquired"},
])

# ---------------------------------------------------------------------------
# Build directed graph
# ---------------------------------------------------------------------------

kg = nx.DiGraph()

for _, row in entities_data.iterrows():
    kg.add_node(row["name"], type=row["type"])

for _, row in relationships_data.iterrows():
    kg.add_edge(row["source"], row["target"], relationship=row["relationship"])

# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

print("Knowledge Graph Information")
print("=" * 40)
print(f"Number of nodes : {kg.number_of_nodes()}")
print(f"Number of edges : {kg.number_of_edges()}")

print("\nNodes:")
for node, data in kg.nodes(data=True):
    print(f"  {node}: {data}")

print("\nRelationships:")
for source, target, data in kg.edges(data=True):
    print(f"  {source} --{data['relationship']}--> {target}")

print("\nDegree Centrality")
print("=" * 40)
centrality = nx.degree_centrality(kg)
for node, score in sorted(centrality.items(), key=lambda x: -x[1]):
    print(f"  {node}: {score:.2f}")

# ---------------------------------------------------------------------------
# Export GraphML
# ---------------------------------------------------------------------------

nx.write_graphml(kg, "output/graph.graphml")
print("\nGraph exported to output/graph.graphml")

# ---------------------------------------------------------------------------
# Static visualization (matplotlib)
# ---------------------------------------------------------------------------

TYPE_COLORS = {
    "Person":  "#4A90D9",
    "Company": "#E07B54",
}

node_colors = [
    TYPE_COLORS.get(kg.nodes[n].get("type", ""), "#AAAAAA")
    for n in kg.nodes()
]

plt.figure(figsize=(10, 7))
pos = nx.spring_layout(kg, seed=42)

nx.draw(
    kg,
    pos,
    with_labels=True,
    node_color=node_colors,
    node_size=3000,
    font_size=10,
    font_color="white",
    font_weight="bold",
    arrows=True,
    arrowsize=20,
)

edge_labels = {
    (u, v): d["relationship"]
    for u, v, d in kg.edges(data=True)
}

nx.draw_networkx_edge_labels(kg, pos, edge_labels=edge_labels, font_size=9)

legend_handles = [
    mpatches.Patch(color=color, label=label)
    for label, color in TYPE_COLORS.items()
]
plt.legend(handles=legend_handles, loc="upper left")

plt.title("Knowledge Graph Visualization")
plt.tight_layout()
plt.savefig("output/graph_visualization.png", dpi=150)
plt.close()
print("Visualization saved to output/graph_visualization.png")

# ---------------------------------------------------------------------------
# Interactive visualization (PyVis)
# ---------------------------------------------------------------------------

PYVIS_COLORS = {
    "Person":  "#4A90D9",
    "Company": "#E07B54",
}

# notebook=False writes a standalone HTML file instead of rendering inline
net = Network(
    height="750px",
    width="100%",
    directed=True,
    notebook=False,
)

for node, data in kg.nodes(data=True):
    node_type = data.get("type", "Unknown")
    net.add_node(
        node,
        label=node,
        title=f"Type: {node_type}",
        color=PYVIS_COLORS.get(node_type, "#AAAAAA"),
    )

for source, target, data in kg.edges(data=True):
    net.add_edge(
        source,
        target,
        title=data["relationship"],
        label=data["relationship"],
    )

net.write_html("output/interactive_graph.html")
print("Interactive graph saved to output/interactive_graph.html")

print("\nKnowledge Graph build completed successfully!")
