<a id="english"></a>

**[English](#english) | [Español](#español)**

---

# Methodology Notes

This document is the project's methodological memory: decisions made, why they were made, tools and techniques used, and things ruled out along the way. It's not a sequential plan or a task tracker, that lives in `MASTER_PLAN.md`. This document gets updated as decisions are made, including decisions that get reversed later. The goal is to be able to explain and defend every choice in an interview, not to keep a changelog of code.

## Central question

Does any historical World Cup player come close to combining, at the same time, the metrics that separate elite finishers, dribblers, chance creators and play organizers, or does Messi's profile stand out for appearing among the elite of several distinct functional roles at once?

This is deliberately not "what's the probability another Messi exists." That wouldn't be statistically defensible with this kind of data.

## What the thesis is not

The thesis is not that Messi ranks first historically in every metric. He doesn't need to. Football has functions that require different profiles: a pure finisher usually doesn't produce a midfielder's organization numbers, a dribbler-heavy winger usually doesn't create like a playmaker. Being exceptional in one dimension is relatively common among historically great players. The possible anomaly is being simultaneously within the elite range of several dimensions tied to different functional roles.

## Bias control

This project starts from a hypothesis that favors Messi, which creates a real risk of confirmation bias. The data must be allowed to contradict the hypothesis. Concretely, this rules out: dropping players because they hurt the conclusion, choosing metrics only after seeing Messi does well on them, changing a threshold (e.g. top 5 to top 10) because it produces a better story, excluding World Cups that weaken the argument, or hiding contradicting metrics. Every non-trivial decision below should be answerable to "why did you make this choice before knowing the result."

## Interpretive principle for the final conclusion

**Decided 2026-08-29.** The project's conclusion is not a "sole owner" contest. If another player (Zidane, Maradona, or anyone else) reaches a comparable multi-role level by some measure, that doesn't cancel or diminish Messi's result, both can be true at once, and the write-up says so rather than searching for a framing that declares a single winner. Phase 5 already produced exactly this situation in practice: Messi shares the observed ceiling (3-of-4 elite roles at the 90th percentile) with 7 other players, and Maradona is a genuine runner-up by average role score among large-sample players. Neither fact is treated as invalidating the central finding, both are reported as what they are.

The final conclusion reads the numbers together with their human context, not the number in isolation. "Player X has the highest average role score" is a fact; "and sustained it across 6 tournaments spanning roughly two decades, not a single hot streak" is what makes that fact meaningful as an achievement. The longevity/totals observation already logged as its own axis (see "Totals vs. per-90" above) isn't a side note kept separate from the conclusion, it's part of how the conclusion gets read: the numbers establish what happened, the surrounding context (age span, tournaments sustained, era, minutes accumulated against elite opposition over time) establishes why it's remarkable, and the final write-up carries both, not one without the other.

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

## Phase 1: full extraction (completed)

Ran the complete extraction across all 900 World Cup matches from 1966 to 2026 (see "Extraction method" below for the anti-bot challenges hit along the way and how they were handled). Result: 900 of 900 matches have a lineup file, none empty, 35-52 player rows per match.

**Independent sanity check:** beyond file counts, checked whether the data reproduces something true about the world that it wasn't told. Messi appears in all 36 of his World Cup matches across his six tournaments (2006, 2010, 2014, 2018, 2022, 2026), and every one of his 5 matches in 2010 shows `goals: NaN` (treated as 0 per the decision above), matching the well known real fact that he didn't score at that tournament. Narrative version lives in `notebooks/01_extraction_coverage.ipynb`.

**Open item carried into Phase 2:** the column-count inconsistency across matches (event-derived columns like `goals` simply don't exist in a match with zero of that event) was confirmed again at full scale, not just in the Phase 0 test case. This needs to be handled explicitly when merging all 900 matches into one population dataset (e.g. `pd.concat` with proper NaN-filling for missing columns, verified rather than assumed), not treated as already solved.

## Phase 2: population construction (completed)

Built the player-career population from the 900 raw lineup files, following the aggregation-level and totals-vs-per-90 decisions above.

**Column ambiguity found and resolved:** the raw data has two `position` columns after flattening, one from the player's general profile (career-typical position) and one from that specific match's tactical lineup slot, disambiguated by reading ScraperFC's source directly rather than guessing. They disagreed on 3876 of 22761 rows (17%), almost entirely reclassifications between defender/midfielder/forward. Only 2 rows involved a goalkeeper label at all: two players (1986 Iraq, 2002 Türkiye) whose match-tactical position was "G" while their general profile position was an outfield position, consistent with (though not independently confirmed as) an emergency outfield-player-in-goal situation. Given the project's rule of comparing by functional role actually performed rather than nominal position, the goalkeeper exclusion filter uses the match-tactical field (`position.1`), applied per match-appearance, not per player: a player who filled in as keeper for one match has only that specific appearance excluded, not their whole career.

**Cleaning pipeline:** concatenate all 900 matches (letting the column mismatch across matches resolve into `NaN` via `pd.concat`, confirmed rather than assumed), drop rows with 0 or missing minutes played (unused substitutes), apply NaN=0 only to genuine event-count columns (confirmed via `totalPass`: 98.8% of its NaN rows belonged to 0-minute players, a real zero, not missing data), leaving era-limited columns like `expectedGoals` (91.6% NaN, present mostly in recent tournaments) untouched rather than invented. Exclude goalkeeper match-appearances as above. Aggregate to one row per player (by SofaScore's numeric `id`, not name, to avoid collisions), summing career totals and building the longevity fields (`world_cups_played`, `matches_played`, first/last World Cup) documented as a separate observation per the totals-vs-per-90 decision.

**Internal consistency check:** verified that `accuratePass <= totalPass`, `wonContest <= totalContest`, `accurateCross <= totalCross`, and `onTargetScoringAttempt <= totalShots` hold for every player in the resulting population, zero violations. This doesn't just confirm the data isn't empty, it confirms it isn't internally contradictory.

**Sanity check:** Messi's career row: 6 World Cups, 34 matches, 3054 minutes, 21 career goals. That total is internally consistent with the per-match goal values already seen across his six tournaments earlier in the pipeline (they sum to exactly 21), i.e. the aggregation correctly reproduces its own upstream data end to end.

**Result:** `data/processed/population.csv`, 5636 outfield players, one row per career with totals only (goals, shots, passes, duels, minutes, etc., plus the longevity fields). Per-90 rates are deliberately not computed here, that's Phase 3's responsibility (`03_role_metrics.ipynb`), together with metric selection and the minimum-minutes threshold, since those are a distinct concern from building and validating the population itself. Narrative version lives in `notebooks/02_population_build.ipynb`.

## Phase 3: role metrics and per-90 normalization (completed)

Started from the 21 event-count metrics that survived Phase 2's cleaning. Surviving isn't the same as belonging to a role, so this got treated as an explicit, separate decision: 16 of the 21 were assigned to one of the four functional roles, 5 were deliberately left out of the role framework entirely (`duelWon`/`duelLost`: a physical/defensive dimension that cuts across every position, not specific to these four attacking/creative roles; `fouls` committed: discipline, not functional performance; `shotOffTarget`, `hitWoodwork`, `bigChanceMissed`: finishing context rather than primary metrics, and in `bigChanceMissed`'s case, a metric that would unfairly penalize players who get into more good positions in the first place).

**Definitions verified, not assumed:** some column names are not self-explanatory and getting them wrong would misread the whole role. Checked against the data provider's own glossary (Opta, the standard behind this kind of event data): `keyPass` specifically excludes passes that led to a goal (those count as `goalAssist` instead, the two categories don't overlap), and `bigChanceCreated` requires a materially higher bar than a key pass, a situation where a teammate should reasonably be expected to score (a one-on-one or a shot from very close range), not any created opportunity.

**Final role assignment:**
- Finisher: `goals`, `totalShots`, `onTargetScoringAttempt`.
- Dribbler: `totalContest`, `wonContest`, `wasFouled`.
- Chance creator: `keyPass`, `goalAssist`, `bigChanceCreated`, `totalCross`, `accurateCross`.
- Play organizer: `totalPass`, `accuratePass`, `totalOppositionHalfPasses`, `accurateOppositionHalfPasses`, `touches`.

**Result:** `data/processed/role_metrics.csv`, 2488 players (of 5636) who meet the 270-minute threshold, with career totals for every metric and per-90 rates for the 16 role-assigned metrics. Narrative version, including the full per-metric definitions, lives in `notebooks/03_role_metrics.ipynb`.

## Phase 4: role correlations (completed)

Combined each role's per-90 metrics into a single composite score per player via percentile rank within the qualified population (0-100), not a raw average, since raw per-90 scales differ wildly across metrics (e.g. `totalOppositionHalfPasses_per90` in the 30s-40s vs. `goals_per90` under 1) and averaging them directly would let high-scale metrics dominate. The composite score is an added column, not a replacement for the underlying numbers: `role_metrics.csv` keeps every career total and per-90 rate, and any report built from this point on shows the composite next to the raw stats behind it (e.g. "92nd percentile as a chance creator: 101 key passes, 12 assists, 24 big chances created"), not the score in isolation.

**Finding:** correlated the four role scores against each other across the qualified population (n=2488). Two distinct patterns, not one: the three attacking roles (finisher, dribbler, chance creator) correlate moderately with each other (0.49-0.58), sharing some common variance, plausibly a general "attacking quality" factor. Play organizer correlates weakly with all three (0.02 with finisher, 0.13 with dribbler, 0.30 with chance creator), behaving as a largely independent skill dimension. This confirms, with data, the reasoning behind including play organizer as a role in the first place (see "Role design rationale" below): the distance between organizer and the other three is real, not assumed.

**Role design rationale (predates this notebook, made explicit here now that it can be stated precisely):** finisher, dribbler, and chance creator describe variants of the same general attacking profile, players routinely move between these labels over a career (a winger becoming a striker, a striker dropping into a playmaker role, a playmaker shifting wide) without changing what kind of player they fundamentally are. Play organizer describes a materially different function, a deeper build-up role, which is why it was chosen as the comparison point precisely because it was expected to be functionally distant from the other three, not picked after seeing the correlation.

**Pre-registered prediction for Phase 5 (2026-08-29, before defining the elite cutoff or running the multi-role count):** Messi's play_organizer_score is 84.06, high in absolute terms for a role that's nearly independent of his dominant skillset (finisher 97.19, dribbler 95.73, chance creator 92.13). This is predicted to be notable on its own terms regardless of whether it clears whatever "elite" cutoff Phase 5 defines, he is explicitly not predicted to rank top-5, top-10, or even top-20/30 specifically in play organizer. Separately, the moderate correlation among the three attacking roles at the population level does not imply that any individual elite finisher, dribbler, or creator will also be elite in the other correlated roles, that's an aggregate pattern, not a guarantee for a given player, and should be checked directly in Phase 5 rather than assumed from this correlation.

## Phase 5: multi-role elite count (completed)

The central question, operationalized with multiple deliberately different lenses instead of one, since no single lens turned out to be sufficient on its own (see below).

**Elite criterion:** percentile-based, not a fixed top-N, following the pre-registered principle against changing a threshold to fit a result. Tested officially at the 90th, 95th, and 99th percentiles. An 85th-percentile cut was also used, but strictly as a diagnostic tool for the small-sample check below, not as an operative elite bar, an early draft of this section conflated the two and was corrected: 85th percentile describes "good," not "elite" by this project's own standard.

**Binary elite-role count:** at every threshold tested, no player in the qualified population (n=2488) reaches elite status in all 4 roles simultaneously. The strongest form of the hypothesis is not supported. At the 90th percentile, the real ceiling is 3-of-4 roles, reached by 8 players: Messi, Neymar, Hagi, Robinho, Flohe, Babington, Rivellino, and Chislenko. Among those 8, Messi has by a wide margin the largest career sample (3054 minutes, 6 World Cups, 34 matches vs. a second-highest of 1225 minutes / 4 tournaments for Neymar).

**Small-sample tail check:** at the looser 85th-percentile diagnostic cut, three players reach 4-of-4 (Zidane, Cruyff, and Ermindo Onega, a respected 1966 Argentina attacking midfielder confirmed via independent web sources as a real player, not a data error). All three have far smaller career samples (360-1109 minutes) than the bulk of the 3-plus-roles group (867-minute average) or Messi (3054). Population-wide, the correlation between career minutes and elite-role-count is weak (0.178), arguing against a strong systematic small-sample bias overall, but the extreme tail behaves differently from the bulk of the distribution: at 900+ minutes, only Zidane among the three survives; at 1500+, none do. This is reported as a real, open limitation of percentile-based elite cutoffs applied without a sample-size floor, not resolved in either direction.

**Average role score, added as a complementary metric:** the binary count treats "clears the bar by a wide margin in 3 roles, misses the 4th by a little" the same as "barely clears the bar in all 4, dominant in none," which loses real information. The simple mean of the four percentile scores addresses this without depending on any cutoff. At the official 270-minute threshold, Messi ranks 2nd (92.28), narrowly behind Cruyff (93.34, his entire World Cup career in a single tournament). At 900+ minutes, Messi ranks 1st (ahead of Neymar and Hagi). At 1500+ minutes, Messi still ranks 1st, well ahead of Maradona in 2nd (89.24) and a steep drop to third place after that.

**Maradona as a genuine large-sample rival:** 2nd by average role score among 900+ and 1500+ minute players, with the gap to Messi (92.28 vs. 89.24) explained almost entirely by play organizer (84.06 vs. 75.09), the exact role Phase 4 predicted, before this notebook ran, would be Messi's relative weak point.

**Cristiano Ronaldo as a contrasting case:** a career sample nearly identical to Messi's (2206 minutes, 6 World Cups, 27 matches) produces the lowest average role score in the synthesis table (69.52), elite in only 1 of 4 roles, driven by a sharply specialized profile (96.6 as a finisher, 37.1 as an organizer). This is direct evidence the finding isn't simply a function of playing many World Cups: Cristiano had comparable opportunity and longevity, and it didn't produce a comparable multi-role result.

**Interpretive principle applied:** consistent with the interpretive principle above, none of this is framed as a "Messi vs. the field" contest. Messi shares the observed 3-of-4 ceiling with 7 other players and has a genuine, non-cherry-picked runner-up (Maradona) by average score. Both facts are reported alongside the central finding, not treated as undermining it.

**Result:** `data/processed/role_scores.csv` updated with elite-count columns at 3 thresholds and `role_score_avg`. Narrative version, including the full synthesis table across reference players and every player who topped some view of the data, lives in `notebooks/05_multirole_elite_count.ipynb`.

## Phase 6: role specialists for communication (completed)

Unlike Phases 0-5, this phase doesn't produce evidence for the central question, it produces a communication artifact: the small set of players shown on the radar chart (project brief, section 13), which illustrates the difference between specialized and multidimensional profiles.

**Statistical leaders, with a stricter selection floor:** the population's per-role leader (highest single-role score, not the average) is data, not opinion, but selecting who gets featured as "the leader" for communication material used a 900-minute floor, stricter than the 270-minute analytical population. This was needed after the organizer-role leader at 270 minutes turned out to be Isco (390 minutes), driven almost entirely by Spain's high-volume, low-threat passing display in their 2018 round-of-16 exit to Russia, a real match, not a data error, but a poor representative of "elite organizer" for a communication piece. At 900+ minutes, the four leaders are David Villa (finisher), Maradona (dribbler, unchanged from the 270-minute leader), David Beckham (chance creator), and Rodri (organizer), all with recognizable, defensible profiles.

**Reference pairs, verified against their own data before assignment:** two manually added reference players per role, 8 total: Xavi and Andrea Pirlo (organizer), Zidane and Cruyff (chance creator), Neymar and Jairzinho (dribbler), Cristiano Ronaldo and Mbappé (finisher). Ronaldinho was initially considered for the dribbler pairing but dropped once his own four scores showed chance creator (93.75), not dribbling (86.11), as his highest role, replaced with Jairzinho, whose dribbler score (98.99) is unambiguously his own career peak. This follows the project's rule against assigning a reference player to a role their own data contradicts.

**Result:** `data/processed/role_specialists.csv`, 12 rows, explicitly labeled `statistical_leader` or `reference_addition`, ready to feed the Tableau radar chart without ambiguity between data and communication choices. A top-10-per-role reference table (at both 270 and 900 minutes) is also kept in the notebook as a visual record, not used downstream.

## Extraction method

SofaScore is accessed through its internal API (no official public API exists), using the ScraperFC library, which handles the anti-bot browser automation. This is being documented explicitly per the project's transparency rules: an internal API is not the same as a public, stable, officially supported one, and that has implications for reproducibility (structure can change without notice) and for rate limiting (requests should not be aggressive).

**Confirmed 2026-08-28:** during the full 1966-2026 extraction, the API started returning `{'error': {'code': 403, 'reason': 'challenge'}}` (a Cloudflare-style anti-bot challenge) after roughly 500 consecutive requests over about 30-40 minutes. ScraperFC surfaces this as a bare `KeyError('event')`, confirmed by fetching a failed match's raw response directly rather than trusting the library's error message. The extraction script now backs off automatically (a cooldown period after several consecutive failures) instead of treating each one as an independent, unrelated failure, since a run of failures across unrelated matches is this challenge response, not a per-match data problem.

## Population definition

**World Cup range (decided 2026-08-27):** 1966-2026. SofaScore exposes valid seasons back to 1930, but Phase 0 only directly validated detailed event data for 1986 and 2022. 1966 was chosen as the population's lower bound because that's the era SofaScore's own historical content (Sofascore Rating comparisons) already references, giving some independent signal of coverage before further spot-checks. Matches before 1966 are excluded from the population for now, not because they're assumed to lack value, but because there's no evidence yet either way. This can expand later if spot-checks on earlier tournaments support it.

**Position scope:** the population is built by functional role, not nominal position (see "Functional roles" below), so defenders and midfielders are not excluded upfront just for being labeled as such. **Goalkeepers are excluded from the base population (decided 2026-08-27):** all four roles are structurally offensive/build-up oriented, and a goalkeeper's passing or distribution numbers aren't meaningfully comparable to an outfield organizer's. Reversible if a concrete reason to include them comes up later.

**Minimum-minutes threshold (decided 2026-08-29): 270 minutes** (3 full matches). Chosen by testing goals-per-90 mean and standard deviation across candidate thresholds (1, 90, 180, ..., 900 minutes) on the real population, not picked in advance. The standard deviation hits its minimum exactly at 270 minutes (0.199) and rises afterward (0.203 at 360, up to 0.228 at 900), and the mean starts climbing at the same point (0.114 at 270, up to 0.181 at 900). Below 270, small-sample noise dominates (a single early goal produces an absurd per-90 rate, max goals/90 falls from 9.00 at 1 minute to 1.50 by 270). Above 270, raising the threshold further stops reducing noise and instead introduces a selection bias in the other direction, filtering toward players who were kept on the pitch specifically because they were performing well. 270 minutes also has a football-meaningful reading: it's a complete group stage under the standard (now-retired) 32-team, 3-match format, not an arbitrary round number. Leaves 2488 of 5636 players (44.1%).

**Aggregation level (decided 2026-08-28):** the population is built at player-career level, one row per player summing all their World Cup matches across the full 1966-2026 range, not one row per player-per-tournament. The central question is about a player's overall World Cup profile, not about a specific edition, and player-tournament level would let players with many World Cups appear multiple times in the population, which muddies "how many roles is this player elite in" into "elite in which edition." Tournament-by-tournament detail isn't discarded, it stays available as a secondary view (e.g. to show consistency over time), but the Phase 5 multi-role elite count runs on the career-level population.

**Totals vs. per-90 (decided 2026-08-28):** both are computed and kept, on purpose, they answer different questions and neither replaces the other. Per-90 metrics isolate rate of production controlling for playing time, and are what feeds the role-elite percentile analysis, since comparing raw totals would conflate opportunity with skill. Totals (career goals, minutes, matches played, number of World Cups played, rounds reached) capture something per-90 can't: durability and sustained selection at a competitive level over years. Playing many World Cup matches, and especially advancing deep into the knockout stage across multiple tournaments, requires being selected and performing well enough, repeatedly, over a long period, that's a different kind of evidence, not "inflated stats from a bigger sample." This gets tracked and reported as its own explicit, labeled observation, kept separate from the per-90 role-elite calculation rather than folded into it. The fact (e.g. "played N World Cup matches across 6 tournaments spanning 20 years") and the interpretation of what that fact means (a durability/excellence claim) are kept visibly distinct, per the project's rule separating evidence from interpretation from opinion. This applies equally to any player in the population who shows the same pattern, not selectively highlighted only for Messi.

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

- Whether "top 5" or a percentile-based cutoff defines the "elite" range per role. This must be justified methodologically, not chosen after seeing which one favors Messi.
- Whether FBref and SofaScore metrics can be safely combined given definitional differences.
- Whether pre-1966 World Cups can be added to the population later, pending further spot-checks.

---

<a id="español"></a>

**[English](#english) | [Español](#español)**

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

## Principio interpretativo para la conclusión final

**Decidido 2026-08-29.** La conclusión del proyecto no es un concurso de "dueño único". Si otro jugador (Zidane, Maradona, o cualquier otro) alcanza un nivel multi-rol comparable según alguna medida, eso no anula ni disminuye el resultado de Messi, las dos cosas pueden ser ciertas a la vez, y el texto final lo dice así en vez de buscar un encuadre que declare un único ganador. La Fase 5 ya produjo exactamente esta situación en la práctica: Messi comparte el techo observado (3 de 4 roles de élite en el percentil 90) con otros 7 jugadores, y Maradona es un segundo lugar genuino por promedio de puntaje de rol entre jugadores de muestra grande. Ninguno de los dos hechos se trata como algo que invalide el hallazgo central, ambos se reportan como lo que son.

La conclusión final lee los números junto con su contexto humano, no el número aislado. "El jugador X tiene el promedio de puntaje de rol más alto" es un hecho; "y lo sostuvo a lo largo de 6 torneos repartidos en unas dos décadas, no un pico corto" es lo que vuelve ese hecho significativo como logro. La observación de longevidad/totales ya registrada como su propio eje (ver "Totales vs. per 90" arriba) no es una nota al margen separada de la conclusión, es parte de cómo se lee la conclusión: los números establecen qué pasó, el contexto alrededor (rango de edad, torneos sostenidos, época, minutos acumulados contra oposición de élite a lo largo del tiempo) establece por qué es notable, y el texto final lleva las dos cosas, no una sin la otra.

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

## Fase 1: extracción completa (completada)

Se corrió la extracción completa sobre los 900 partidos de Mundiales entre 1966 y 2026 (ver "Método de extracción" abajo para los desafíos anti-bot que aparecieron en el camino y cómo se resolvieron). Resultado: 900 de 900 partidos tienen archivo de alineación, ninguno vacío, entre 35 y 52 filas de jugador por partido.

**Chequeo de sanidad independiente:** más allá del conteo de archivos, se revisó si los datos reproducen algo real del mundo que no se les indicó. Messi aparece en los 36 partidos de sus seis Mundiales (2006, 2010, 2014, 2018, 2022, 2026), y cada uno de sus 5 partidos de 2010 muestra `goals: NaN` (tratado como 0 según la decisión de arriba), coincidiendo con el hecho real conocido de que no convirtió en ese torneo. La versión narrativa vive en `notebooks/01_extraction_coverage.ipynb`.

**Punto abierto que pasa a la Fase 2:** la inconsistencia en la cantidad de columnas entre partidos (columnas derivadas de eventos como `goals` directamente no existen en un partido con cero ocurrencias de ese evento) se confirmó de nuevo a escala completa, no solo en el caso de prueba de la Fase 0. Esto hay que manejarlo explícitamente al unir los 900 partidos en un solo dataset de población (por ejemplo, `pd.concat` con relleno correcto de NaN para columnas faltantes, verificado y no asumido), no darlo por resuelto solo.

## Fase 2: construcción de la población (completada)

Se construyó la población a nivel jugador-carrera a partir de los 900 archivos crudos de alineación, siguiendo las decisiones de nivel de agregación y totales-vs-per-90 de arriba.

**Ambigüedad de columnas encontrada y resuelta:** los datos crudos tienen dos columnas `position` después del aplanado, una del perfil general del jugador (posición típica de carrera) y otra de la alineación táctica de ese partido específico, distinguidas leyendo directamente el código fuente de ScraperFC en vez de adivinar. Estuvieron en desacuerdo en 3876 de 22761 filas (17%), casi todas reclasificaciones entre defensa/mediocampista/delantero. Solo 2 filas involucraron la etiqueta de arquero: dos jugadores (Irak 1986, Türkiye 2002) cuya posición táctica del partido era "G" mientras su posición de perfil general era de campo, consistente con (aunque no confirmado de forma independiente como) una situación de jugador de campo atajando de emergencia. Dado que la regla del proyecto es comparar por rol funcional realmente ejercido y no por posición nominal, el filtro de exclusión de arqueros usa el campo táctico (`position.1`), aplicado por aparición-partido, no por jugador: alguien que atajó de emergencia en un solo partido pierde solo esa aparición puntual, no toda su carrera.

**Pipeline de limpieza:** concatenar los 900 partidos (dejando que el desajuste de columnas entre partidos se resuelva en `NaN` vía `pd.concat`, confirmado y no asumido), descartar filas con 0 minutos o minutos ausentes (suplentes no utilizados), aplicar NaN=0 solo a columnas genuinas de conteo de eventos (confirmado con `totalPass`: 98.8% de sus filas en NaN correspondían a jugadores con 0 minutos, un cero real, no un dato faltante), dejando intactas columnas limitadas por época como `expectedGoals` (91.6% NaN, presente sobre todo en torneos recientes) en vez de inventar el dato. Excluir apariciones como arquero según lo anterior. Agregar a una fila por jugador (por el `id` numérico de SofaScore, no por nombre, para evitar colisiones), sumando totales de carrera y construyendo los campos de longevidad (`world_cups_played`, `matches_played`, primer/último Mundial) documentados como observación separada según la decisión de totales-vs-per-90.

**Chequeo de consistencia interna:** se verificó que `accuratePass <= totalPass`, `wonContest <= totalContest`, `accurateCross <= totalCross`, y `onTargetScoringAttempt <= totalShots` se cumplan para todos los jugadores de la población resultante, cero violaciones. Esto no solo confirma que los datos no están vacíos, confirma que no son internamente contradictorios.

**Chequeo de sanidad:** la fila de carrera de Messi: 6 Mundiales, 34 partidos, 3054 minutos, 21 goles de carrera. Ese total es consistente de forma interna con los valores de gol por partido ya vistos antes en el pipeline para sus seis torneos (suman exactamente 21), es decir, la agregación reproduce correctamente sus propios datos previos de punta a punta.

**Resultado:** `data/processed/population.csv`, 5636 jugadores de campo, una fila por carrera con totales solamente (goles, tiros, pases, duelos, minutos, etc., más los campos de longevidad). Las tasas per 90 deliberadamente no se calculan acá, eso es responsabilidad de la Fase 3 (`03_role_metrics.ipynb`), junto con la selección de métricas y el umbral mínimo de minutos, porque es una preocupación distinta a construir y validar la población en sí. La versión narrativa vive en `notebooks/02_population_build.ipynb`.

## Fase 3: métricas por rol y normalización per 90 (completada)

Partió de las 21 métricas de conteo de eventos que sobrevivieron la limpieza de la Fase 2. Sobrevivir no es lo mismo que pertenecer a un rol, así que se trató como una decisión explícita y separada: 16 de las 21 se asignaron a uno de los cuatro roles funcionales, 5 quedaron deliberadamente fuera del framework de roles por completo (`duelWon`/`duelLost`: una dimensión física/defensiva que atraviesa todas las posiciones, no específica de estos cuatro roles ofensivos/creativos; `fouls` cometidas: disciplina, no rendimiento funcional; `shotOffTarget`, `hitWoodwork`, `bigChanceMissed`: contexto de finalización en vez de métricas primarias, y en el caso de `bigChanceMissed`, una métrica que penalizaría injustamente a jugadores que se meten en más posiciones de gol en primer lugar).

**Definiciones verificadas, no asumidas:** algunos nombres de columna no son evidentes y entenderlos mal malinterpreta todo el rol. Se revisaron contra el glosario propio del proveedor de datos (Opta, el estándar detrás de este tipo de datos de eventos): `keyPass` excluye específicamente los pases que terminaron en gol (esos cuentan como `goalAssist` en su lugar, las dos categorías no se superponen), y `bigChanceCreated` exige una vara sustancialmente más alta que un pase clave, una situación donde razonablemente se esperaría que un compañero convierta (mano a mano con el arquero o un remate desde muy cerca), no cualquier ocasión creada.

**Asignación final de roles:**
- Finalizador: `goals`, `totalShots`, `onTargetScoringAttempt`.
- Desequilibrante: `totalContest`, `wonContest`, `wasFouled`.
- Creador de juego: `keyPass`, `goalAssist`, `bigChanceCreated`, `totalCross`, `accurateCross`.
- Organizador de juego: `totalPass`, `accuratePass`, `totalOppositionHalfPasses`, `accurateOppositionHalfPasses`, `touches`.

**Resultado:** `data/processed/role_metrics.csv`, 2488 jugadores (de 5636) que cumplen el umbral de 270 minutos, con totales de carrera para cada métrica y tasas per 90 para las 16 métricas asignadas a un rol. La versión narrativa, con las definiciones completas por métrica, vive en `notebooks/03_role_metrics.ipynb`.

## Fase 4: correlación entre roles (completada)

Se combinaron las métricas per 90 de cada rol en un único puntaje compuesto por jugador vía percentil dentro de la población calificada (0-100), no un promedio crudo, porque las escalas per 90 crudas difieren enormemente entre métricas (por ejemplo `totalOppositionHalfPasses_per90` ronda 30-40 mientras `goals_per90` está debajo de 1) y promediarlas directamente dejaría que las métricas de escala alta dominen. El puntaje compuesto es una columna agregada, no un reemplazo de los números de base: `role_metrics.csv` conserva cada total de carrera y tasa per 90, y cualquier reporte construido desde acá muestra el compuesto al lado de las estadísticas crudas que lo forman (por ejemplo "percentil 92 como creador de juego: 101 pases clave, 12 asistencias, 24 grandes ocasiones creadas"), no el puntaje aislado.

**Hallazgo:** se correlacionaron los cuatro puntajes de rol entre sí sobre la población calificada (n=2488). Dos patrones distintos, no uno: los tres roles ofensivos (finalizador, desequilibrante, creador) correlacionan de forma moderada entre sí (0.49-0.58), compartiendo algo de varianza común, plausiblemente un factor general de "calidad ofensiva". Organizador de juego correlaciona débilmente con los tres (0.02 con finalizador, 0.13 con desequilibrante, 0.30 con creador), comportándose como una dimensión de habilidad en gran medida independiente. Esto confirma, con datos, el razonamiento detrás de incluir organizador como rol en primer lugar (ver "Razón de diseño de roles" abajo): la distancia entre organizador y los otros tres es real, no asumida.

**Razón de diseño de roles (anterior a este notebook, hecha explícita ahora que se puede plantear con precisión):** finalizador, desequilibrante y creador de juego describen variantes de un mismo perfil general ofensivo, los jugadores se mueven habitualmente entre estas etiquetas a lo largo de una carrera (un extremo que se convierte en delantero, un delantero que retrocede a mediapunta, un mediapunta que se abre a la banda) sin cambiar fundamentalmente qué tipo de jugador son. Organizador de juego describe una función sustancialmente distinta, un rol de construcción más retrasado, por eso se eligió como punto de comparación precisamente porque se esperaba que fuera funcionalmente lejano a los otros tres, no elegido después de ver la correlación.

**Predicción pre-registrada para la Fase 5 (2026-08-29, antes de definir el corte de élite o correr el conteo multi-rol):** el `play_organizer_score` de Messi es 84.06, alto en términos absolutos para un rol casi independiente de su perfil dominante (finalizador 97.19, desequilibrante 95.73, creador 92.13). Se predice que esto es notable en sí mismo sin importar si termina calificando según el corte de "élite" que defina la Fase 5, explícitamente no se predice que quede top-5, top-10, ni siquiera top-20/30 específicamente en organizador. Por separado, la correlación moderada entre los tres roles ofensivos a nivel poblacional no implica que un finalizador, desequilibrante o creador élite puntual también vaya a ser élite en los otros roles correlacionados, eso es un patrón agregado, no una garantía para un jugador dado, y debería revisarse directamente en la Fase 5 en vez de asumirse a partir de esta correlación.

## Fase 5: conteo de élite multi-rol (completada)

La pregunta central, operacionalizada con varias vistas deliberadamente distintas en vez de una sola, porque ninguna vista sola resultó ser suficiente por sí misma (ver abajo).

**Criterio de élite:** basado en percentil, no un top-N fijo, siguiendo el principio pre-registrado contra cambiar un umbral para ajustarse a un resultado. Probado oficialmente en los percentiles 90, 95 y 99. También se usó un corte en el percentil 85, pero estrictamente como herramienta de diagnóstico para el chequeo de muestra chica de abajo, no como criterio de élite operativo; un borrador temprano de esta sección mezcló las dos cosas y se corrigió: el percentil 85 describe "bueno", no "élite" según el propio estándar del proyecto.

**Conteo binario de élite por rol:** en todos los umbrales probados, ningún jugador de la población calificada (n=2488) alcanza estatus de élite en los 4 roles simultáneamente. La forma más fuerte de la hipótesis no está respaldada. En el percentil 90, el techo real es 3 de 4 roles, alcanzado por 8 jugadores: Messi, Neymar, Hagi, Robinho, Flohe, Babington, Rivellino y Chislenko. Entre esos 8, Messi tiene por un margen amplio la muestra de carrera más grande (3054 minutos, 6 Mundiales, 34 partidos, contra un segundo lugar de 1225 minutos / 4 torneos de Neymar).

**Chequeo de la cola de muestra chica:** en el corte diagnóstico más laxo del percentil 85, tres jugadores llegan a 4 de 4 (Zidane, Cruyff, y Ermindo Onega, un respetado mediocampista ofensivo de Argentina 1966 confirmado como jugador real, no un error de datos, mediante fuentes web independientes). Los tres tienen muestras de carrera mucho más chicas (360-1109 minutos) que el promedio del grupo de 3+ roles (867 minutos) o que Messi (3054). A nivel poblacional, la correlación entre minutos de carrera y cantidad de roles de élite es débil (0.178), lo que va en contra de un sesgo sistemático fuerte de muestra chica en general, pero la cola extrema se comporta distinto al grueso de la distribución: con 900+ minutos, solo Zidane de los tres sobrevive; con 1500+, ninguno. Esto se reporta como una limitación real y abierta de los cortes de élite basados en percentil aplicados sin un piso de tamaño de muestra, no resuelta en ningún sentido.

**Promedio de puntaje de rol, agregado como métrica complementaria:** el conteo binario trata igual a "supera el umbral por mucho margen en 3 roles, falla el 4to por poco" que a "apenas supera el umbral en los 4, sin dominar en ninguno", lo cual pierde información real. El promedio simple de los cuatro puntajes de percentil resuelve esto sin depender de ningún corte. Con el umbral oficial de 270 minutos, Messi queda 2do (92.28), apenas detrás de Cruyff (93.34, toda su carrera mundialista en un solo torneo). Con 900+ minutos, Messi queda 1ro (por delante de Neymar y Hagi). Con 1500+ minutos, Messi sigue 1ro, muy por delante de Maradona en 2do lugar (89.24) y con una caída pronunciada hasta el tercer puesto después de eso.

**Maradona como rival genuino de muestra grande:** 2do por promedio de puntaje de rol entre jugadores de 900+ y 1500+ minutos, con la distancia a Messi (92.28 contra 89.24) explicada casi por completo por organizador de juego (84.06 contra 75.09), exactamente el rol que la Fase 4 predijo, antes de correr este notebook, como el punto relativamente más débil de Messi.

**Cristiano Ronaldo como caso de contraste:** una muestra de carrera casi idéntica a la de Messi (2206 minutos, 6 Mundiales, 27 partidos) produce el promedio de puntaje de rol más bajo de la tabla de síntesis (69.52), élite en solo 1 de 4 roles, explicado por un perfil marcadamente especializado (96.6 como finalizador, 37.1 como organizador). Esto es evidencia directa de que el hallazgo no es simplemente una función de jugar muchos Mundiales: Cristiano tuvo oportunidad y longevidad comparables, y no produjo un resultado multi-rol comparable.

**Principio interpretativo aplicado:** en línea con el principio interpretativo de arriba, nada de esto se enmarca como un concurso "Messi contra el resto". Messi comparte el techo observado de 3-de-4 con otros 7 jugadores y tiene un segundo lugar genuino, no elegido a conveniencia (Maradona), por promedio de puntaje. Ambos hechos se reportan junto al hallazgo central, no se tratan como algo que lo socave.

**Resultado:** `data/processed/role_scores.csv` actualizado con las columnas de conteo de élite en 3 umbrales y `role_score_avg`. La versión narrativa, con la tabla de síntesis completa entre jugadores de referencia y todo jugador que encabezó alguna vista de los datos, vive en `notebooks/05_multirole_elite_count.ipynb`.

## Fase 6: especialistas por rol para comunicación (completada)

A diferencia de las Fases 0-5, esta fase no produce evidencia para la pregunta central, produce un artefacto de comunicación: el pequeño conjunto de jugadores que se muestra en el radar chart (planteamiento del proyecto, sección 13), que ilustra la diferencia entre perfiles especializados y multidimensionales.

**Líderes estadísticos, con un piso de selección más exigente:** el líder por rol de la población (puntaje más alto en un solo rol, no el promedio) es dato, no opinión, pero elegir a quién mostrar como "el líder" en el material de comunicación usó un piso de 900 minutos, más exigente que la población analítica de 270 minutos. Esto fue necesario después de que el líder de organizador con 270 minutos resultara ser Isco (390 minutos), impulsado casi por completo por la actuación de España de mucho volumen y poco peligro en la eliminación en octavos de 2018 contra Rusia, un partido real, no un error de datos, pero un mal representante de "organizador de élite" para una pieza de comunicación. Con 900+ minutos, los cuatro líderes son David Villa (finalizador), Maradona (desequilibrante, sin cambios respecto al líder de 270 minutos), David Beckham (creador de juego), y Rodri (organizador), todos con perfiles reconocibles y defendibles.

**Pares de referencia, verificados contra sus propios datos antes de asignarlos:** dos jugadores de referencia agregados manualmente por rol, 8 en total: Xavi y Andrea Pirlo (organizador), Zidane y Cruyff (creador de juego), Neymar y Jairzinho (desequilibrante), Cristiano Ronaldo y Mbappé (finalizador). Ronaldinho se consideró inicialmente para el par de desequilibrante pero se descartó cuando sus propios cuatro puntajes mostraron a creador de juego (93.75), no desequilibrante (86.11), como su rol más alto, reemplazado por Jairzinho, cuyo puntaje de desequilibrante (98.99) es inequívocamente su propio pico de carrera. Esto sigue la regla del proyecto contra asignar a un jugador de referencia a un rol que sus propios datos contradicen.

**Resultado:** `data/processed/role_specialists.csv`, 12 filas, etiquetadas explícitamente como `statistical_leader` o `reference_addition`, listas para alimentar el radar chart de Tableau sin ambigüedad entre dato y decisión de comunicación. También queda en el notebook, como registro visual sin uso posterior, una tabla de referencia del top 10 por rol (tanto en 270 como en 900 minutos).

## Método de extracción

Se accede a SofaScore a través de su API interna (no existe una API pública oficial), usando la librería ScraperFC, que maneja la automatización de navegador para evitar la protección anti-bot. Esto se documenta explícitamente según las reglas de transparencia del proyecto: una API interna no es lo mismo que una API pública, estable y oficialmente soportada, y eso tiene implicaciones para la reproducibilidad (la estructura puede cambiar sin aviso) y para el rate limiting (las solicitudes no deben ser agresivas).

**Confirmado 2026-08-28:** durante la extracción completa 1966-2026, la API empezó a devolver `{'error': {'code': 403, 'reason': 'challenge'}}` (un desafío anti-bot tipo Cloudflare) después de aproximadamente 500 requests seguidas en unos 30-40 minutos. ScraperFC muestra esto como un simple `KeyError('event')`, confirmado al pedir directamente la respuesta cruda de un partido fallido en vez de confiar en el mensaje de error de la librería. El script de extracción ahora se frena solo (un período de espera después de varias fallas seguidas) en vez de tratar cada una como una falla independiente y no relacionada, porque una racha de fallas en partidos sin relación entre sí es este desafío, no un problema de datos específico de cada partido.

## Definición de población

**Rango de Mundiales (decidido 2026-08-27):** 1966-2026. SofaScore expone temporadas válidas desde 1930, pero la Fase 0 solo validó directamente datos detallados de eventos para 1986 y 2022. Se eligió 1966 como límite inferior de la población porque es la era a la que ya hace referencia el propio contenido histórico de SofaScore (comparaciones de Sofascore Rating), lo que da alguna señal independiente de cobertura antes de más spot-checks. Los partidos anteriores a 1966 quedan excluidos de la población por ahora, no porque se asuma que no tienen valor, sino porque todavía no hay evidencia en ningún sentido. Esto puede ampliarse después si spot-checks en torneos más antiguos lo respaldan.

**Alcance de posiciones:** la población se construye por rol funcional, no por posición nominal (ver "Roles funcionales" abajo), así que defensas y mediocampistas no quedan excluidos de entrada solo por estar etiquetados así. **Los arqueros quedan excluidos de la población base (decidido 2026-08-27):** los cuatro roles son estructuralmente ofensivos/de construcción de juego, y los números de pase o distribución de un arquero no son comparables de forma significativa a los de un organizador de campo. Es reversible si más adelante aparece una razón concreta para incluirlos.

**Umbral mínimo de minutos (decidido 2026-08-29): 270 minutos** (3 partidos completos). Elegido probando la media y la desviación estándar de goles per 90 en varios umbrales candidatos (1, 90, 180, ..., 900 minutos) sobre la población real, no elegido de antemano. La desviación estándar toca su mínimo justo en 270 minutos (0.199) y sube después (0.203 en 360, hasta 0.228 en 900), y la media empieza a subir en ese mismo punto (0.114 en 270, hasta 0.181 en 900). Por debajo de 270, domina el ruido de muestra chica (un solo gol temprano dispara una tasa per 90 absurda, el máximo de goles/90 cae de 9.00 con 1 minuto a 1.50 en 270). Por encima de 270, subir más el umbral deja de reducir ruido y en cambio introduce un sesgo de selección en la otra dirección, filtrando hacia jugadores que se quedaron en cancha específicamente porque rendían bien. 270 minutos también tiene una lectura futbolísticamente significativa: es una fase de grupos completa bajo el formato estándar (hoy extinto) de 32 equipos y 3 partidos, no un número redondo arbitrario. Deja 2488 de 5636 jugadores (44.1%).

**Nivel de agregación (decidido 2026-08-28):** la población se construye a nivel jugador-carrera, una fila por jugador sumando todos sus partidos de Mundial en todo el rango 1966-2026, no una fila por jugador-por-torneo. La pregunta central es sobre el perfil mundialista general de un jugador, no sobre una edición específica, y el nivel jugador-torneo dejaría que jugadores con muchos Mundiales aparezcan varias veces en la población, lo que convierte "¿en cuántos roles es élite este jugador?" en algo ambiguo, "¿élite en qué edición?". El detalle por torneo no se descarta, queda disponible como vista secundaria (por ejemplo, para mostrar consistencia en el tiempo), pero el conteo de élite multi-rol de la Fase 5 corre sobre la población a nivel de carrera.

**Totales vs. per 90 (decidido 2026-08-28):** se calculan y conservan ambos, a propósito, responden preguntas distintas y ninguno reemplaza al otro. Las métricas per 90 aíslan la tasa de producción controlando por tiempo jugado, y son las que alimentan el análisis de percentiles por rol, porque comparar totales crudos confundiría oportunidad con habilidad. Los totales (goles de carrera, minutos, partidos jugados, cantidad de Mundiales disputados, rondas alcanzadas) capturan algo que el per 90 no puede: durabilidad y selección sostenida a nivel competitivo durante años. Jugar muchos partidos de Mundial, y sobre todo avanzar lejos en la fase eliminatoria en varias ediciones distintas, requiere ser convocado y rendir lo suficientemente bien, de forma repetida, durante mucho tiempo, eso es un tipo de evidencia distinto, no "estadísticas infladas por tener más muestra". Esto se registra y reporta como una observación propia, explícita y etiquetada, separada del cálculo de élite por rol per 90 en vez de mezclada con él. El hecho (por ejemplo, "jugó N partidos de Mundial en 6 torneos a lo largo de 20 años") y la interpretación de qué significa ese hecho (una afirmación de durabilidad/excelencia) se mantienen visiblemente distintos, según la regla del proyecto de separar hallazgo de interpretación y de opinión. Esto aplica igual para cualquier jugador de la población que muestre el mismo patrón, no solo para Messi.

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

- Si "top 5" o un corte basado en percentil define el rango de "élite" por rol. Esto debe justificarse metodológicamente, no elegirse después de ver cuál favorece a Messi.
- Si las métricas de FBref y SofaScore se pueden combinar con seguridad dado que podrían definirse distinto.
- Si los Mundiales anteriores a 1966 se pueden agregar a la población más adelante, pendiente de más spot-checks.