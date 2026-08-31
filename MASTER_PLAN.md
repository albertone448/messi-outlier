# Plan maestro — messi-outlier

Documento de seguimiento secuencial. Se trabaja de arriba hacia abajo, un paso a la vez, marcando `[x]` conforme se completa. No saltar pasos: si algo no aplica o se decide dejar para después, se anota explícitamente en vez de simplemente omitirlo, para no perder el rastro entre conversaciones.

Las decisiones metodológicas de fondo (por qué se eligió algo, qué se descartó y por qué, herramientas usadas) viven en `METHODOLOGY.md`, no acá. Este documento es la lista de tareas, no el razonamiento detrás de ellas.

---

## PARTE 0 — Fase 0: Viabilidad de datos históricos — COMPLETA

- [x] Elegir caso de prueba (Argentina vs Inglaterra, Mundial 1986, partido más documentado de Maradona)
- [x] Instalar y revisar el código fuente de ScraperFC para entender cómo accede a SofaScore (endpoint interno, id de torneo, requiere navegador real por anti-bot)
- [x] Escribir `scripts/validate_maradona_1986.py`
- [x] Correr el script contra la API real, confirmar que 1986 es temporada válida y que el partido existe (id `7846755`)
- [x] Confirmar que las 4 dimensiones de rol tienen candidatos con datos reales en ese partido
- [x] Detectar el patrón de `NaN` en campos de conteo de eventos (`fouls`, etc.)
- [x] Descartar la hipótesis de que `NaN` siempre significa 0 (caso Fenwick)
- [x] Escribir `scripts/check_nan_pattern_modern_match.py` y correrlo contra la final del Mundial 2022
- [x] Confirmar que el patrón de NaN es una convención general de la API, no una brecha de cobertura de 1986
- [x] Decidir tratamiento: NaN = 0 en campos de conteo de eventos, aplicado a todas las épocas
- [x] Construir `notebooks/00_historical_data_validation.ipynb` con la narrativa completa de la Fase 0
- [x] Mover los CSV/JSON generados por los scripts a `data/raw/` con nombres descriptivos
- [x] Documentar todo el proceso y la conclusión en `METHODOLOGY.md`
- [x] Commit de Fase 0

---

## PARTE 1 — Definición de población y roles

- [x] Definir rango de Mundiales de la población: 1966-2026
- [x] Justificar por qué 1966 y no otro año (referencia independiente en contenido histórico de SofaScore)
- [x] Definir alcance de posiciones: por rol funcional, no por posición nominal
- [x] Decidir exclusión de arqueros de la población base, con justificación
- [x] Definir los 4 roles funcionales candidatos (finalizador, desequilibrante, creador, organizador) con su arquetipo de jugador
- [x] Declarar expectativa pre-registrada sobre el rol organizador (punto relativamente más débil de Messi, declarado antes de ver números)
- [x] Definir método de selección de líderes por rol: líder estadístico (dato) + adiciones manuales de referencia (comunicación), claramente etiquetadas y nunca mezcladas
- [x] Definir umbral mínimo de minutos — 270 minutos (3 partidos), ver Parte 4
- [ ] Definir criterio de "élite" por rol (top 5 vs. corte por percentil) — pendiente, se resuelve en Parte 6 con datos reales en mano
- [x] Decidir nivel de agregación de la población: jugador-carrera (una fila por jugador, sumando todos sus Mundiales 1966-2026), no jugador-torneo
- [x] Decidir conservar tanto totales como métricas per 90, cada uno etiquetado para lo que mide, con el detalle de longevidad/rondas alcanzadas documentado como observación separada del cálculo de élite por rol
- [x] Documentar todo lo anterior en `METHODOLOGY.md`

---

## PARTE 2 — Fase 1: Extracción completa de datos — COMPLETA

