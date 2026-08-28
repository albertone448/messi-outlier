"""
Validation test for messi-outlier: check whether SofaScore has detailed
match-level data for the 1986 World Cup, using the Argentina vs England
quarter-final (Maradona's "Hand of God" / "Goal of the Century" match)
as the test case.

This does NOT assume the data exists. It queries the real API and prints
what comes back, including empty/error responses, so we can see the
actual level of detail (or lack of it) before deciding how Maradona
participates in the analysis.

Requirements:
    pip install ScraperFC --break-system-packages
    Google Chrome installed locally (ScraperFC drives a real browser
    under the hood to get past SofaScore's anti-bot protection).

Run:
    python validate_maradona_1986.py
"""

import json

import ScraperFC as sfc

WORLD_CUP = "FIFA World Cup"
TARGET_YEAR = "1986"
TARGET_TEAMS = {"Argentina", "England"}


def find_1986_match(sofascore: sfc.Sofascore) -> dict | None:
    valid_seasons = sofascore.get_valid_seasons(WORLD_CUP)
    print(f"Valid SofaScore seasons found for '{WORLD_CUP}':")
    print(sorted(valid_seasons.keys()))

    if TARGET_YEAR not in valid_seasons:
        print(f"\n'{TARGET_YEAR}' is NOT among the seasons SofaScore exposes "
              f"for the World Cup. Stopping here, this alone is a finding.")
        return None

    matches = sofascore.get_match_dicts(TARGET_YEAR, WORLD_CUP)
    print(f"\n{len(matches)} matches found for the {TARGET_YEAR} World Cup.")

    for match in matches:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        if {home, away} == TARGET_TEAMS:
            print(f"\nFound target match: {home} vs {away}, id={match['id']}")
            return match

    print(f"\nCould not find a {' vs '.join(TARGET_TEAMS)} match in the "
          f"{TARGET_YEAR} World Cup match list.")
    return None


def main():
    sofascore = sfc.Sofascore()
    match = find_1986_match(sofascore)

    if match is None:
        return

    match_id = match["id"]
    result = {"match_dict": match}

    print("\nPulling player lineup stats (Maradona's raw fields live here)...")
    try:
        lineups_df = sofascore.scrape_player_match_stats(match_id)
        result["lineup_columns"] = list(lineups_df.columns)
        maradona_row = lineups_df[
            lineups_df["name"].str.contains("Maradona", case=False, na=False)
        ]
        result["maradona_stats"] = maradona_row.to_dict(orient="records")
        lineups_df.to_csv("maradona_1986_lineups_raw.csv", index=False)
        print("Saved full lineup stats to maradona_1986_lineups_raw.csv")
    except Exception as e:
        result["lineup_error"] = str(e)
        print(f"Lineup stats failed: {e}")

    print("\nPulling shot map...")
    try:
        shots_df = sofascore.scrape_match_shots(match_id)
        result["shotmap_columns"] = list(shots_df.columns)
        shots_df.to_csv("maradona_1986_shots_raw.csv", index=False)
        print("Saved shot map to maradona_1986_shots_raw.csv")
    except Exception as e:
        result["shotmap_error"] = str(e)
        print(f"Shot map failed: {e}")

    print("\nPulling heatmaps (this can be slow, one request per player)...")
    try:
        heatmaps = sofascore.scrape_heatmaps(match_id)
        maradona_heatmap = {
            name: data for name, data in heatmaps.items()
            if "Maradona" in name
        }
        result["maradona_heatmap_points"] = {
            name: len(data["heatmap"]) for name, data in maradona_heatmap.items()
        }
    except Exception as e:
        result["heatmap_error"] = str(e)
        print(f"Heatmaps failed: {e}")

    with open("maradona_1986_validation_summary.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    print("\nDone. Summary saved to maradona_1986_validation_summary.json")
    print("Send back that file (or paste its contents) so we can look at it together.")


if __name__ == "__main__":
    main()
