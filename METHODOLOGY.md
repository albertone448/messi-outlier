# Methodology Notes

This document is the project's methodological memory: decisions made, why they were made, tools and techniques used, and things ruled out along the way. It's not a sequential plan or a task tracker, that lives in `MASTER_PLAN.md`. This document gets updated as decisions are made, including decisions that get reversed later. The goal is to be able to explain and defend every choice in an interview, not to keep a changelog of code.

## Central question

Does any historical World Cup player come close to combining, at the same time, the metrics that separate elite finishers, dribblers, chance creators and play organizers, or does Messi's profile stand out for appearing among the elite of several distinct functional roles at once?

This is deliberately not "what's the probability another Messi exists." That wouldn't be statistically defensible with this kind of data.

## What the thesis is not

The thesis is not that Messi ranks first historically in every metric. He doesn't need to. Football has functions that require different profiles: a pure finisher usually doesn't produce a midfielder's organization numbers, a dribbler-heavy winger usually doesn't create like a playmaker. Being exceptional in one dimension is relatively common among historically great players. The possible anomaly is being simultaneously within the elite range of several dimensions tied to different functional roles.

## Bias control

This project starts from a hypothesis that favors Messi, which creates a real risk of confirmation bias. The data must be allowed to contradict the hypothesis. Concretely, this rules out: dropping players because they hurt the conclusion, choosing metrics only after seeing Messi does well on them, changing a threshold (e.g. top 5 to top 10) because it produces a better story, excluding World Cups that weaken the argument, or hiding contradicting metrics. Every non-trivial decision below should be answerable to "why did you make this choice before knowing the result."

## Status: Phase 0, historical data feasibility (completed)

Before designing the notebooks or the pipeline, the project needed to know whether the data even supports the analysis for older World Cups. Building everything assuming 1966-2026 data is equally detailed would have been premature.

