"""
Full extraction run for the messi-outlier population: builds the match
manifest for every World Cup from 1966 to 2026, then extracts player
lineup stats for every match in it.

This is slow by design (a real browser hits SofaScore's API for every
match, with a delay in between to avoid hammering it) and safe to
interrupt: re-running it skips matches already saved.

ENV=production is set here, before importing botasaurus/ScraperFC,
because botasaurus's browser decorator pauses execution and waits for a
human to press Enter when a task inside it crashes, unless it thinks it's
running in production. That interactive pause is fine for someone
debugging one request by hand, but it silently blocks an unattended run
of hundreds of matches. Setting it as an env var, not just in this file,
is more robust (works regardless of import order), so this is also
documented as the recommended way to run it:

    ENV=production python scripts/run_extraction.py

Run:
    python scripts/run_extraction.py
"""

import os

os.environ.setdefault("ENV", "production")

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

import ScraperFC as sfc
from src.sofascore_extraction import build_match_manifest, extract_all_lineups

MANIFEST_PATH = Path("data/raw/matches_manifest.csv")
LINEUPS_DIR = Path("data/raw/lineups")
FAILURES_PATH = Path("data/raw/lineup_extraction_failures.csv")


def main():
    sofascore = sfc.Sofascore()

    if MANIFEST_PATH.exists():
        print(f"Manifest already exists at {MANIFEST_PATH}, loading it.")
        manifest = pd.read_csv(MANIFEST_PATH)
    else:
        print("Building match manifest for 1966-2026...")
        manifest = build_match_manifest(sofascore)
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        manifest.to_csv(MANIFEST_PATH, index=False)
        print(f"Saved manifest with {len(manifest)} matches to {MANIFEST_PATH}")

    print(f"\nExtracting player lineup stats for {len(manifest)} matches...")
    print("This will take a while, and it's safe to stop (Ctrl+C) and rerun later.")
    failures = extract_all_lineups(sofascore, manifest, LINEUPS_DIR)

    if len(failures) > 0:
        failures.to_csv(FAILURES_PATH, index=False)
        print(f"\n{len(failures)} matches failed. Saved to {FAILURES_PATH} for retry.")
    else:
        print("\nAll matches extracted with no failures.")


if __name__ == "__main__":
    main()