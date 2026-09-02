<a id="english"></a>

**[English](#english) | [Español](#español)**

---

# Messi: Outlier

Statistical analysis of how singular Lionel Messi's profile is across World Cups, measured against the full population of historical World Cup players rather than a handful of hand-picked comparisons.

## Status

**Complete.** Full data pipeline (8 notebooks, `00` through `07`), fully documented in `METHODOLOGY.md`, and a 3-part interactive dashboard published on Tableau Public (links below).

## The question

Does any historical World Cup player come close to combining, at the same time, the metrics that separate elite finishers, dribblers, chance creators and play organizers, or does Messi's profile stand out for appearing among the elite of several distinct functional roles at once?

Framing note: "outlier" can suggest absolute uniqueness, and that's not quite what the data shows. Messi shares the highest ceiling actually observed in the population (elite status in 3 of 4 roles) with 7 other players. What the data does show, and what holds up under every threshold and sample-size cut tested, is something more precise: across the full 1966-2026 World Cup population, no player's profile clearly exceeds or consistently matches his on the measure that matters most, average role percentile among players with a real career-length sample. That's a claim about the absence of a better-supported rival, not about mathematical uniqueness.

## Why this project

This is a portfolio Data Analytics project, built to be reproducible and defensible in a technical interview, not a highlight reel of Messi stats. The full reasoning behind every decision, including the ones that didn't go as expected, lives in `METHODOLOGY.md`. `MASTER_PLAN.md` (Spanish only, working document) tracks the sequential task list from start to finish.

## Approach (summary)

- Players are compared by **functional role** (finisher, dribbler, chance creator, play organizer), not by nominal position, since a player's position often doesn't match what they actually do on the pitch. 16 metrics, verified against the data provider's own glossary, were assigned across the four roles; metrics without solid historical coverage (like xG/xA, only available from 2022 on) were checked and left out.
- Metrics are normalized **per 90 minutes**, aggregated at player-career level (one row per player, summing every World Cup match from 1966 to 2026), with a **270-minute minimum** (three full matches), chosen by testing where small-sample noise in goals-per-90 actually stabilizes across the real population. Higher floors (900, 1500 minutes) are used throughout as a transparency check, not a replacement.
- "Elite" is defined by **percentile**, not a fixed top-N, tested at the 90th, 95th, and 99th percentiles rather than committing to one cutoff.
- Percentiles are calculated against the **full relevant player population** (5636 outfield players; 2488 meet the 270-minute threshold), not only against a few reference players. Reference and statistically-derived comparisons are always kept clearly labeled as one or the other, never blended.
- The hypothesis was allowed to fail, and did, in its strongest form: no player, including Messi, reaches elite status in all four roles at once at a genuine elite threshold.

## Results

**Phases 0-1, data validation and extraction.** Confirmed, against a 1986 Maradona match and the 2022 final, that SofaScore's internal API has comparable event-level detail across the entire 1966-2026 range. Full extraction: 900 matches, 5636 outfield players at career level.

**Phase 4, role correlations.** The three attacking roles (finisher, dribbler, chance creator) correlate moderately with each other (0.49-0.58). Play organizer is nearly independent of all three (0.02-0.30), confirming it as a genuinely distinct skill dimension. This led to a prediction, made before running any numbers: organizer would be Messi's relative weak point.

**Phase 5, the central finding.** No player in the population reaches elite status in all 4 roles at a genuine threshold (90th percentile or higher). The real ceiling, elite in 3 of 4 roles, is shared by 8 players; Messi is one of them, with by far the largest career sample (6 World Cups, 34 matches, 3054 minutes). Among players with a real career-length sample (900+ minutes), Messi has the highest average role percentile in the entire population. Maradona is a genuine, non-cherry-picked runner-up, with the gap explained almost entirely by play organizer, exactly as predicted in Phase 4. Cristiano Ronaldo, with a nearly identical career sample to Messi's, has the lowest average role score in the project's comparison sets, direct evidence the finding isn't simply a function of playing many World Cups.

**Phase 6, role specialists.** Building the reference set for the radar charts surfaced its own finding: the organizer-role leader at the base 270-minute threshold turned out to be driven by a single match of high-volume, low-threat passing (Spain's 2018 round-of-16 exit to Russia), not genuine organizing quality. A stricter 900-minute floor was applied specifically for choosing which players get shown as "leaders."

## Conclusion

No player's profile in the 1966-2026 World Cup population clearly exceeds or consistently matches Messi's across the four functional roles measured here. This isn't a claim of mathematical uniqueness, several other players share the observed ceiling, and Maradona is a real, well-supported runner-up. It's a claim about the absence of a better-supported rival, on the most robust measure this project could construct: average role percentile among players with a genuine career-length sample, tested across multiple percentile thresholds and multiple minimum-minutes floors, none of which changed the result. The one relative weakness found, play organizer, was predicted before the data was ever run, which strengthens the finding rather than undermining it.

The declared limitation stands: this measures roughly 6 months of accumulated football (Messi's six World Cups) against a much longer career, a deliberate scope choice explained in `METHODOLOGY.md`, not an oversight.

## Closing a chapter, while this project was closing too

On August 31, 2026, while this project was in the middle of being built, Lionel Messi officially announced his retirement from the Argentina national team, after playing his sixth World Cup. At 39 years old, in what turned out to be his last tournament, he scored 8 goals and gave 4 assists in 8 matches, taking Argentina all the way to the final. Those are numbers most footballers in history never reach even at their physical peak, and he produced them at the end of his career. With that, his World Cup story is closed for good: six tournaments between 2006 and 2026, 34 matches, 21 goals.

This wasn't planned. The project started as a Data Analytics portfolio exercise, and it ended up coinciding, without anyone intending it, with the real and final close of the World Cup career it analyzes. From here on, Messi's World Cup numbers won't change again. In that sense, this is a finished, complete record, not a snapshot of something still in motion.

Football, looked at closely like this, is more than a game. It made us root, unconditionally, for a country none of us were born in. For those of us who experienced it that way, World Cups won't feel the same without him on the pitch.

Thank you, Leo. And I will always carry December 18, 2022 in my heart, the day you fulfilled your childhood dream.

## Data sources

- **SofaScore**: the project's sole data source. Detailed match-level stats (passes, duels, touches, dribbles, shots) accessed through its internal API (no official public API exists), using the ScraperFC library. Validated first against a 1986 Maradona match and the 2022 final before committing to a full extraction; confirmed to provide comparable detail across the entire 1966-2026 range.
- FBref and Kaggle were considered as complementary sources early on but weren't ultimately needed; SofaScore's historical coverage covered everything the project's metrics required.

## Stack

Python, pandas, Jupyter, Matplotlib, ScraperFC (SofaScore extraction), Tableau Public for the final dashboard.

## Dashboards

- [Dashboard 1: are the four roles really distinct?](https://public.tableau.com/views/MessiOutlier/Dash1Loscuatrorolessonrealmentedistintos?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) — role correlation heatmap and an interactive scatter of the weakest pair (chance creator vs. play organizer).
- [Dashboard 2: the central finding](https://public.tableau.com/views/MessiOutlier/Dash2Elhallazgocentral?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) — average role score vs. career minutes (interactive minimum-minutes control), and the distribution of how many roles each player reaches at the elite threshold.
- [Dashboard 3: profiles](https://public.tableau.com/views/MessiOutlier/Dash3Perfiles?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) — Messi against Phase 6's reference set, against each role's individual top 5, and against an editorially-selected set of historical GOAT candidates.

## Repository structure

```
messi-outlier/
├── data/
│   ├── raw/                          # 900 raw match files + manifest, never edited by hand
│   └── processed/                    # population.csv, role_metrics.csv, role_scores.csv,
│                                      # role_specialists.csv, role_correlation_matrix.csv,
│                                      # dataset_final.csv
├── notebooks/
│   ├── 00_historical_data_validation.ipynb
│   ├── 01_extraction_coverage.ipynb
│   ├── 02_population_build.ipynb
│   ├── 03_role_metrics.ipynb
│   ├── 04_role_correlations.ipynb
│   ├── 05_multirole_elite_count.ipynb
│   ├── 06_role_specialists_reference.ipynb
│   └── 07_dataset_final.ipynb
├── src/                              # Reusable extraction functions
├── scripts/                          # Standalone scripts (validation, full extraction run)
├── reports/figures/                  # Exported preview visualizations (ahead of Tableau)
├── METHODOLOGY.md                    # Decisions, tools, techniques (why)
├── MASTER_PLAN.md                    # Step-by-step task list, Spanish only (what, in what order)
└── README.md
```

## Reproducing this

```bash
pip install -r requirements.txt

# Full extraction (900 matches, several hours, resumable, requires Chrome)
ENV=production python scripts/run_extraction.py

# Then run the notebooks in order, 00 through 07
```

The extraction script hits SofaScore's internal API through a real browser (via ScraperFC/botasaurus), so it needs Chrome installed locally and is deliberately rate-limited; it can be safely stopped and resumed. Each notebook builds on the previous one's output in `data/processed/`.

---

<a id="español"></a>

**[English](#english) | [Español](#español)**

---

# Messi: Una Anomalía

Análisis estadístico de qué tan singular es el perfil de Lionel Messi en Mundiales, medido contra toda la población histórica de jugadores de Mundiales y no contra un puñado de comparaciones elegidas a mano.

## Estado actual

**Completo.** Pipeline de datos completo (8 notebooks, `00` al `07`), documentado por completo en `METHODOLOGY.md`, y un dashboard interactivo de 3 partes publicado en Tableau Public (links abajo).

## La pregunta

¿Existe algún jugador histórico de Mundiales que se acerque a combinar, simultáneamente, las métricas que distinguen a finalizadores, desequilibrantes, creadores de juego y organizadores de élite, o el perfil de Messi resalta precisamente por aparecer entre la élite de varios roles funcionales distintos al mismo tiempo?

Nota de encuadre: "anomalía" puede sugerir unicidad absoluta, y no es exactamente lo que muestran los datos. Messi comparte el techo más alto realmente observado en la población (élite en 3 de 4 roles) con otros 7 jugadores. Lo que los datos sí muestran, y que se sostiene bajo cada umbral y corte de muestra probado, es algo más preciso: en toda la población mundialista 1966-2026, ningún perfil de jugador supera claramente ni iguala de forma consistente al de Messi en la medida que más importa, el percentil promedio de rol entre jugadores con una muestra de carrera real. Eso es una afirmación sobre la ausencia de un rival mejor respaldado por evidencia, no sobre unicidad matemática.

## Por qué este proyecto

Este es un proyecto de portafolio de Data Analytics, construido para ser reproducible y defendible en una entrevista técnica, no una recopilación de estadísticas de Messi. El razonamiento completo detrás de cada decisión, incluyendo las que no salieron como se esperaba, vive en `METHODOLOGY.md`. `MASTER_PLAN.md` (solo en español, documento de trabajo) lleva el registro secuencial de tareas de punta a punta.

## Enfoque (resumen)

- Los jugadores se comparan por **rol funcional** (finalizador, desequilibrante, creador de juego, organizador), no por posición nominal, porque la posición de un jugador muchas veces no coincide con lo que realmente hace en la cancha. Se asignaron 16 métricas, verificadas contra el glosario propio del proveedor de datos, a los cuatro roles; las métricas sin cobertura histórica sólida (como xG/xA, disponible solo desde 2022) se revisaron y se descartaron.
- Las métricas se normalizan **por 90 minutos**, agregadas a nivel jugador-carrera (una fila por jugador, sumando todos sus partidos de Mundial entre 1966 y 2026), con un **mínimo de 270 minutos** (tres partidos completos), elegido probando dónde se estabiliza realmente el ruido de muestra chica en goles per 90 sobre la población real. Pisos más altos (900, 1500 minutos) se usan en todo el proyecto como chequeo de transparencia, no como reemplazo.
- "Élite" se define por **percentil**, no un top-N fijo, probado en los percentiles 90, 95 y 99 en vez de comprometerse con un solo corte.
- Los percentiles se calculan contra **toda la población relevante de jugadores** (5636 jugadores de campo; 2488 cumplen el umbral de 270 minutos), no solo contra unos pocos jugadores de referencia. Las comparaciones de referencia y las derivadas estadísticamente siempre quedan claramente etiquetadas como una u otra, nunca mezcladas.
- La hipótesis tuvo permiso de fallar, y falló, en su forma más fuerte: ningún jugador, incluyendo a Messi, alcanza estatus de élite en los cuatro roles a la vez en un umbral de élite genuino.

## Resultados

**Fases 0-1, validación y extracción de datos.** Confirmado, contra un partido de Maradona de 1986 y la final de 2022, que la API interna de SofaScore tiene un nivel de detalle de eventos comparable en todo el rango 1966-2026. Extracción completa: 900 partidos, 5636 jugadores de campo a nivel de carrera.

**Fase 4, correlación entre roles.** Los tres roles ofensivos (finalizador, desequilibrante, creador) correlacionan de forma moderada entre sí (0.49-0.58). Organizador de juego es casi independiente de los tres (0.02-0.30), confirmándolo como una dimensión de habilidad genuinamente distinta. Esto llevó a una predicción, hecha antes de correr cualquier número: organizador sería el punto relativamente más débil de Messi.

**Fase 5, el hallazgo central.** Ningún jugador de la población alcanza estatus de élite en los 4 roles en un umbral genuino (percentil 90 o superior). El techo real, élite en 3 de 4 roles, lo comparten 8 jugadores; Messi es uno de ellos, con por lejos la muestra de carrera más grande (6 Mundiales, 34 partidos, 3054 minutos). Entre jugadores con una muestra de carrera real (900+ minutos), Messi tiene el percentil promedio de rol más alto de toda la población. Maradona es un segundo lugar genuino, no elegido a conveniencia, con la distancia explicada casi por completo por organizador de juego, exactamente como se predijo en la Fase 4. Cristiano Ronaldo, con una muestra de carrera casi idéntica a la de Messi, tiene el promedio de puntaje de rol más bajo de los conjuntos de comparación del proyecto, evidencia directa de que el hallazgo no es simplemente una función de jugar muchos Mundiales.

**Fase 6, especialistas por rol.** Armar el conjunto de referencia para los radares sacó a la luz su propio hallazgo: el líder de organizador con el umbral base de 270 minutos resultó estar impulsado por un solo partido de posesión de mucho volumen y poco peligro (la eliminación de España en octavos de 2018 contra Rusia), no por calidad real de organización. Se aplicó un piso más exigente de 900 minutos específicamente para elegir a quién mostrar como "líder".

## Conclusión

Ningún perfil de jugador en la población mundialista 1966-2026 supera claramente ni iguala de forma consistente al de Messi en los cuatro roles funcionales medidos acá. Esto no es una afirmación de unicidad matemática, varios otros jugadores comparten el techo observado, y Maradona es un segundo lugar real y bien respaldado. Es una afirmación sobre la ausencia de un rival mejor respaldado por evidencia, en la medida más robusta que este proyecto pudo construir: percentil promedio de rol entre jugadores con una muestra de carrera genuina, probado en múltiples umbrales de percentil y múltiples pisos de minutos, ninguno de los cuales cambió el resultado. La única debilidad relativa encontrada, organizador de juego, se predijo antes de correr los datos, lo que refuerza el hallazgo en vez de debilitarlo.

La limitación declarada se mantiene: esto mide aproximadamente 6 meses de fútbol acumulado (los seis Mundiales de Messi) contra una carrera mucho más larga, un recorte de alcance deliberado explicado en `METHODOLOGY.md`, no un descuido.

## Cierre de un capítulo, mientras se cerraba este proyecto

El 31 de agosto de 2026, mientras este proyecto estaba en construcción, Lionel Messi anunció oficialmente su retiro de la selección argentina, después de disputar su sexto Mundial. Con 39 años, en lo que fue su última participación, convirtió 8 goles y dio 4 asistencias en 8 partidos, llevando a Argentina hasta la final. Son números que la inmensa mayoría de los futbolistas de la historia no alcanza ni en su mejor momento físico, y él los produjo al final de su carrera. Con esto, su participación en Mundiales queda cerrada para siempre: seis torneos entre 2006 y 2026, 34 partidos, 21 goles.

Esto no fue planeado. El proyecto arrancó como un ejercicio de portafolio de Data Analytics, y terminó coincidiendo, sin buscarlo, con el cierre real y definitivo de la carrera mundialista del jugador que analiza. A partir de ahora, los datos de Messi en Mundiales ya no van a cambiar. Este es, en ese sentido, un registro final y completo, no una fotografía de un proceso todavía en marcha.

El fútbol, cuando se lo mira de cerca así, es más que un juego. Nos hizo apoyar de forma incondicional a un país en el que ni siquiera nacimos. Para quienes lo disfrutamos así, los Mundiales ya no se van a sentir igual sin él en la cancha.

Gracias, Leo. Y por siempre voy a llevar el 18 de diciembre de 2022 en el corazón, el día en que cumpliste tu sueño de niño.

## Fuentes de datos

- **SofaScore**: la única fuente de datos del proyecto. Estadísticas detalladas a nivel de partido (pases, duelos, toques, regates, tiros) accedidas a través de su API interna (no existe una API pública oficial), usando la librería ScraperFC. Validada primero contra un partido de Maradona de 1986 y la final de 2022 antes de comprometerse con una extracción completa; confirmada con un nivel de detalle comparable en todo el rango 1966-2026.
- FBref y Kaggle se consideraron como fuentes complementarias al inicio pero finalmente no hicieron falta; la cobertura histórica de SofaScore cubrió todo lo que las métricas del proyecto necesitaban.

## Stack

Python, pandas, Jupyter, Matplotlib, ScraperFC (extracción de SofaScore), Tableau Public para el dashboard final.

## Dashboards

- [Dashboard 1: ¿los cuatro roles son realmente distintos?](https://public.tableau.com/views/MessiOutlier/Dash1Loscuatrorolessonrealmentedistintos?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) — heatmap de correlación entre roles y un scatter interactivo del par más débil (creador de juego vs. organizador).
- [Dashboard 2: el hallazgo central](https://public.tableau.com/views/MessiOutlier/Dash2Elhallazgocentral?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) — promedio de puntaje de rol vs. minutos de carrera (control interactivo de mínimo de minutos), y la distribución de en cuántos roles llega cada jugador al umbral de élite.
- [Dashboard 3: perfiles](https://public.tableau.com/views/MessiOutlier/Dash3Perfiles?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) — Messi contra el conjunto de referencia de la Fase 6, contra el top 5 individual de cada rol, y contra un conjunto de candidatos históricos a GOAT seleccionado editorialmente.

## Estructura del repositorio

```
messi-outlier/
├── data/
│   ├── raw/                          # 900 archivos de partido crudos + manifiesto, nunca editados a mano
│   └── processed/                    # population.csv, role_metrics.csv, role_scores.csv,
│                                      # role_specialists.csv, role_correlation_matrix.csv,
│                                      # dataset_final.csv
├── notebooks/
│   ├── 00_historical_data_validation.ipynb
│   ├── 01_extraction_coverage.ipynb
│   ├── 02_population_build.ipynb
│   ├── 03_role_metrics.ipynb
│   ├── 04_role_correlations.ipynb
│   ├── 05_multirole_elite_count.ipynb
│   ├── 06_role_specialists_reference.ipynb
│   └── 07_dataset_final.ipynb
├── src/                              # Funciones reutilizables de extracción
├── scripts/                          # Scripts puntuales (validación, corrida de extracción completa)
├── reports/figures/                  # Visualizaciones previas exportadas (antes de Tableau)
├── METHODOLOGY.md                    # Decisiones, herramientas, técnicas (el porqué)
├── MASTER_PLAN.md                    # Lista de tareas paso a paso, solo en español (el qué, en qué orden)
└── README.md
```

## Cómo reproducir esto

```bash
pip install -r requirements.txt

# Extracción completa (900 partidos, varias horas, resumible, requiere Chrome)
ENV=production python scripts/run_extraction.py

# Después corré los notebooks en orden, del 00 al 07
```

El script de extracción le pega a la API interna de SofaScore a través de un navegador real (vía ScraperFC/botasaurus), así que necesita Chrome instalado localmente y está deliberadamente limitado en velocidad; se puede parar y retomar sin problema. Cada notebook se construye sobre el output del anterior en `data/processed/`.