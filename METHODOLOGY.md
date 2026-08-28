# Methodology

This document is the project's methodological memory. It gets updated as decisions are made, including decisions that get reversed later. The goal is to be able to explain and defend every choice in an interview, not to keep a changelog of code.

## Central question

Does any historical World Cup player come close to combining, at the same time, the metrics that separate elite finishers, dribblers, chance creators and play organizers, or does Messi's profile stand out for appearing among the elite of several distinct functional roles at once?

This is deliberately not "what's the probability another Messi exists." That wouldn't be statistically defensible with this kind of data.

## What the thesis is not

The thesis is not that Messi ranks first historically in every metric. He doesn't need to. Football has functions that require different profiles: a pure finisher usually doesn't produce a midfielder's organization numbers, a dribbler-heavy winger usually doesn't create like a playmaker. Being exceptional in one dimension is relatively common among historically great players. The possible anomaly is being simultaneously within the elite range of several dimensions tied to different functional roles.

## Bias control

This project starts from a hypothesis that favors Messi, which creates a real risk of confirmation bias. The data must be allowed to contradict the hypothesis. Concretely, this rules out: dropping players because they hurt the conclusion, choosing metrics only after seeing Messi does well on them, changing a threshold (e.g. top 5 to top 10) because it produces a better story, excluding World Cups that weaken the argument, or hiding contradicting metrics. Every non-trivial decision below should be answerable to "why did you make this choice before knowing the result."

## Status: Phase 0, historical data feasibility

Before designing the notebooks or the pipeline, the project needs to know whether the data even supports the analysis for older World Cups. Building everything assuming 1966-2026 data is equally detailed would be premature.

