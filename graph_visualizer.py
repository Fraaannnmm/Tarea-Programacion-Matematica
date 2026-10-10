from __future__ import annotations

from pathlib import Path
from unicodedata import normalize

from transport_problem import Matrix, TransportationProblem

def save_all_graphs(
    problem: TransportationProblem,
    solutions: dict[str, Matrix],
    output_directory: str = "output",
) -> list[Path]:
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError as error:
        raise RuntimeError(
            "La visualización requiere las dependencias de requirements.txt."
        ) from error

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for method_name, allocation in solutions.items():
        graph = nx.DiGraph()
        origin_nodes = [f"O{i}" for i in range(len(problem.origins))]
        destination_nodes = [f"D{j + 1}" for j in range(len(problem.destinations))]
        graph.add_nodes_from(origin_nodes, bipartite=0)
        graph.add_nodes_from(destination_nodes, bipartite=1)
        for i, origin in enumerate(problem.origins):
            graph.nodes[origin_nodes[i]]["label"] = origin
        for j, destination in enumerate(problem.destinations):
            graph.nodes[destination_nodes[j]]["label"] = destination
        for i, origin_node in enumerate(origin_nodes):
            for j, destination_node in enumerate(destination_nodes):
                quantity = allocation[i][j]
                if quantity > 0:
                    graph.add_edge(
                        origin_node,
                        destination_node,
                        quantity=quantity,
                        cost=problem.costs[i][j],
                    )

        positions = {
            **{node: (0, -index) for index, node in enumerate(origin_nodes)},
            **{node: (1, -index) for index, node in enumerate(destination_nodes)},
        }
        figure, axis = plt.subplots(figsize=(12, 7))
        nx.draw_networkx_nodes(graph, positions, nodelist=origin_nodes, node_color="#9ecae1", node_size=2400, ax=axis)
        nx.draw_networkx_nodes(graph, positions, nodelist=destination_nodes, node_color="#a1d99b", node_size=2400, ax=axis)
        nx.draw_networkx_edges(graph, positions, arrows=True, arrowstyle="-|>", arrowsize=18, width=1.8, ax=axis)
        labels = {node: graph.nodes[node]["label"] for node in graph.nodes}
        nx.draw_networkx_labels(graph, positions, labels=labels, font_size=9, ax=axis)
        edge_labels = {
            (origin, destination): f"{data['quantity']:.0f}"
            for origin, destination, data in graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, label_pos=0.5, ax=axis)
        axis.set_title(f"Red de transporte - {method_name}")
        axis.axis("off")
        output_path = directory / f"{_safe_filename(method_name)}.png"
        figure.savefig(output_path, dpi=180, bbox_inches="tight")
        plt.close(figure)
        generated.append(output_path)
    return generated

def _safe_filename(value: str) -> str:
    ascii_value = normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return ascii_value.lower().replace(" ", "_")
