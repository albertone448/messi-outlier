<a id="english"></a>

**[English](#english) | [Español](#español)**

---

# Messi: Outlier

Statistical analysis of how singular Lionel Messi's profile is across World Cups, measured against the full population of historical World Cup players rather than a handful of hand-picked comparisons.

## Status

Early stage. The repository structure and methodology are being set up. Before building any pipeline, the project validated whether a source like SofaScore can provide detailed match-level statistics for older World Cups (starting with a 1986 Maradona match as a test case), and passed that check. See `METHODOLOGY.md` for the current state of every methodological decision made so far, and `MASTER_PLAN.md` for the step-by-step task list.

## The question

Does any historical World Cup player come close to combining, at the same time, the metrics that separate elite finishers, dribblers, chance creators and play organizers, or does Messi's profile stand out for appearing among the elite of several distinct functional roles at once?

This is not an attempt to show Messi is the best in every category. Being extraordinary in one dimension is common among great players. The question is whether being simultaneously excellent across several different functional dimensions is rare, and if so, how rare, against what population, and under what criteria.

## Why this project

This is a portfolio Data Analytics project, built to be reproducible and defensible in a technical interview, not a highlight reel of Messi stats. The full reasoning behind every decision, including the ones that didn't go as expected, lives in `METHODOLOGY.md`. `MASTER_PLAN.md` (Spanish only, working document) tracks the sequential task list.

## Approach (summary)

- Players are compared by **functional role** (finisher, dribbler, chance creator, play organizer), not by nominal position, since a player's position often doesn't match what they actually do on the pitch.
- Metrics are normalized **per 90 minutes**, with a minimum-minutes threshold still to be defined and justified, so that career length doesn't get confused with performance.
- Percentiles are calculated against the **full relevant player population**, not only against a few reference players. Cristiano Ronaldo, Neymar, Mbappé, Ronaldinho and Maradona are used as reference points to help interpret the results, not as the whole comparison set.
- The hypothesis is allowed to fail. If a dimension of Messi's profile turns out to be unremarkable, that gets documented, not dropped.

## Data sources (candidates, under evaluation)

- **SofaScore**: primary candidate for detailed match stats (passes, duels, touches, dribbles). Accessed through its internal API, since there's no official public API.
- **FBref**: complementary source for advanced modern metrics (xG, xA, progressive actions), with likely weaker historical coverage.
- **Kaggle**: complementary datasets for base structures, checked for provenance before use.

Nothing here is final. Section 15 of the project's working methodology explains what each source needs to be checked for before being trusted.

## Stack

Python, pandas, Jupyter, Matplotlib for exploration, Tableau Public for the final dashboard.

## Repository structure

```
messi-outlier/
├── data/
│   ├── raw/          # Original extracted data, never edited by hand
│   └── processed/     # Cleaned and merged datasets
├── notebooks/          # Analysis notebooks (not yet created, pending phase design)
├── src/                # Reusable functions shared across notebooks
├── scripts/            # Standalone one-off scripts (extraction, validation)
├── reports/figures/     # Exported visualizations
├── METHODOLOGY.md       # Decisions, tools, techniques (why)
├── MASTER_PLAN.md        # Step-by-step task list, Spanish only (what, in what order)
└── README.md
```

## Reproducing this

```bash
pip install -r requirements.txt
python scripts/validate_maradona_1986.py
```

Right now that script is the only thing that runs. It checks, against the real SofaScore API, whether the 1986 World Cup has the level of detail this project needs.

---

<a id="español"></a>

**[English](#english) | [Español](#español)**

---

# Messi: Una Anomalía

Análisis estadístico de qué tan singular es el perfil de Lionel Messi en Mundiales, medido contra toda la población histórica de jugadores de Mundiales y no contra un puñado de comparaciones elegidas a mano.

## Estado actual

Etapa inicial. Se está armando la estructura del repositorio y la metodología. Antes de construir cualquier pipeline, el proyecto validó si una fuente como SofaScore puede ofrecer estadísticas detalladas a nivel de partido para Mundiales antiguos (empezando con un partido de Maradona de 1986 como caso de prueba), y pasó esa validación. Cada decisión metodológica tomada hasta ahora está en `METHODOLOGY.md`, y el paso a paso secuencial en `MASTER_PLAN.md`.

## La pregunta

¿Existe algún jugador histórico de Mundiales que se acerque a combinar, simultáneamente, las métricas que distinguen a finalizadores, desequilibrantes, creadores de juego y organizadores de élite, o el perfil de Messi resalta precisamente por aparecer entre la élite de varios roles funcionales distintos al mismo tiempo?

Esto no busca demostrar que Messi es el mejor en cada categoría. Ser extraordinario en una sola dimensión es común entre los grandes jugadores. La pregunta es si ser excelente simultáneamente en varias dimensiones funcionales distintas es poco común, y si lo es, qué tan poco común, contra qué población y bajo qué criterios.

## Por qué este proyecto

Este es un proyecto de portafolio de Data Analytics, construido para ser reproducible y defendible en una entrevista técnica, no una recopilación de estadísticas de Messi. El razonamiento completo detrás de cada decisión, incluyendo las que no salieron como se esperaba, vive en `METHODOLOGY.md`. `MASTER_PLAN.md` (solo en español, documento de trabajo) lleva el registro secuencial de tareas.

## Enfoque (resumen)

- Los jugadores se comparan por **rol funcional** (finalizador, desequilibrante, creador de juego, organizador), no por posición nominal, porque la posición de un jugador muchas veces no coincide con lo que realmente hace en la cancha.
- Las métricas se normalizan **por 90 minutos**, con un umbral mínimo de minutos todavía por definir y justificar, para que la duración de una carrera no se confunda con rendimiento.
- Los percentiles se calculan contra **toda la población relevante de jugadores**, no solo contra unos pocos jugadores de referencia. Cristiano Ronaldo, Neymar, Mbappé, Ronaldinho y Maradona se usan como referencia para interpretar resultados, no como todo el conjunto de comparación.
- La hipótesis tiene permiso de fallar. Si alguna dimensión del perfil de Messi resulta poco destacable, eso se documenta, no se descarta.

## Fuentes de datos (candidatas, en evaluación)

- **SofaScore**: candidata principal para estadísticas detalladas de partido (pases, duelos, toques, regates). Se accede a través de su API interna, ya que no existe una API pública oficial.
- **FBref**: fuente complementaria para métricas avanzadas modernas (xG, xA, acciones progresivas), probablemente con cobertura histórica más débil.
- **Kaggle**: datasets complementarios para estructuras base, revisados por procedencia antes de usarlos.

Nada de esto es definitivo. La sección 15 de la metodología de trabajo del proyecto explica qué hay que verificar de cada fuente antes de confiar en ella.

## Stack

Python, pandas, Jupyter, Matplotlib para exploración, Tableau Public para el dashboard final.

## Estructura del repositorio

```
messi-outlier/
├── data/
│   ├── raw/           # Datos originales extraídos, nunca editados a mano
│   └── processed/     # Datasets limpios y unificados
├── notebooks/          # Notebooks de análisis (aún no creados, pendiente diseño de fases)
├── src/                # Funciones reutilizables compartidas entre notebooks
├── scripts/            # Scripts puntuales (extracción, validación)
├── reports/figures/     # Visualizaciones exportadas
├── METHODOLOGY.md       # Decisiones, herramientas, técnicas (el porqué)
├── MASTER_PLAN.md        # Lista de tareas paso a paso, solo en español (el qué, en qué orden)
└── README.md
```

## Cómo reproducir esto

```bash
pip install -r requirements.txt
python scripts/validate_maradona_1986.py
```

Por ahora ese script es lo único que corre. Comprueba, contra la API real de SofaScore, si el Mundial de 1986 tiene el nivel de detalle que este proyecto necesita.