from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

Matrix = list[list[float]]

@dataclass(frozen=True)
class TransportationProblem:
    origins: list[str]
    destinations: list[str]
    costs: Matrix
    supply: list[float]
    demand: list[float]

    def __post_init__(self) -> None:
        if not self.origins or not self.destinations:
            raise ValueError("Debe existir al menos un origen y un destino.")
        if len(self.costs) != len(self.origins):
            raise ValueError("La cantidad de filas de costos no coincide con los orígenes.")
        if any(len(row) != len(self.destinations) for row in self.costs):
            raise ValueError("La matriz de costos no tiene dimensiones consistentes.")
        if len(self.supply) != len(self.origins) or len(self.demand) != len(self.destinations):
            raise ValueError("Oferta y demanda no coinciden con las dimensiones del problema.")
        if any(value < 0 for row in self.costs for value in row):
            raise ValueError("Los costos no pueden ser negativos.")
        if any(value < 0 for value in (*self.supply, *self.demand)):
            raise ValueError("La oferta y la demanda no pueden ser negativas.")
        if sum(self.supply) != sum(self.demand):
            raise ValueError("El problema debe estar balanceado: oferta total = demanda total.")

    def solve_northwest_corner(self) -> Matrix:
        return self._solve_by_northwest_corner()

    def solve_least_cost(self) -> Matrix:
        return self._solve_by_least_cost()

    def solve_vogel(self) -> Matrix:
        return self._solve_by_vogel()

    def total_cost(self, allocation: Matrix) -> float:
        self._validate_allocation(allocation)
        return sum(
            allocation[i][j] * self.costs[i][j]
            for i in range(len(self.origins))
            for j in range(len(self.destinations))
        )

    def _new_allocation(self) -> Matrix:
        return [[0.0 for _ in self.destinations] for _ in self.origins]

    def _solve_by_northwest_corner(self) -> Matrix:
        allocation = self._new_allocation()
        supply = self.supply.copy()
        demand = self.demand.copy()
        row, column = 0, 0
        epsilon = 1e-9

        while row < len(supply) and column < len(demand):
            quantity = min(supply[row], demand[column])
            allocation[row][column] = quantity
            supply[row] -= quantity
            demand[column] -= quantity
            if abs(supply[row]) < epsilon:
                supply[row] = 0
                row += 1
            if abs(demand[column]) < epsilon:
                demand[column] = 0
                column += 1
        return allocation

    def _solve_by_least_cost(self) -> Matrix:
        allocation = self._new_allocation()
        supply = self.supply.copy()
        demand = self.demand.copy()
        available = {
            (i, j)
            for i in range(len(self.origins))
            for j in range(len(self.destinations))
        }

        while available:
            i, j = min(
                available,
                key=lambda position: (
                    self.costs[position[0]][position[1]],
                    position[0],
                    position[1],
                ),
            )
            quantity = min(supply[i], demand[j])
            allocation[i][j] = quantity
            supply[i] -= quantity
            demand[j] -= quantity
            if supply[i] == 0:
                available = {(r, c) for r, c in available if r != i}
            if demand[j] == 0:
                available = {(r, c) for r, c in available if c != j}
        return allocation

    def _solve_by_vogel(self) -> Matrix:
        allocation = self._new_allocation()
        supply = self.supply.copy()
        demand = self.demand.copy()
        active_rows = set(range(len(self.origins)))
        active_columns = set(range(len(self.destinations)))

        while active_rows and active_columns:
            row_penalties = {
                i: self._penalty(
                    self.costs[i][j] for j in sorted(active_columns)
                )
                for i in active_rows
            }
            column_penalties = {
                j: self._penalty(
                    self.costs[i][j] for i in sorted(active_rows)
                )
                for j in active_columns
            }
            best_row = max(row_penalties.items(), key=lambda item: (item[1], -item[0]))
            best_column = max(
                column_penalties.items(), key=lambda item: (item[1], -item[0])
            )

            if best_row[1] > best_column[1]:
                row = best_row[0]
                column = min(
                    active_columns,
                    key=lambda j: (self.costs[row][j], j),
                )
            elif best_column[1] > best_row[1]:
                column = best_column[0]
                row = min(
                    active_rows,
                    key=lambda i: (self.costs[i][column], i),
                )
            else:
                cheapest_row = min(
                    (self.costs[i][j], i, j)
                    for i in active_rows
                    for j in active_columns
                )
                cheapest_column = min(
                    (self.costs[i][j], j, i)
                    for j in active_columns
                    for i in active_rows
                )
                if cheapest_row[:2] <= (cheapest_column[0], cheapest_column[2]):
                    row, column = cheapest_row[1], cheapest_row[2]
                else:
                    column, row = cheapest_column[1], cheapest_column[2]

            quantity = min(supply[row], demand[column])
            allocation[row][column] = quantity
            supply[row] -= quantity
            demand[column] -= quantity
            if supply[row] == 0:
                active_rows.remove(row)
            if demand[column] == 0:
                active_columns.remove(column)
        return allocation

    @staticmethod
    def _penalty(costs: Iterable[float]) -> float:
        ordered = sorted(costs)
        return ordered[1] - ordered[0] if len(ordered) > 1 else ordered[0]

    def _validate_allocation(self, allocation: Matrix) -> None:
        if len(allocation) != len(self.origins) or any(
            len(row) != len(self.destinations) for row in allocation
        ):
            raise ValueError("La matriz de asignación tiene dimensiones inválidas.")
        if any(value < 0 for row in allocation for value in row):
            raise ValueError("Una asignación no puede ser negativa.")
        for i, expected in enumerate(self.supply):
            if sum(allocation[i]) != expected:
                raise ValueError(f"La fila {i} no satisface la oferta.")
        for j, expected in enumerate(self.demand):
            if sum(allocation[i][j] for i in range(len(self.origins))) != expected:
                raise ValueError(f"La columna {j} no satisface la demanda.")