**Test case:** Argentina vs England, 1986 World Cup quarter-final (Maradona's "Hand of God" and "Goal of the Century" match). Chosen because it's Maradona's most documented match, making it the best-case scenario for historical data availability, not the average case.

**Findings so far (as of this session):**

- SofaScore's own blog content references match-by-match "Sofascore Rating" and granular stats (successful dribbles, duels won, touches, pass accuracy, chip passes) for Maradona's 1986 campaign. This is secondary evidence (SofaScore describing its own data), not a direct check of the raw data, so it doesn't count as validation by itself.
- Inspecting ScraperFC's source directly (not assuming how it works) confirmed: SofaScore has no official public API; the library hits an internal endpoint at `https://api.sofascore.com/api/v1`; the FIFA World Cup tournament id on SofaScore is `16`; and `1986` needs to be confirmed as a valid season through `get_valid_seasons`, which hasn't been run yet against the live API from an environment with real network access to sofascore.com.
- ScraperFC drives an actual browser under the hood (via botasaurus) rather than making plain HTTP requests, because SofaScore has anti-bot protection. This matters for reproducibility: running the extraction requires Chrome installed locally.

**Pending:** run `scripts/validate_maradona_1986.py` from a machine with real network access, and inspect the raw JSON/CSV output together before deciding whether Maradona is included in the full four-role analysis, only partially, or only with basic stats (goals, cards, minutes).

## Extraction method

SofaScore is accessed through its internal API (no official public API exists), using the ScraperFC library, which handles the anti-bot browser automation. This is being documented explicitly per the project's transparency rules: an internal API is not the same as a public, stable, officially supported one, and that has implications for reproducibility (structure can change without notice) and for rate limiting (requests should not be aggressive).

## Functional roles (working definition, not final)

Four candidate dimensions, to be validated against real data before being locked in:

- **Finisher**: goals, xG, shot conversion, shots on target.
- **Dribbler**: successful dribbles, fouls received, progressive carries.
- **Chance creator**: assists, key passes, xA, big chances created.
- **Play organizer**: progressive passes, pass completion, passes into the final third.

These are candidates. Before adopting any metric it needs to be checked for historical availability, consistency across sources, and whether different sources define it the same way.

## Open decisions (not yet made)

- Minimum-minutes threshold for per-90 comparisons.
- Whether "top 5" or a percentile-based cutoff defines the "elite" range per role. This must be justified methodologically, not chosen after seeing which one favors Messi.
- Whether FBref and SofaScore metrics can be safely combined given definitional differences.

---

# Metodología

Este documento es la memoria metodológica del proyecto. Se actualiza a medida que se toman decisiones, incluyendo decisiones que después se revierten. El objetivo es poder explicar y defender cada elección en una entrevista, no llevar un changelog del código.

## Pregunta central

¿Existe algún jugador histórico de Mundiales que se acerque a combinar, simultáneamente, las métricas que distinguen a finalizadores, desequilibrantes, creadores de juego y organizadores de élite, o el perfil de Messi resalta precisamente por aparecer entre la élite de varios roles funcionales distintos al mismo tiempo?

Deliberadamente esto no es "cuál es la probabilidad de que exista otro Messi". Eso no sería sostenible estadísticamente con este tipo de datos.

## Lo que la tesis no es

La tesis no es que Messi sea número uno histórico en cada métrica. No necesita serlo. El fútbol tiene funciones que requieren perfiles distintos: un finalizador puro normalmente no produce los números de organización de un mediocampista, un extremo desequilibrante normalmente no crea juego como un armador. Ser extraordinario en una sola dimensión es relativamente común entre los grandes jugadores históricos. La posible anomalía es estar simultáneamente dentro del rango de élite en varias dimensiones asociadas a roles funcionales distintos.

## Control de sesgo

Este proyecto parte de una hipótesis favorable a Messi, lo que crea un riesgo real de confirmation bias. Los datos deben tener permiso para contradecir la hipótesis. En concreto, esto descarta: eliminar jugadores porque perjudican la conclusión, elegir métricas solo después de ver que Messi destaca en ellas, cambiar un umbral (por ejemplo top 5 a top 10) porque produce una mejor historia, excluir Mundiales que debiliten el argumento, u ocultar métricas contradictorias. Cada decisión no trivial de este documento debería poder responder a "por qué tomé esta decisión antes de conocer el resultado".

## Estado actual: Fase 0, viabilidad de datos históricos

Antes de diseñar los notebooks o el pipeline, hay que saber si los datos siquiera sostienen el análisis para Mundiales antiguos. Construir todo asumiendo que los datos de 1966 a 2026 son igual de detallados sería prematuro.

**Caso de prueba:** Argentina vs Inglaterra, cuartos de final del Mundial 1986 (el partido de "la Mano de Dios" y el "Gol del Siglo" de Maradona). Elegido porque es el partido más documentado de Maradona, lo que lo convierte en el mejor escenario posible para disponibilidad de datos históricos, no en el escenario promedio.

**Hallazgos hasta ahora (en esta sesión):**

- El propio blog de SofaScore hace referencia a un "Sofascore Rating" partido a partido y a estadísticas granulares (regates exitosos, duelos ganados, toques, precisión de pase, chip passes) para la campaña de Maradona en 1986. Esto es evidencia secundaria (SofaScore describiendo sus propios datos), no una revisión directa del dato crudo, así que no cuenta como validación por sí sola.
- Al inspeccionar directamente el código fuente de ScraperFC (sin asumir cómo funciona) se confirmó: SofaScore no tiene API pública oficial; la librería usa un endpoint interno en `https://api.sofascore.com/api/v1`; el id de SofaScore para el torneo FIFA World Cup es `16`; y falta confirmar que `1986` sea una temporada válida vía `get_valid_seasons`, algo que todavía no se ha corrido contra la API real desde un entorno con acceso de red real a sofascore.com.
- ScraperFC controla un navegador real por debajo (vía botasaurus) en lugar de hacer solicitudes HTTP simples, porque SofaScore tiene protección anti-bot. Esto importa para la reproducibilidad: correr la extracción requiere tener Chrome instalado localmente.

**Pendiente:** correr `scripts/validate_maradona_1986.py` desde una máquina con acceso de red real, y revisar juntos el JSON/CSV crudo antes de decidir si Maradona entra al análisis completo de los cuatro roles, solo parcialmente, o solo con estadísticas básicas (goles, tarjetas, minutos).

## Método de extracción

Se accede a SofaScore a través de su API interna (no existe una API pública oficial), usando la librería ScraperFC, que maneja la automatización de navegador para evitar la protección anti-bot. Esto se documenta explícitamente según las reglas de transparencia del proyecto: una API interna no es lo mismo que una API pública, estable y oficialmente soportada, y eso tiene implicaciones para la reproducibilidad (la estructura puede cambiar sin aviso) y para el rate limiting (las solicitudes no deben ser agresivas).

## Roles funcionales (definición de trabajo, no final)

Cuatro dimensiones candidatas, a validar contra datos reales antes de fijarlas:

- **Finalizador**: goles, xG, conversión de tiros, tiros al arco.
- **Desequilibrante**: regates exitosos, faltas recibidas, conducciones progresivas.
- **Creador de juego**: asistencias, pases clave, xA, big chances creadas.
- **Organizador de juego**: pases progresivos, precisión de pase, pases al último tercio.

Son candidatas. Antes de adoptar cualquier métrica hay que revisar disponibilidad histórica, consistencia entre fuentes, y si distintas fuentes la definen igual.

## Decisiones abiertas (aún no tomadas)

- Umbral mínimo de minutos para comparaciones per 90.
- Si "top 5" o un corte basado en percentil define el rango de "élite" por rol. Esto debe justificarse metodológicamente, no elegirse después de ver cuál favorece a Messi.
- Si las métricas de FBref y SofaScore se pueden combinar con seguridad dado que podrían definirse distinto.