- [x] 2.1 Definir la lista completa de partidos de Mundiales 1966-2026 a extraer (usar `get_match_dicts` por año, no solo el caso de prueba)
- [x] 2.2 Escribir el script de extracción completo en `src/` (reutilizable, a diferencia de los scripts de validación puntual que quedaron en `scripts/`)
- [x] 2.3 Implementar manejo de rate limiting razonable (no golpear la API de forma agresiva, ver nota de transparencia en `METHODOLOGY.md`)
- [x] 2.4 Definir naming convention consistente para los archivos de `data/raw/` (un archivo por partido en `data/raw/lineups/{match_id}.csv`, manifiesto en `data/raw/matches_manifest.csv`)
- [x] 2.5 Correr la extracción completa (900/900 partidos, sin fallos pendientes; se resolvió en el camino un bloqueo anti-bot 403 con reintentos + cooldown automático, y un bug de botasaurus que pausaba la ejecución esperando input humano, corregido con `ENV=production`)
- [x] 2.6 Construir `notebooks/01_extraction_coverage.ipynb`: cuantificar cobertura real por Mundial
- [x] 2.7 Identificar si hay Mundiales dentro del rango 1966-2026 con cobertura significativamente peor que 1986/2022 (no se encontraron huecos a nivel de archivo; validación adicional con Messi en sus 6 Mundiales, incluyendo su sequía goleadora real de 2010)
- [ ] 2.8 Decidir cómo se tratan huecos a nivel de campo individual (no de archivo) — pendiente para la Fase 2, cuando se trabaje con las columnas reales
- [x] 2.9 Documentar hallazgos de cobertura y las decisiones técnicas del camino en `METHODOLOGY.md`
- [ ] 2.10 Commit de Fase 1

---

## PARTE 3 — Fase 2: Limpieza y construcción de la población — COMPLETA

- [x] 3.1 Aplicar filtro de rango de años (1966-2026) — ya viene aplicado desde la extracción (Fase 1)
- [x] 3.2 Resolver la ambigüedad de las columnas duplicadas `position`/`position.1` (perfil general vs. táctica del partido, confirmado leyendo el código fuente de ScraperFC) y aplicar el filtro de exclusión de arqueros por aparición-partido usando `position.1`, no por jugador completo
- [x] 3.3 Aplicar la decisión NaN=0 solo a columnas genuinas de conteo de eventos, después de descartar primero a los suplentes no utilizados (filas con 0 minutos o minutos ausentes), dejando intactas columnas limitadas por época como `expectedGoals`
- [x] 3.4 Construir, además del dataset de población a nivel de carrera, los totales de trayectoria por jugador (partidos jugados, Mundiales disputados), documentados como observación separada del cálculo de élite por rol, no mezclados con el per 90
- [x] 3.5 Chequeo de consistencia interna (accurate ≤ total en pases, regates, centros, tiros) — cero violaciones
- [x] 3.6 Construir `notebooks/02_population_build.ipynb`
- [x] 3.7 Exportar `data/processed/population.csv` (5636 jugadores de campo, nivel jugador-carrera, 29 columnas incluyendo `totalOppositionHalfPasses`/`accurateOppositionHalfPasses`, solo totales, sin per 90)
- [x] 3.8 Documentar todas las decisiones de limpieza de esta fase en `METHODOLOGY.md`
- [ ] 3.9 Commit de Fase 2

---

## PARTE 4 — Fase 3: Métricas por rol y normalización per 90 — COMPLETA

- [x] 4.1 Revisar disponibilidad histórica real de cada métrica candidata contra la extracción completa (no solo el caso de prueba de la Fase 0)
- [x] 4.2 Descartar métricas mal cubiertas o inconsistentes entre épocas, documentando por qué (xG/xA solo 2022-2026, conducción progresiva con hueco 1978-2002)
- [x] 4.3 Calcular métricas per 90 minutos para las métricas que sobreviven
- [x] 4.4 Graficar la distribución real de minutos jugados en la población
- [x] 4.5 Fijar el umbral mínimo de minutos: 270 (probando media/std de goles per 90 en varios cortes, el std toca mínimo justo ahí y sube después; 270 min = fase de grupos completa del formato clásico de 32 equipos)
- [x] 4.6 Justificar y documentar el umbral elegido en `METHODOLOGY.md`
- [x] 4.7 Clasificar las 21 métricas sobrevivientes en los 4 roles funcionales (16 asignadas, 5 excluidas del framework por no describir un rol con precisión), con definiciones verificadas contra el glosario del proveedor de datos, no asumidas por el nombre de columna
- [x] 4.8 Construir `notebooks/03_role_metrics.ipynb`
- [x] 4.9 Exportar `data/processed/role_metrics.csv` (2488 jugadores que cumplen el umbral, 45 columnas: totales, per-90 y metadata)
- [ ] 4.10 Commit de Fase 3

---

## PARTE 5 — Fase 4: Relación entre roles — COMPLETA

