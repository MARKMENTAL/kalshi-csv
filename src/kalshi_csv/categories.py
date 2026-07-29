TICKER_CATEGORY_MAP = {
    "KXMLB": "MLB Baseball",
    "KXMLBHR": "MLB Baseball",
    "KXMLBMEN": "MLB Baseball",
    "KXNPB": "NPB Baseball (Japan)",
    "KXNBASUMMER": "NBA Summer League",
    "KXNEXTTEAMNBA": "NBA Summer League",
    "KXWNBA": "WNBA Basketball",
    "KXINXU": "S&P 500 (INXU Intraday)",
    "KXINX": "S&P 500 (INXU Intraday)",
    "KXMVE": "Multivariate Events",
}

SOCCER_PREFIXES = [
    "KXWC",
    "KXUCL",
    "KXUECL",
    "KXBRASILEIRO",
    "KXALLSVENSKAN",
    "KXELITESERIEN",
    "KXECULP",
    "KXLIGAMX",
    "KXLIGAEXP",
    "KXKLEAGUE",
    "KXCLUBF",
    "KXSCOCUP",
    "KXURYPD",
    "KXDIMAYOR",
    "KXARGPREM",
    "KXBOLP",
]


def categorize_ticker(ticker):
    """Maps a Kalshi market ticker to a human-readable category."""
    for prefix, category in TICKER_CATEGORY_MAP.items():
        if ticker.startswith(prefix):
            return category

    for prefix in SOCCER_PREFIXES:
        if ticker.startswith(prefix):
            return "Global Soccer / Football"

    return "Other Markets"
