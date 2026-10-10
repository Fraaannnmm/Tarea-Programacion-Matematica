# Tarea de Programación Matemática: Problema de Transporte

Implementación orientada a objetos para `Rutas y Suministros C.A.`. Incluye:

- Esquina Noroeste, Costo Mínimo y Aproximación de Vogel, sin librerías de optimización.
- Visualización de las rutas usadas con NetworkX y Matplotlib.
- Cliente REST opcional para Gemini mediante `GEMINI_API_KEY`.
- Datos del enunciado como prueba por defecto.

## Ejecución

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Para validar los algoritmos sin instalar las librerías gráficas:

```bash
python main.py --sin-graficos
```

Las imágenes se guardan en `output/`. Las cantidades de las aristas representan
las unidades transportadas.

## Activar el análisis de IA

1. Crear una API key de Gemini en Google AI Studio.
2. Configurarla solo en la sesión local, sin escribirla en el código:

```bash
export GEMINI_API_KEY="TU_API_KEY"
python main.py
```

Si la variable no existe, el sistema informa que el análisis no fue ejecutado y
el resto de los módulos continúa funcionando.