- [x] 5.1 Calcular la matriz de correlación entre las 4 dimensiones de rol sobre la población calificada (n=2488), combinadas primero en puntaje compuesto por percentil (no promedio crudo)
- [x] 5.2 Visualizar (heatmap)
- [x] 5.3 Evaluar si el patrón respalda que los roles se comportan como dimensiones estadísticamente distintas (sección 12 de las instrucciones del proyecto): sí, pero con matices — los 3 roles ofensivos correlacionan moderado entre sí (0.49-0.58), organizador está cerca de ser independiente de los tres (0.02-0.30)
- [x] 5.4 Construir `notebooks/04_role_correlations.ipynb`
- [x] 5.5 Documentar el hallazgo en `METHODOLOGY.md`, incluyendo la razón de diseño de roles y la predicción pre-registrada para la Fase 5 (percentil 84 de Messi en organizador, y que la correlación poblacional no garantiza rendimiento individual correlacionado)
- [x] 5.7 Exportar `data/processed/role_scores.csv` (2488 jugadores, 4 puntajes de rol por percentil)
- [ ] 5.6 Commit de Fase 4

---

## PARTE 6 — Fase 5: Múltiples vistas del rendimiento multi-rol (evidencia central del proyecto)

Replanteado 2026-08-29: no hay una sola respuesta correcta a "¿es Messi
único en los cuatro roles?", hay varias formas legítimas de medirlo
(conteo binario de élite vs. promedio continuo; distintos umbrales de
percentil; distintos pisos de minutos), y cada una puede mostrar algo
distinto (el caso de Maradona, invisible en el conteo binario por su
organizador bajo, pero 2do en promedio con muestra seria, es la prueba de
por qué). En vez de elegir una vista y presentarla como "la respuesta",
la Fase 5 combina todas en una sola tabla de síntesis, dejando explícito
qué depende de qué elección metodológica.

- [x] 6.1 Definir y justificar el criterio de "élite" por rol: percentil, no top-N fijo. Probado en 90/95/99, con 85 usado solo como diagnóstico de sensibilidad, no como criterio oficial (aclarado después de una confusión propia en el camino)
- [x] 6.2 Para cada jugador de la población, calcular en cuántos de los 4 roles cae en rango de élite, en los 3 umbrales oficiales
- [x] 6.3 Construir la distribución completa de la población en cada umbral (cuántos jugadores caen en 0, 1, 2, 3 o 4 roles de élite)
- [x] 6.4 Ubicar a Messi dentro de esa distribución en cada umbral
- [x] 6.5 Identificar el techo real observado en cada umbral y quiénes lo alcanzan (no solo Messi, toda la población)
- [x] 6.6 Investigar los casos que llegan al techo con muestra chica (Zidane/Cruyff/Onega en el umbral 85), confirmar que son datos reales (no error), y chequear con evidencia si hay sesgo de muestra chica residual en la cola extrema pese al umbral de 270 minutos ya validado
- [x] 6.7 Agregar el promedio de puntaje de rol (las 4 métricas percentil promediadas) como vista complementaria al conteo binario, para capturar la diferencia entre "perfil parejo cerca del umbral" y "perfil con picos que domina en varios roles y falla por poco en uno"
- [x] 6.8 Repetir tanto el conteo de élite como el promedio con pisos de minutos más altos (900, 1500), como chequeo de sensibilidad transparente al umbral oficial de 270, sin reemplazarlo
- [x] 6.9 Construir una tabla de síntesis única (no fragmentos dispersos) con, para un conjunto relevante de jugadores (Messi, jugadores de referencia, y quien aparezca en el top de cualquiera de las vistas anteriores): conteo de élite en 90/95/99, promedio de puntaje de rol en 270/900/1500, y los totales de carrera (minutos, partidos, Mundiales) de la Parte 1
- [x] 6.10 Interpretación final integrando todas las vistas: qué se sostiene en todas las combinaciones de criterio, qué depende de cuál se elija, y qué le pasó específicamente a Maradona como ejemplo del porqué de esto
- [x] 6.11 Escribir el hallazgo central en markdown, incluso si contradice parcial o totalmente la hipótesis del proyecto (ninguna forma de "élite en los 4 a la vez" está respaldada; sí lo está "mejor promedio multi-rol entre muestras de carrera reales", con Maradona como segundo lugar genuino y Cristiano Ronaldo como contraste directo)
- [x] 6.12 Construir `notebooks/05_multirole_elite_count.ipynb`
- [x] 6.13 Documentar todo el criterio y el resultado en `METHODOLOGY.md`, incluyendo el principio interpretativo de que esto no es un concurso de dueño único
- [ ] 6.14 Commit de Fase 5

