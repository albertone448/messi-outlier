"""
Reusable SofaScore extraction functions for the World Cup population
(1966-2026). Kept here, not in scripts/, because both the manifest step
and the lineup extraction step are meant to be re-run and reused (e.g.
after the 2026 World Cup wraps up, or to retry failed matches), not
one-off validation checks.
"""

import time
from pathlib import Path

import pandas as pd

import ScraperFC as sfc

WORLD_CUP_YEARS = [
    "1966", "1970", "1974", "1978", "1982", "1986", "1990", "1994",
    "1998", "2002", "2006", "2010", "2014", "2018", "2022", "2026",
]


def build_match_manifest(sofascore: sfc.Sofascore, years: list[str] = WORLD_CUP_YEARS) -> pd.DataFrame:
    """Pull every match for each World Cup year and return one row per match.

    This only hits the API once per year (get_match_dicts), so it's cheap
    compared to the per-match lineup extraction.

    Round info isn't assumed to have a fixed shape: knockout matches expose
    a "name" (e.g. "Quarterfinals"), group-stage matches typically only
    expose a numeric "round" with no name or group label. Both are normal
    and handled here; only a match missing round info entirely gets logged.
    """
    rows = []
    for year in years:
        matches = sofascore.get_match_dicts(year, "FIFA World Cup")
        unlabeled_count = 0
        for match in matches:
            round_info = match.get("roundInfo", {})
            round_label = round_info.get("name") or round_info.get("group")
            if round_label is None:
                round_label = f"round_{round_info.get('round', 'unknown')}"
                unlabeled_count += 1
            if "round" not in round_info and round_label.endswith("unknown"):
                print(f"Match {match.get('id')} ({year}) has no round info at all: {round_info}")

            rows.append({
                "match_id": match["id"],
                "year": year,
                "round": round_label,
                "home_team": match["homeTeam"]["name"],
                "away_team": match["awayTeam"]["name"],
                "home_score": match["homeScore"].get("current"),
                "away_score": match["awayScore"].get("current"),
                "start_timestamp": match["startTimestamp"],
            })
        print(f"{year}: {len(matches)} matches ({unlabeled_count} group-stage matches "
              f"with numeric round only, as expected)")
    return pd.DataFrame(rows)


def extract_all_lineups(
    sofascore: sfc.Sofascore,
    manifest: pd.DataFrame,
    output_dir: Path,
    delay_seconds: float = 3.0,
    max_consecutive_failures: int = 3,
    cooldown_seconds: int = 600,
    max_attempts_per_match: int = 3,
) -> pd.DataFrame:
    """Extract player lineup stats for every match in the manifest.

    Resumable: skips any match_id that already has a saved CSV, so this
    can be stopped and restarted without re-fetching what's already done.

    SofaScore's internal API returns a 403 "challenge" response (Cloudflare
    style anti-bot check) after sustained request volume, confirmed by
    fetching a raw failed response directly: {'error': {'code': 403,
    'reason': 'challenge'}}. ScraperFC surfaces this as a bare
    KeyError('event') because it assumes response["event"] always exists.
    A run of consecutive failures across different, unrelated matches is
    the signature of this, as opposed to one specific match genuinely
    having a data problem. When `max_consecutive_failures` failures happen
    in a row, this backs off for `cooldown_seconds` instead of burning
    through the rest of the manifest logging failures, then keeps going.
    Each match gets up to `max_attempts_per_match` tries before it's
    recorded as failed and the run moves on, so one permanently broken
    match can't stall everything.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    failures = []
    consecutive_failures = 0

    for _, row in manifest.iterrows():
        match_id = row["match_id"]
        out_path = output_dir / f"{match_id}.csv"
        if out_path.exists():
            continue

        succeeded = False
        last_error = None

        for attempt in range(1, max_attempts_per_match + 1):
            try:
                lineup_df = sofascore.scrape_player_match_stats(match_id)
                lineup_df["match_id"] = match_id
                lineup_df["year"] = row["year"]
                lineup_df.to_csv(out_path, index=False)
                succeeded = True
                consecutive_failures = 0
                break
            except Exception as e:
                last_error = str(e)
                consecutive_failures += 1
                print(f"Failed match {match_id} ({row['year']}), attempt {attempt}: {e}")

                if consecutive_failures >= max_consecutive_failures:
                    print(f"{consecutive_failures} failures in a row, likely rate-limited "
                          f"or hit an anti-bot challenge. Cooling down for "
                          f"{cooldown_seconds}s before retrying...")
                    time.sleep(cooldown_seconds)
                    consecutive_failures = 0

        if not succeeded:
            failures.append({"match_id": match_id, "year": row["year"], "error": last_error})

        time.sleep(delay_seconds)

    return pd.DataFrame(failures)
