from kalshi_csv.categories import categorize_ticker


def test_mlb_categorization():
    assert categorize_ticker("KXMLBGAME-26JUL081940BOSCWS-BOS") == "MLB Baseball"
    assert categorize_ticker("KXMLBHRDERBY-26-KSCHWARBER12") == "MLB Baseball"


def test_npb_categorization():
    assert categorize_ticker("KXNPBGAME-26JUL150500YOMYAK-YAK") == "NPB Baseball (Japan)"


def test_nba_summer_categorization():
    assert categorize_ticker("KXNBASUMMERGAME-26JUL14MEMGSW-GSW") == "NBA Summer League"


def test_wnba_categorization():
    assert categorize_ticker("KXWNBAGAME-26JUL13PHXMIN-PHX") == "WNBA Basketball"


def test_sp500_categorization():
    assert categorize_ticker("KXINXU-26JUL08H1400-T7479.9999") == "S&P 500 (INXU Intraday)"
    assert categorize_ticker("KXINX-26JUL08H1400-T7479.9999") == "S&P 500 (INXU Intraday)"


def test_multivariate_events_categorization():
    assert categorize_ticker("KXMVESPORTSMULTIGAMEEXTENDED-S2026769CE3FA3F9-6D4DB2E2128") == "Multivariate Events"
    assert categorize_ticker("KXMVECROSSCATEGORY-S2026AC77F3A8C7A-6D4DB2E2128") == "Multivariate Events"


def test_soccer_categorization():
    assert categorize_ticker("KXWCADVANCE-26JUL07ARGEGY-ARG") == "Global Soccer / Football"
    assert categorize_ticker("KXUCLADVANCE-26JUL14KUPSVAR-VAR") == "Global Soccer / Football"
    assert categorize_ticker("KXBRASILEIROBGAME-26JUL13AMGLON-LON") == "Global Soccer / Football"
    assert categorize_ticker("KXECULPGAME-26JUL14MACMUR-MUR") == "Global Soccer / Football"
    assert categorize_ticker("KXALLSVENSKANGAME-26JUL12BROSIR-SIR") == "Global Soccer / Football"
    assert categorize_ticker("KXCLUBFGAME-26JUL27GALVEN-VEN") == "Global Soccer / Football"


def test_other_markets_categorization():
    assert categorize_ticker("KXRAIN-26JUL15-ATL") == "Other Markets"
    assert categorize_ticker("KXTRUMPMENTION-26JUL15") == "Other Markets"
    assert categorize_ticker("KXTEMPNYCH-26JUL15") == "Other Markets"
    assert categorize_ticker("KXHIGHCHI-26JUL15") == "Other Markets"


def test_unknown_ticker_defaults_to_other():
    assert categorize_ticker("UNKNOWN-TICKER-123") == "Other Markets"
