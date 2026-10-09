import os
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def generate_mindmap(summary_points):
    if not summary_points:
        raise ValueError("No summary points available.")

    graph = nx.Graph()
    root = "MindMapBot\nSummary"
    graph.add_node(root)

    for i, point in enumerate(summary_points[:15], 1):
        label = textwrap.fill(str(point), width=32)
        node = "P{}".format(i)
        graph.add_node(node, label=label)
        graph.add_edge(root, node)

    pos = nx.spring_layout(graph, seed=42, k=1.5)

    fig, ax = plt.subplots(figsize=(14, 9))
    nx.draw_networkx_nodes(
        graph, pos, ax=ax, node_size=2600, alpha=0.9
    )
    nx.draw_networkx_edges(
        graph, pos, ax=ax, width=1.5, alpha=0.6
    )

    labels = {root: root}
    labels.update({
        node: graph.nodes[node].get("label", node)
        for node in graph.nodes
        if node != root
    })

    nx.draw_networkx_labels(
        graph, pos, labels=labels, ax=ax,
        font_size=8, font_weight="bold"
    )

    ax.set_axis_off()
    fig.tight_layout()

    path = os.path.join(TEMP_DIR, "mindmap.png")
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path
