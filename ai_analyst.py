from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from transport_problem import Matrix, TransportationProblem

class AIAnalyst:
    def __init__(self, api_key: str | None = None, timeout: int = 30) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.timeout = timeout

    def build_prompt(
        self,
        problem: TransportationProblem,
        costs: dict[str, float],
        best_method: str,
        best_allocation: Matrix,
    ) -> str:
        return f"""Actúa como Consultor Logístico para Rutas y Suministros C.A.
Analiza los resultados del problema de transporte balanceado.

Costos totales por método:
{json.dumps(costs, ensure_ascii=False, indent=2)}

El mejor método fue: {best_method}
Matriz de asignación del mejor método:
{json.dumps(best_allocation, ensure_ascii=False)}

Orígenes: {problem.origins}
Destinos: {problem.destinations}
Oferta: {problem.supply}
Demanda: {problem.demand}

Devuelve una conclusión ejecutiva breve, de máximo dos párrafos. Explica
matemáticamente por qué el método ganador superó a los demás y valida si la
distribución final tiene sentido para el negocio. No inventes datos.
"""

    def analyze(
        self,
        problem: TransportationProblem,
        costs: dict[str, float],
        best_method: str,
        best_allocation: Matrix,
    ) -> str:
        if not self.api_key:
            return (
                "Análisis de IA no ejecutado: configure la variable de entorno "
                "GEMINI_API_KEY para habilitar la consulta REST."
            )
        prompt = self.build_prompt(problem, costs, best_method, best_allocation)
        payload = json.dumps(
            {"contents": [{"parts": [{"text": prompt}]}]}
        ).encode("utf-8")
        request = Request(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.0-flash:generateContent",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except (HTTPError, URLError, TimeoutError) as error:
            return f"No fue posible obtener el análisis de IA: {error}"
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as error:
            return f"La API devolvió una respuesta inesperada: {error}"
