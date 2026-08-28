"""
Follow-up check for the 1986 validation: is the fouls=NaN pattern seen for
Maradona and Burruchaga a 1986-specific data gap, or just how SofaScore's
API behaves for any match (fields only populated when at least one event
of that type was recorded)?

Pulls the same lineup stats for a known modern World Cup match and prints
the same fouls / wasFouled / duelWon / duelLost columns side by side with
the 1986 data already saved locally.

Run:
    python scripts/check_nan_pattern_modern_match.py
"""

import pandas as pd

import ScraperFC as sfc

# Argentina vs France, 2022 World Cup final. Well documented match, good
# contrast case: high foul count, well known individual performances.
MODERN_YEAR = "2022"
MODERN_TEAMS = {"Argentina", "France"}


def main():
    sofascore = sfc.Sofascore()
    matches = sofascore.get_match_dicts(MODERN_YEAR, "FIFA World Cup")

    target = None
    for match in matches:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        if {home, away} == MODERN_TEAMS and match["roundInfo"]["name"] == "Final":
            target = match
            break

    if target is None:
        print("Could not find the 2022 final in the match list.")
        return

    match_id = target["id"]
    print(f"Found {target['homeTeam']['name']} vs {target['awayTeam']['name']}, id={match_id}")

    df = sofascore.scrape_player_match_stats(match_id)
    df.to_csv("modern_2022_final_lineups_raw.csv", index=False)

    cols = ["name", "fouls", "wasFouled", "duelWon", "duelLost", "minutesPlayed"]
    print("\nPlayers who played at least 45 minutes:")
    played = df[df["minutesPlayed"].fillna(0) >= 45]
    print(played[cols].to_string(index=False))

    nan_fouls_but_played = played[played["fouls"].isna()]
    print(f"\n{len(nan_fouls_but_played)} of {len(played)} players who played "
          f"45+ minutes have fouls=NaN.")


if __name__ == "__main__":
    main()