---

## PARTE 7 — Fase 6: Especialistas por rol (comunicación, no evidencia) — COMPLETA

- [x] 7.1 Identificar el líder estadístico de la población en la métrica principal de cada uno de los 4 roles, con un piso de 900 minutos aplicado específicamente para esta selección (más exigente que los 270 de la población analítica), después de detectar que el líder de organizador con 270 min (Isco, 390 minutos) reflejaba un caso real de posesión estéril (España-Rusia, octavos 2018), no buen rendimiento como organizador
- [x] 7.2 Decidir 2 jugadores de referencia conocidos por rol (8 en total: Xavi/Pirlo, Zidane/Cruyff, Neymar/Jairzinho, Cristiano/Mbappé), cada uno verificado contra sus propios 4 puntajes antes de asignarlo (Ronaldinho descartado de desequilibrante al confirmar que su puntaje más alto es creador, reemplazado por Jairzinho)
- [x] 7.3 Etiquetar claramente cada nombre como `statistical_leader` o `reference_addition` en el dataset resultante
- [x] 7.4 Construir `notebooks/06_role_specialists_reference.ipynb`
- [x] 7.6 Exportar `data/processed/role_specialists.csv` (12 filas: 4 líderes + 8 referencias)
- [x] 7.7 Agregar tabla de referencia top 10 por rol (270 y 900 minutos) al notebook, sin uso posterior en el pipeline, solo registro visual
- [x] 7.5 Commit de Fase 6

---

## PARTE 8 — Dataset final y Tableau

- [x] 8.1 Construir `notebooks/07_dataset_final.ipynb`: integrar outputs de todas las fases anteriores, validar consistencia (ids coincidentes entre `role_metrics`/`role_scores`, sin duplicados, sin columnas vacías, 5 jugadores clave verificados con valores consistentes de ambas fuentes)
- [x] 8.2 Exportar el dataset final a `data/processed/dataset_final.csv` (2488 jugadores, 72 columnas) y confirmar `role_specialists.csv` de la Fase 6 sin cambios
- [x] 8.2.1 Construir 4 visualizaciones previas en el mismo notebook (promedio vs. minutos de carrera, distribución de roles de élite, coordenadas paralelas de Messi vs. destacados multi-rol, coordenadas paralelas de Messi vs. top-5 por rol individual), guardadas en `reports/figures/`, como boceto de trabajo antes del dashboard real
- [x] 8.2.2 Documentar la interpretación del arco de carrera (minutos de juventud/veteranía como capa de dificultad adicional, razonada pero no demostrable como contrafactual) y la nota de opinión sobre el rol finalizador, ambas etiquetadas explícitamente como interpretación/opinión, no como hallazgo estadístico
- [x] 8.2.3 Commit de la Fase de integración final y visualizaciones previas
- [ ] 8.3 Diseñar el dashboard en Tableau Public (filtros por jugador, torneo, rol, métrica)
- [ ] 8.4 Publicar el dashboard
- [ ] 8.5 Agregar el link del dashboard al README
- [ ] 8.6 Revisión final: confirmar que README y METHODOLOGY.md reflejan el estado real del proyecto de punta a punta
- [ ] 8.7 Commit de cierre

---

## Referencia: dónde vive cada cosa (notebooks)

| Pieza | Notebook / lugar |
|---|---|
| Validación de viabilidad histórica (Fase 0) | `notebooks/00_historical_data_validation.ipynb` |
| Cobertura de la extracción completa (Fase 1) | `notebooks/01_extraction_coverage.ipynb` |
| Construcción de la población (Fase 2) | `notebooks/02_population_build.ipynb` |
| Métricas por rol y per 90 (Fase 3) | `notebooks/03_role_metrics.ipynb` |
| Correlación entre roles (Fase 4) | `notebooks/04_role_correlations.ipynb` |
| Conteo de élite multi-rol, hallazgo central (Fase 5) | `notebooks/05_multirole_elite_count.ipynb` |
| Especialistas por rol para el radar chart (Fase 6) | `notebooks/06_role_specialists_reference.ipynb` |
| Dataset final e integración | `notebooks/07_dataset_final.ipynb` |
| Decisiones metodológicas, herramientas y razones | `METHODOLOGY.md` |
| Tableau | Fuera del repo de notebooks, en Tableau Public |