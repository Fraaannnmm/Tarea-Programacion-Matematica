from __future__ import annotations

import argparse
from pathlib import Path

from ai_analyst import AIAnalyst
from graph_visualizer import save_all_graphs
from transport_problem import TransportationProblem

DEFAULT_PROBLEM = TransportationProblem(
    origins=["Planta San Diego (O1)", "Planta Maracay (O2)", "Planta Barquisimeto (O3)"],
    destinations=["Caracas (D1)", "Maracaibo (D2)", "Puerto La Cruz (D3)", "San Cristóbal (D4)"],
    costs=[[15, 35, 40, 45], [10, 45, 30, 50], [25, 20, 55, 20]],
    supply=[300, 400, 500],
    demand=[250, 350, 400, 200],
)

def main() -> None:
    parser = argparse.ArgumentParser(description="Optimización de una red de transporte.")
    parser.add_argument(
        "--sin-graficos",
        action="store_true",
        help="No generar imágenes de la red.",
    )
    parser.add_argument(
        "--salida",
        default="output",
        help="Directorio para guardar las imágenes (por defecto: output).",
    )
    args = parser.parse_args()

    solutions = {
        "Esquina Noroeste": DEFAULT_PROBLEM.solve_northwest_corner(),
        "Costo Mínimo": DEFAULT_PROBLEM.solve_least_cost(),
        "Vogel": DEFAULT_PROBLEM.solve_vogel(),
    }
    costs = {
        method: DEFAULT_PROBLEM.total_cost(allocation)
        for method, allocation in solutions.items()
    }
    best_method = min(costs, key=costs.get)

    print("=== RESULTADOS DEL PROBLEMA DE TRANSPORTE ===")
    for method, allocation in solutions.items():
        print(f"\n{method}:")
        print_matrix(allocation)
        print(f"Costo total: ${costs[method]:,.2f}")
    print(f"\nMejor método: {best_method} (${costs[best_method]:,.2f})")

    if not args.sin_graficos:
        generated = save_all_graphs(DEFAULT_PROBLEM, solutions, args.salida)
        print("\nImágenes generadas:")
        for path in generated:
            print(f"- {Path(path).resolve()}")

    print("\n=== CONCLUSIÓN DEL AGENTE ANALISTA ===")
    print(AIAnalyst().analyze(DEFAULT_PROBLEM, costs, best_method, solutions[best_method]))

def print_matrix(matrix: list[list[float]]) -> None:
    for row in matrix:
        print("  " + " | ".join(f"{value:.0f}" for value in row))

if __name__ == "__main__":
    main()
