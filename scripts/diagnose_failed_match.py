"""
Diagnostic: fetch the raw API response for a match that failed during
extraction, bypassing ScraperFC's get_match_dict (which assumes
response["event"] exists and throws a bare KeyError if it doesn't).
This is to see what SofaScore is actually returning: a real error message,
a rate-limit response, an empty dict, something else.

Run:
    python scripts/diagnose_failed_match.py
"""

from ScraperFC.utils.botasaurus_getters import botasaurus_browser_get_json

API_PREFIX = "https://api.sofascore.com/api/v1"

# One of the match ids that failed during extraction.
FAILED_MATCH_ID = 268528


def main():
    url = f"{API_PREFIX}/event/{FAILED_MATCH_ID}"
    print(f"Fetching {url} directly...\n")
    response = botasaurus_browser_get_json(url)
    print("Raw response:")
    print(response)


if __name__ == "__main__":
    main()