**Test case:** Argentina vs England, 1986 World Cup quarter-final (Maradona's "Hand of God" and "Goal of the Century" match). Chosen because it's Maradona's most documented match, making it the best-case scenario for historical data availability, not the average case.

**Findings:**

- SofaScore's own blog content references match-by-match "Sofascore Rating" and granular stats (successful dribbles, duels won, touches, pass accuracy, chip passes) for Maradona's 1986 campaign. This was secondary evidence (SofaScore describing its own data), not a direct check of the raw data, so it didn't count as validation by itself.
- Inspecting ScraperFC's source directly (not assuming how it works) confirmed: SofaScore has no official public API; the library hits an internal endpoint at `https://api.sofascore.com/api/v1`; the FIFA World Cup tournament id on SofaScore is `16`.
- ScraperFC drives an actual browser under the hood (via botasaurus) rather than making plain HTTP requests, because SofaScore has anti-bot protection. This matters for reproducibility: running the extraction requires Chrome installed locally.
- Ran `scripts/validate_maradona_1986.py` against the live API. `1986` is a valid World Cup season, and the Argentina vs England match exists as event id `7846755`. Player-level lineup stats for that match include real values for all four candidate role dimensions: `goals`/`totalShots` (finisher), `totalContest`/`wonContest` (dribbler), `keyPass`/`totalCross` (creator), `totalPass`/`accuratePass`/`touches` (organizer). Maradona's row: 2 goals, 7 shots, 10/15 successful dribbles, 5 key passes, 31 passes with 24 completed, 73 touches, duel record 19W/13L, rating 9.8.
- **Open question raised by the data:** several event-derived fields (`fouls`, `hitWoodwork`, `bigChanceMissed`) returned `NaN` rather than an explicit `0` for players with heavy involvement in the match, including Maradona (`fouls: NaN` despite being heavily involved in duels). Checking Terry Fenwick, known for physically marking Maradona, ruled out "NaN always means 0": he shows `fouls: 3.0`. This left it ambiguous whether the NaN pattern was a 1986-specific coverage gap or a general API convention.
- **Resolved:** ran the same lineup check against the 2022 World Cup final (Argentina vs France), one of the most heavily covered matches in SofaScore's dataset. 8 of 25 players with 45+ minutes played also show `fouls: NaN`, including well-known, heavily-involved players like Di María and Griezmann. This confirms the NaN pattern is not a 1986-specific coverage gap: it's a general convention of this API, most likely because these fields come from an event feed, and a stat key only gets created when at least one event of that type is recorded for a player. No key means no event, not "not tracked because it's an old match."

**Decision:** event-count fields (`fouls`, `bigChanceMissed`, `hitWoodwork`, and similarly structured columns) will be treated as `0` when `NaN` during data cleaning, applied consistently across all eras. This is a data-cleaning assumption, not a proven fact about each individual player-match, and it's documented here so it can be revisited if later evidence contradicts it.

**Phase 0 conclusion:** SofaScore's internal API provides match-level data for the 1986 World Cup at a level of detail comparable to 2022, covering candidate metrics for all four functional roles. Maradona is cleared to participate in the full four-role analysis, not just basic stats. This was tested against the single most-documented Maradona match as a best case, not the average case, so per-match coverage should still be spot-checked for less prominent 1986 matches once the full extraction is built. Narrative version of this validation lives in `notebooks/00_historical_data_validation.ipynb`.

## Extraction method

SofaScore is accessed through its internal API (no official public API exists), using the ScraperFC library, which handles the anti-bot browser automation. This is being documented explicitly per the project's transparency rules: an internal API is not the same as a public, stable, officially supported one, and that has implications for reproducibility (structure can change without notice) and for rate limiting (requests should not be aggressive).

## Population definition

**World Cup range (decided 2026-08-27):** 1966-2026. SofaScore exposes valid seasons back to 1930, but Phase 0 only directly validated detailed event data for 1986 and 2022. 1966 was chosen as the population's lower bound because that's the era SofaScore's own historical content (Sofascore Rating comparisons) already references, giving some independent signal of coverage before further spot-checks. Matches before 1966 are excluded from the population for now, not because they're assumed to lack value, but because there's no evidence yet either way. This can expand later if spot-checks on earlier tournaments support it.

**Position scope:** the population is built by functional role, not nominal position (see "Functional roles" below), so defenders and midfielders are not excluded upfront just for being labeled as such. **Goalkeepers are excluded from the base population (decided 2026-08-27):** all four roles are structurally offensive/build-up oriented, and a goalkeeper's passing or distribution numbers aren't meaningfully comparable to an outfield organizer's. Reversible if a concrete reason to include them comes up later.

**Minimum-minutes threshold:** not yet defined. Will be set once real per-90 distributions are in hand, so the threshold is chosen by looking at where small-sample noise actually shows up in the data, not picked arbitrarily beforehand.

## Functional roles (working definition, not final)

Four candidate dimensions, to be validated against real data before being locked in:

- **Finisher**: goals, xG, shot conversion, shots on target. Archetype: out-and-out center forward.
- **Dribbler**: successful dribbles, fouls received, progressive carries. Archetype: winger.
- **Chance creator**: assists, key passes, xA, big chances created. Archetype: advanced playmaker ("10" / attacking midfielder).
- **Play organizer**: progressive passes, pass completion, passes into the final third. Archetype: deeper, build-up midfielder.

These are candidates. Before adopting any metric it needs to be checked for historical availability, consistency across sources, and whether different sources define it the same way.

**Pre-registered expectation (2026-08-27, before running any organizer-role numbers):** of the four functional roles, "play organizer" is expected to be Messi's relative weak point compared to the other three. This isn't a data finding, it's declared here first: "chance creator" describes an advanced playmaker archetype, which matches Messi's natural game far more closely than "play organizer," which describes a deeper, build-up midfielder archetype. If the data doesn't support this, that gets reported as-is, not adjusted after the fact.

## Role leaders / reference players

**Decided 2026-08-27.** Two separate, clearly labeled categories, never mixed:

- **Statistical role leaders**: the actual top player(s) in that role's primary metric(s), computed within the defined population (1966-2026 World Cups). This is data, not opinion, and it's what feeds any claim about "who leads a role historically in this dataset."
- **Manually added reference players**: well-known players (Cristiano Ronaldo, Neymar, Mbappé, Ronaldinho, etc.) added to visualizations like the radar chart for recognizability, even when they don't statistically lead that specific role within this specific population. Example: Cristiano might not be the World-Cup-only goals leader in this dataset even though he's a top scorer in football history broadly; he can still be shown as a reference point.

Every chart or table that includes a manually added reference player must visually or textually distinguish them from statistical leaders (e.g. a different marker, an explicit label), so a reader can't mistake "recognizable name added for context" for "this player statistically leads this role." This follows directly from the project's rule against disguising interpretation or communication choices as findings.

## Open decisions (not yet made)

- Minimum-minutes threshold for per-90 comparisons (see "Population definition" above).
- Whether "top 5" or a percentile-based cutoff defines the "elite" range per role. This must be justified methodologically, not chosen after seeing which one favors Messi.
- Whether FBref and SofaScore metrics can be safely combined given definitional differences.
- Whether pre-1966 World Cups can be added to the population later, pending further spot-checks.

---

# Notas metodológicas

Este documento es la memoria metodológica del proyecto: decisiones tomadas, por qué se tomaron, herramientas y técnicas usadas, y cosas que se descartaron en el camino. No es un plan secuencial ni un tracker de tareas, eso vive en `MASTER_PLAN.md`. Se actualiza a medida que se toman decisiones, incluyendo decisiones que después se revierten. El objetivo es poder explicar y defender cada elección en una entrevista, no llevar un changelog del código.

## Pregunta central

¿Existe algún jugador histórico de Mundiales que se acerque a combinar, simultáneamente, las métricas que distinguen a finalizadores, desequilibrantes, creadores de juego y organizadores de élite, o el perfil de Messi resalta precisamente por aparecer entre la élite de varios roles funcionales distintos al mismo tiempo?

Deliberadamente esto no es "cuál es la probabilidad de que exista otro Messi". Eso no sería sostenible estadísticamente con este tipo de datos.

## Lo que la tesis no es

La tesis no es que Messi sea número uno histórico en cada métrica. No necesita serlo. El fútbol tiene funciones que requieren perfiles distintos: un finalizador puro normalmente no produce los números de organización de un mediocampista, un extremo desequilibrante normalmente no crea juego como un armador. Ser extraordinario en una sola dimensión es relativamente común entre los grandes jugadores históricos. La posible anomalía es estar simultáneamente dentro del rango de élite en varias dimensiones asociadas a roles funcionales distintos.

## Control de sesgo

Este proyecto parte de una hipótesis favorable a Messi, lo que crea un riesgo real de confirmation bias. Los datos deben tener permiso para contradecir la hipótesis. En concreto, esto descarta: eliminar jugadores porque perjudican la conclusión, elegir métricas solo después de ver que Messi destaca en ellas, cambiar un umbral (por ejemplo top 5 a top 10) porque produce una mejor historia, excluir Mundiales que debiliten el argumento, u ocultar métricas contradictorias. Cada decisión no trivial de este documento debería poder responder a "por qué tomé esta decisión antes de conocer el resultado".

## Estado actual: Fase 0, viabilidad de datos históricos (completada)

Antes de diseñar los notebooks o el pipeline, había que saber si los datos siquiera sostienen el análisis para Mundiales antiguos. Construir todo asumiendo que los datos de 1966 a 2026 son igual de detallados hubiera sido prematuro.

**Caso de prueba:** Argentina vs Inglaterra, cuartos de final del Mundial 1986 (el partido de "la Mano de Dios" y el "Gol del Siglo" de Maradona). Elegido porque es el partido más documentado de Maradona, lo que lo convierte en el mejor escenario posible para disponibilidad de datos históricos, no en el escenario promedio.

**Hallazgos:**

- El propio blog de SofaScore hace referencia a un "Sofascore Rating" partido a partido y a estadísticas granulares (regates exitosos, duelos ganados, toques, precisión de pase, chip passes) para la campaña de Maradona en 1986. Esto fue evidencia secundaria (SofaScore describiendo sus propios datos), no una revisión directa del dato crudo, así que no contaba como validación por sí sola.
- Al inspeccionar directamente el código fuente de ScraperFC (sin asumir cómo funciona) se confirmó: SofaScore no tiene API pública oficial; la librería usa un endpoint interno en `https://api.sofascore.com/api/v1`; el id de SofaScore para el torneo FIFA World Cup es `16`.
- ScraperFC controla un navegador real por debajo (vía botasaurus) en lugar de hacer solicitudes HTTP simples, porque SofaScore tiene protección anti-bot. Esto importa para la reproducibilidad: correr la extracción requiere tener Chrome instalado localmente.
- Se corrió `scripts/validate_maradona_1986.py` contra la API real. `1986` es una temporada válida del Mundial, y el partido Argentina-Inglaterra existe como evento id `7846755`. Las estadísticas por jugador de ese partido incluyen valores reales para las cuatro dimensiones de rol candidatas: `goals`/`totalShots` (finalizador), `totalContest`/`wonContest` (desequilibrante), `keyPass`/`totalCross` (creador), `totalPass`/`accuratePass`/`touches` (organizador). La línea de Maradona: 2 goles, 7 remates, 10/15 regates exitosos, 5 pases clave, 31 pases con 24 completados, 73 toques, récord de duelos 19G/13P, nota 9.8.
- **Pregunta abierta que surgió de los datos:** varios campos derivados de eventos (`fouls`, `hitWoodwork`, `bigChanceMissed`) devolvieron `NaN` en vez de un `0` explícito para jugadores con mucha participación en el partido, incluyendo a Maradona (`fouls: NaN` a pesar de estar muy involucrado en duelos). Revisar a Terry Fenwick, conocido por marcar físicamente a Maradona, descartó que "NaN siempre significa 0": él muestra `fouls: 3.0`. Esto dejó ambiguo si el patrón de NaN era una brecha de cobertura específica de 1986 o una convención general de la API.
- **Resuelto:** se corrió el mismo chequeo de alineación contra la final del Mundial 2022 (Argentina vs Francia), uno de los partidos con mejor cobertura del dataset de SofaScore. 8 de 25 jugadores con 45+ minutos también muestran `fouls: NaN`, incluyendo jugadores muy conocidos y con mucha participación como Di María y Griezmann. Esto confirma que el patrón de NaN no es una brecha de cobertura específica de 1986: es una convención general de esta API, lo más probable porque estos campos vienen de un feed de eventos, y una clave de estadística solo se crea cuando hay al menos un evento de ese tipo registrado para un jugador. Sin clave no hay evento, no significa "no se registró por ser un partido viejo".

**Decisión:** los campos de conteo de eventos (`fouls`, `bigChanceMissed`, `hitWoodwork`, y columnas con estructura similar) se van a tratar como `0` cuando sean `NaN` durante la limpieza de datos, aplicado igual para todas las épocas. Esto es un supuesto de limpieza de datos, no un hecho probado sobre cada partido-jugador individual, y queda documentado acá para poder revisarlo si aparece evidencia que lo contradiga.

**Conclusión de la Fase 0:** la API interna de SofaScore ofrece datos a nivel de partido para el Mundial de 1986 con un nivel de detalle comparable al de 2022, cubriendo métricas candidatas para los cuatro roles funcionales. Maradona queda habilitado para participar en el análisis completo de los cuatro roles, no solo en estadísticas básicas. Esto se probó contra su partido más documentado como mejor escenario posible, no el promedio, así que la cobertura por partido todavía debería revisarse puntualmente para partidos menos prominentes de 1986 una vez que se construya la extracción completa. La versión narrativa de esta validación vive en `notebooks/00_historical_data_validation.ipynb`.

## Método de extracción

Se accede a SofaScore a través de su API interna (no existe una API pública oficial), usando la librería ScraperFC, que maneja la automatización de navegador para evitar la protección anti-bot. Esto se documenta explícitamente según las reglas de transparencia del proyecto: una API interna no es lo mismo que una API pública, estable y oficialmente soportada, y eso tiene implicaciones para la reproducibilidad (la estructura puede cambiar sin aviso) y para el rate limiting (las solicitudes no deben ser agresivas).

## Definición de población

**Rango de Mundiales (decidido 2026-08-27):** 1966-2026. SofaScore expone temporadas válidas desde 1930, pero la Fase 0 solo validó directamente datos detallados de eventos para 1986 y 2022. Se eligió 1966 como límite inferior de la población porque es la era a la que ya hace referencia el propio contenido histórico de SofaScore (comparaciones de Sofascore Rating), lo que da alguna señal independiente de cobertura antes de más spot-checks. Los partidos anteriores a 1966 quedan excluidos de la población por ahora, no porque se asuma que no tienen valor, sino porque todavía no hay evidencia en ningún sentido. Esto puede ampliarse después si spot-checks en torneos más antiguos lo respaldan.

**Alcance de posiciones:** la población se construye por rol funcional, no por posición nominal (ver "Roles funcionales" abajo), así que defensas y mediocampistas no quedan excluidos de entrada solo por estar etiquetados así. **Los arqueros quedan excluidos de la población base (decidido 2026-08-27):** los cuatro roles son estructuralmente ofensivos/de construcción de juego, y los números de pase o distribución de un arquero no son comparables de forma significativa a los de un organizador de campo. Es reversible si más adelante aparece una razón concreta para incluirlos.

**Umbral mínimo de minutos:** todavía no definido. Se va a fijar una vez que se tengan las distribuciones reales per 90 en mano, para elegir el umbral mirando dónde aparece de verdad el ruido de muestra pequeña en los datos, no eligiéndolo arbitrariamente de antemano.

## Roles funcionales (definición de trabajo, no final)

Cuatro dimensiones candidatas, a validar contra datos reales antes de fijarlas:

- **Finalizador**: goles, xG, conversión de tiros, tiros al arco. Arquetipo: delantero centro puro.
- **Desequilibrante**: regates exitosos, faltas recibidas, conducciones progresivas. Arquetipo: extremo.
- **Creador de juego**: asistencias, pases clave, xA, big chances creadas. Arquetipo: armador avanzado ("10" / mediapunta).
- **Organizador de juego**: pases progresivos, precisión de pase, pases al último tercio. Arquetipo: mediocampista de base, más retrasado.

Son candidatas. Antes de adoptar cualquier métrica hay que revisar disponibilidad histórica, consistencia entre fuentes, y si distintas fuentes la definen igual.

**Expectativa pre-registrada (2026-08-27, antes de correr cualquier número del rol organizador):** de los cuatro roles funcionales, se espera que "organizador de juego" sea el punto relativamente más débil de Messi comparado con los otros tres. Esto no es un hallazgo de datos, se declara acá primero: "creador de juego" describe un arquetipo de armador avanzado, que se parece mucho más al juego natural de Messi que "organizador de juego", que describe un arquetipo de mediocampista de base más retrasado. Si los datos no respaldan esto, se reporta tal cual, sin ajustarlo después.

## Líderes por rol / jugadores de referencia

**Decidido 2026-08-27.** Dos categorías separadas y claramente etiquetadas, que nunca se mezclan:

- **Líderes estadísticos del rol**: el o los jugadores realmente líderes en la(s) métrica(s) principal(es) de ese rol, calculado dentro de la población definida (Mundiales 1966-2026). Esto es dato, no opinión, y es lo que alimenta cualquier afirmación sobre "quién lidera históricamente un rol en este dataset".
- **Jugadores de referencia agregados manualmente**: jugadores conocidos (Cristiano Ronaldo, Neymar, Mbappé, Ronaldinho, etc.) agregados a visualizaciones como el radar chart por su reconocibilidad, aunque no lideren estadísticamente ese rol específico dentro de esta población específica. Ejemplo: Cristiano puede no ser el líder de goles solo-en-Mundiales de este dataset aunque sea uno de los máximos goleadores de la historia del fútbol en general; igual se puede mostrar como punto de referencia.

Todo gráfico o tabla que incluya un jugador de referencia agregado manualmente debe distinguirlo visual o textualmente de los líderes estadísticos (por ejemplo, un marcador distinto, una etiqueta explícita), para que quien lo lea no confunda "nombre reconocible agregado por contexto" con "este jugador lidera estadísticamente este rol". Esto se desprende directamente de la regla del proyecto contra disfrazar interpretación o decisiones de comunicación como hallazgos.

## Decisiones abiertas (aún no tomadas)

- Umbral mínimo de minutos para comparaciones per 90 (ver "Definición de población" arriba).
- Si "top 5" o un corte basado en percentil define el rango de "élite" por rol. Esto debe justificarse metodológicamente, no elegirse después de ver cuál favorece a Messi.
- Si las métricas de FBref y SofaScore se pueden combinar con seguridad dado que podrían definirse distinto.
- Si los Mundiales anteriores a 1966 se pueden agregar a la población más adelante, pendiente de más spot-checks.