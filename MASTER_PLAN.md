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
- [ ] Definir umbral mínimo de minutos — pendiente, se resuelve en Parte 4 con distribuciones reales en mano
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

## PARTE 3 — Fase 2: Limpieza y construcción de la población

- [ ] 3.1 Aplicar filtro de rango de años (1966-2026)
- [ ] 3.2 Aplicar filtro de exclusión de arqueros
- [ ] 3.3 Aplicar la decisión NaN=0 en campos de conteo de eventos
- [ ] 3.4 Construir, además del dataset de población a nivel de carrera, las métricas totales de longevidad/trayectoria por jugador (Mundiales disputados, partidos jugados, rondas alcanzadas), documentadas como observación separada del cálculo de élite por rol, no mezcladas con el per 90
- [ ] 3.5 Construir `notebooks/02_population_build.ipynb`
- [ ] 3.6 Exportar `data/processed/population.csv`
- [ ] 3.7 Documentar la decisión del punto 3.4 y cualquier otra decisión de limpieza relevante en `METHODOLOGY.md`
- [ ] 3.8 Commit de Fase 2

---

## PARTE 4 — Fase 3: Métricas por rol y normalización per 90

- [ ] 4.1 Revisar disponibilidad histórica real de cada métrica candidata contra la extracción completa (no solo el caso de prueba de la Fase 0)
- [ ] 4.2 Descartar métricas mal cubiertas o inconsistentes entre épocas, documentando por qué
- [ ] 4.3 Calcular métricas per 90 minutos para las métricas que sobreviven
- [ ] 4.4 Graficar la distribución real de minutos jugados en la población
- [ ] 4.5 Fijar el umbral mínimo de minutos usando esa distribución (no un número arbitrario elegido antes de ver los datos)
- [ ] 4.6 Justificar y documentar el umbral elegido en `METHODOLOGY.md`
- [ ] 4.7 Construir `notebooks/03_role_metrics.ipynb`
- [ ] 4.8 Commit de Fase 3

---

## PARTE 5 — Fase 4: Relación entre roles

- [ ] 5.1 Calcular la matriz de correlación entre las 4 dimensiones de rol sobre la población completa
- [ ] 5.2 Visualizar (heatmap o scatter matrix)
- [ ] 5.3 Evaluar si el patrón respalda que los roles se comportan como dimensiones estadísticamente distintas (sección 12 de las instrucciones del proyecto)
- [ ] 5.4 Construir `notebooks/04_role_correlations.ipynb`
- [ ] 5.5 Documentar el hallazgo, sea cual sea, en `METHODOLOGY.md`
- [ ] 5.6 Commit de Fase 4

---

## PARTE 6 — Fase 5: Conteo de élite multi-rol (evidencia central del proyecto)

- [ ] 6.1 Definir y justificar el criterio de "élite" por rol (top 5 vs. percentil), apoyándose en lo observado en las fases anteriores
- [ ] 6.2 Para cada jugador de la población, calcular en cuántos de los 4 roles cae en rango de élite
- [ ] 6.3 Construir la distribución completa de la población (cuántos jugadores caen en 0, 1, 2, 3 o 4 roles de élite)
- [ ] 6.4 Ubicar a Messi dentro de esa distribución
- [ ] 6.5 Ubicar también a los jugadores de referencia (Cristiano, Neymar, Mbappé, Ronaldinho, etc.) en la misma distribución, con el mismo cálculo
- [ ] 6.6 Escribir el hallazgo central en markdown, incluso si contradice parcial o totalmente la hipótesis del proyecto
- [ ] 6.7 Construir `notebooks/05_multirole_elite_count.ipynb`
- [ ] 6.8 Documentar el criterio de élite elegido y el resultado en `METHODOLOGY.md`
- [ ] 6.9 Commit de Fase 5

---

## PARTE 7 — Fase 6: Especialistas por rol (comunicación, no evidencia)

- [ ] 7.1 Identificar el líder estadístico de la población en la métrica principal de cada uno de los 4 roles
- [ ] 7.2 Decidir qué jugadores de referencia conocidos se agregan manualmente aunque no lideren esa métrica específica en esta población
- [ ] 7.3 Etiquetar claramente cada nombre como "líder estadístico" o "adición de referencia" en la tabla/dataset resultante
- [ ] 7.4 Construir `notebooks/06_role_specialists_reference.ipynb`
- [ ] 7.5 Commit de Fase 6

---

## PARTE 8 — Dataset final y Tableau

- [ ] 8.1 Construir `notebooks/XX_dataset_final.ipynb`: integrar outputs de todas las fases anteriores, validar consistencia
- [ ] 8.2 Exportar el dataset final a `data/processed/`
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
| Dataset final e integración | `notebooks/XX_dataset_final.ipynb` |
| Decisiones metodológicas, herramientas y razones | `METHODOLOGY.md` |
| Tableau | Fuera del repo de notebooks, en Tableau Public |