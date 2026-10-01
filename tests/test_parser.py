from datetime import datetime

import pytest

from kalshi_csv import KalshiCSV


def test_parse_returns_self(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    result = kalshi.parse()
    assert result is kalshi


def test_trade_count(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert kalshi.summary["trade_count"] == 3


def test_total_fees(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert abs(kalshi.summary["total_fees"] - 0.07) < 1e-6


def test_total_pnl_without_fees(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert abs(kalshi.summary["total_pnl_without_fees"] - (-0.20)) < 1e-6


def test_total_pnl_with_fees(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert abs(kalshi.summary["total_pnl_with_fees"] - (-0.27)) < 1e-6


def test_total_tax_basis(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert abs(kalshi.summary["total_tax_basis"] - 1.64) < 1e-6


def test_total_tax_proceeds(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert abs(kalshi.summary["total_tax_proceeds"] - 1.37) < 1e-6


def test_trades_list_length(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert len(kalshi.trades) == 3


def test_first_trade_data(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    trade = kalshi.trades[0]
    assert trade["ticker"] == "TESTMARKET-WIN"
    assert trade["side"] == "YES"
    assert trade["qty"] == 1.0
    assert trade["entry"] == 0.50
    assert trade["exit"] == 1.00
    assert abs(trade["pnl_no_fees"] - 0.50) < 1e-6
    assert abs(trade["pnl_with_fees"] - 0.47) < 1e-6


def test_irs_summary(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    irs = kalshi.irs_summary()
    assert irs["box"] == "C"
    assert irs["description"] == "Kalshi Event Contracts (Aggregate Summary)"
    assert irs["date_acquired"] == "07/07/2026"
    assert irs["date_sold"] == "07/07/2026"
    assert abs(irs["gross_proceeds"] - 1.37) < 1e-6
    assert abs(irs["cost_basis"] - 1.64) < 1e-6
    assert abs(irs["gain_or_loss"] - (-0.27)) < 1e-6


def test_date_tracking(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert kalshi.summary["earliest_open_date"] is not None
    assert kalshi.summary["latest_close_date"] is not None
    assert kalshi.summary["earliest_open_date"].strftime("%m/%d/%Y") == "07/07/2026"
    assert kalshi.summary["latest_close_date"].strftime("%m/%d/%Y") == "07/07/2026"


def test_file_not_found():
    kalshi = KalshiCSV("/nonexistent/path.csv")
    with pytest.raises(FileNotFoundError):
        kalshi.parse()


def test_market_breakdown_returns_list(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    breakdown = kalshi.market_breakdown()
    assert isinstance(breakdown, list)
    assert len(breakdown) > 0


def test_market_breakdown_structure(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    breakdown = kalshi.market_breakdown()
    for item in breakdown:
        assert "category" in item
        assert "trades" in item
        assert "win_rate" in item
        assert "net_pnl" in item


def test_market_breakdown_sorted_by_trades(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    breakdown = kalshi.market_breakdown()
    trade_counts = [item["trades"] for item in breakdown]
    assert trade_counts == sorted(trade_counts, reverse=True)


def test_sp500_price_tier_breakdown_groups_entry_prices_and_excludes_other_markets():
    kalshi = KalshiCSV("unused.csv")
    entries_and_pnls = [
        (0.399, 1.0),
        (0.40, -0.5),
        (0.4001, -0.25),
        (0.69, 0.0),
        (0.70, 2.0),
        (0.7001, -1.0),
        (0.85, 3.0),
        (0.8501, -2.0),
        (1.00, 4.0),
        (-0.01, 100.0),
        (1.01, 100.0),
    ]
    kalshi.trades = [
        {
            "entry": entry,
            "pnl_with_fees": pnl,
            "market_category": "S&P 500 (INXU Intraday)",
        }
        for entry, pnl in entries_and_pnls
    ]
    kalshi.trades.append({
        "entry": 0.50,
        "pnl_with_fees": 100.0,
        "market_category": "Other Markets",
    })

    breakdown = kalshi.sp500_price_tier_breakdown()

    assert [item["price_tier"] for item in breakdown] == [
        "<=$0.40 (Out-of-the-Money Speculative)",
        ">$0.40-$0.70 (At-the-Money / Coincident)",
        ">$0.70-$0.85 (Likely / Moderate ITM)",
        ">$0.85 (Deep ITM / High Probability)",
    ]
    assert [item["trades"] for item in breakdown] == [2, 3, 2, 2]
    assert [item["win_rate"] for item in breakdown] == pytest.approx([50.0, 100 / 3, 50.0, 50.0])
    assert [item["average_win"] for item in breakdown] == [1.0, 2.0, 3.0, 4.0]
    assert [item["average_loss"] for item in breakdown] == [-0.5, -0.25, -1.0, -2.0]
    assert [item["net_pnl"] for item in breakdown] == [0.5, 1.75, 2.0, 2.0]


def test_sp500_price_tier_breakdown_is_empty_without_sp500_trades():
    kalshi = KalshiCSV("unused.csv")
    kalshi.trades = [{
        "entry": 0.50,
        "pnl_with_fees": 1.0,
        "market_category": "Other Markets",
    }]

    assert kalshi.sp500_price_tier_breakdown() == []


def test_parse_sp500_ticker_extracts_strike_and_cutoff():
    from kalshi_csv.parser import KalshiCSV

    parsed = KalshiCSV._parse_sp500_ticker("KXINXU-26SEP24H1300-T7659")

    assert parsed == {
        "target_date": datetime(2026, 9, 24).date(),
        "cutoff_hour": 13,
        "strike": 7659.0,
    }
    assert KalshiCSV._parse_sp500_ticker("INVALID") is None


def test_parse_sp500_ticker_accepts_decimal_strike():
    from kalshi_csv.parser import KalshiCSV

    parsed = KalshiCSV._parse_sp500_ticker("KXINXU-26SEP30H1500-T7684.9999")

    assert parsed == {
        "target_date": datetime(2026, 9, 30).date(),
        "cutoff_hour": 15,
        "strike": 7684.9999,
    }


def test_sp500_hourly_performance_groups_by_contract_target_hour(monkeypatch):
    monkeypatch.setattr(KalshiCSV, "_sp500_market_context", lambda self, trades: None)
    kalshi = KalshiCSV("unused.csv")
    trades = []

    def add_trade(entry, pnl, timestamp, target_hour, category="S&P 500 (INXU Intraday)"):
        trades.append({
            "entry": entry,
            "exit": entry,
            "side": "YES",
            "pnl_with_fees": pnl,
            "market_category": category,
            "ticker": "KXINXU-26JUL07H{:02d}00-T7615".format(target_hour),
            "open_timestamp": datetime.fromisoformat(timestamp) if timestamp else None,
        })

    # Different trade-entry times share the same contract target hour.
    for pnl, timestamp in zip(
        (1.0, 1.0, 0.0, -1.0, -1.0),
        (
            "2026-07-07T12:49:00-04:00",
            "2026-07-07T12:31:00-04:00",
            "2026-07-07T11:15:00-04:00",
            "2026-07-07T12:05:00-04:00",
            "2026-07-07T12:55:00-04:00",
        ),
    ):
        add_trade(0.40, pnl, timestamp, 13)
    # The same trade-entry hour but a different ticker target remains separate.
    for pnl in (1.0, 1.0, 1.0, 1.0, -1.0):
        add_trade(0.40, pnl, "2026-07-07T12:49:00-04:00", 14)
    # High win rate with only four trades does not qualify for a suggestion.
    for _ in range(4):
        add_trade(0.41, 1.0, "2026-07-07T12:49:00-04:00", 13)
    add_trade(0.50, 1.0, "2026-07-07T12:49:00-04:00", 13, "Other Markets")
    kalshi.trades = trades

    breakdown = kalshi.sp500_hourly_performance()

    assert len(breakdown) == 3
    first_tier = [item for item in breakdown if item["price_tier"].startswith("<=")]
    assert [item["target_hour"] for item in first_tier] == [
        "13:00 ET",
        "14:00 ET",
    ]
    assert [item["trades"] for item in first_tier] == [5, 5]
    assert [item["win_rate"] for item in first_tier] == [40.0, 80.0]
    assert first_tier[0]["pushes"] == 1
    assert first_tier[0]["net_pnl"] == pytest.approx(0.0)
    assert first_tier[0]["recommended"] is False
    assert first_tier[1]["recommended"] is True
    assert first_tier[1]["avg_sp500_open"] is None
    assert first_tier[1]["avg_sp500_close"] is None
    second_tier = [item for item in breakdown if item["price_tier"].startswith(">")]
    assert second_tier[0]["trades"] == 4
    assert second_tier[0]["win_rate"] == 100.0
    assert second_tier[0]["recommended"] is False


def test_sp500_market_context_compares_prices_to_strike(monkeypatch):
    import pandas as pd
    from kalshi_csv.parser import KalshiCSV

    idx = pd.to_datetime([
        "2026-07-07 09:00:00+00:00",
        "2026-07-07 10:00:00+00:00",
        "2026-07-07 13:00:00+00:00",
        "2026-07-07 14:00:00+00:00",
    ])
    prices = pd.Series([7600.0, 7610.0, 7620.0, 7630.0], index=idx)
    monkeypatch.setattr(KalshiCSV, "_fetch_sp500_prices", lambda self, s, e: prices)

    trades = [{
        "ticker": "KXINXU-26JUL26H1600-T7615",
        "open_timestamp": datetime.fromisoformat("2026-07-07T09:15:00-04:00"),
        "close_timestamp": datetime.fromisoformat("2026-07-07T13:15:00-04:00"),
    } for _ in range(5)]

    ctx = KalshiCSV("unused.csv")._sp500_market_context(trades)

    assert ctx["available"] is True
    assert ctx["strike"] == 7615.0
    assert ctx["avg_open"] == 7620.0
    assert ctx["avg_close"] == 7630.0
    assert ctx["open_above"] is True
    assert ctx["close_above"] is True
    assert ctx["move"] == 10.0
    assert ctx["cutoff_above"] is True


def test_sp500_top_trades_returns_winners_sorted_by_pnl():
    from kalshi_csv.parser import KalshiCSV

    trades = [
        {"ticker": "KXINXU-26JUL26H1600-T7615", "side": "YES", "entry": 0.50, "exit": 1.00, "pnl_with_fees": 1.00, "open_timestamp": datetime.fromisoformat("2026-07-07T09:15:00-04:00")},
        {"ticker": "KXINXU-26JUL26H1600-T7615", "side": "NO", "entry": 0.60, "exit": 0.00, "pnl_with_fees": 3.00, "open_timestamp": datetime.fromisoformat("2026-07-07T10:15:00-04:00")},
        {"ticker": "KXINXU-26JUL26H1600-T7615", "side": "YES", "entry": 0.70, "exit": 0.00, "pnl_with_fees": -1.00, "open_timestamp": datetime.fromisoformat("2026-07-07T11:15:00-04:00")},
        {"ticker": "KXINXU-26JUL26H1600-T7615", "side": "NO", "entry": 0.80, "exit": 1.00, "pnl_with_fees": 2.00, "open_timestamp": datetime.fromisoformat("2026-07-07T12:15:00-04:00")},
    ]

    top = KalshiCSV._sp500_top_trades(trades)

    assert len(top) == 3
    assert top[0]["pnl"] == 3.00
    assert top[1]["pnl"] == 2.00
    assert top[2]["pnl"] == 1.00
    assert top[0]["open_time_et"] == "Jul 07, 2026 10:15 AM ET"
    assert all(t["pnl"] > 0 for t in top)


def test_sp500_hourly_performance_selects_top_five_profitable_global_suggestions(monkeypatch):
    monkeypatch.setattr(KalshiCSV, "_sp500_market_context", lambda self, trades: None)
    kalshi = KalshiCSV("unused.csv")
    trades = []

    def add_group(entry, hour, pnls):
        for pnl in pnls:
            trades.append({
                "entry": entry,
                "exit": entry,
                "side": "YES",
                "pnl_with_fees": pnl,
                "market_category": "S&P 500 (INXU Intraday)",
                "ticker": "KXINXU-26JUL07H{:02d}00-T7615".format(hour),
                "open_timestamp": datetime.fromisoformat(
                    "2026-07-07T{:02d}:15:00-04:00".format(hour)
                ),
            })

    # Highest win rate, but a net loss: this group must not be suggested.
    add_group(0.40, 9, (1.0, 1.0, 1.0, 1.0, -10.0))
    # Same win rate, different profits: the larger net P&L wins the tie.
    add_group(0.50, 10, (2.0, 2.0, 2.0, -0.1, -0.1))
    add_group(0.80, 11, (3.0, 3.0, 3.0, -0.1, -0.1))
    # Higher total profit but lower win rate: win rate has priority.
    add_group(0.90, 12, (10.0, 10.0, -0.1, -0.1, -0.1))
    # Additional qualifying groups to verify top-5 selection.
    add_group(0.40, 13, (1.0, 1.0, 1.0, 1.0, 1.0))
    add_group(0.50, 14, (1.0, 1.0, 1.0, 1.0, -0.1))
    add_group(0.80, 15, (1.0, 1.0, 1.0, -0.1, -0.1))
    kalshi.trades = trades

    breakdown = kalshi.sp500_hourly_performance()
    suggestions = [item for item in breakdown if item["recommended"]]

    assert len(suggestions) == 5
    # Suggestions are in breakdown order (tier, then hour), not ranking order.
    assert suggestions[0]["price_tier"].startswith("<=")
    assert suggestions[0]["target_hour"] == "13:00 ET"
    assert suggestions[0]["win_rate"] == 100.0
    assert suggestions[0]["net_pnl"] == pytest.approx(5.0)
    assert suggestions[1]["price_tier"].startswith(">$0.40")
    assert suggestions[1]["target_hour"] == "10:00 ET"
    assert suggestions[1]["win_rate"] == 60.0
    assert suggestions[1]["net_pnl"] == pytest.approx(5.8)
    assert suggestions[2]["price_tier"].startswith(">$0.40")
    assert suggestions[2]["target_hour"] == "14:00 ET"
    assert suggestions[2]["win_rate"] == 80.0
    assert suggestions[2]["net_pnl"] == pytest.approx(3.9)
    assert suggestions[3]["price_tier"].startswith(">$0.70")
    assert suggestions[3]["target_hour"] == "11:00 ET"
    assert suggestions[3]["win_rate"] == 60.0
    assert suggestions[3]["net_pnl"] == pytest.approx(8.8)
    assert suggestions[4]["price_tier"].startswith(">$0.70")
    assert suggestions[4]["target_hour"] == "15:00 ET"
    assert suggestions[4]["win_rate"] == 60.0
    assert suggestions[4]["net_pnl"] == pytest.approx(2.8)
    assert len(suggestions[0]["top_trades"]) == 3
    assert [trade["pnl"] for trade in suggestions[0]["top_trades"]] == [1.0, 1.0, 1.0]
    assert all(trade["pnl"] > 0 for setup in suggestions for trade in setup["top_trades"])
    assert all("_trades" not in setup for setup in breakdown)


def test_sp500_hourly_performance_has_no_suggestion_for_nonpositive_net_pnl(monkeypatch):
    monkeypatch.setattr(KalshiCSV, "_sp500_market_context", lambda self, trades: None)
    kalshi = KalshiCSV("unused.csv")
    kalshi.trades = [{
        "entry": 0.50,
        "pnl_with_fees": -0.1,
        "market_category": "S&P 500 (INXU Intraday)",
        "ticker": "KXINXU-26JUL07H1600-T7615",
        "open_timestamp": datetime.fromisoformat("2026-07-07T09:15:00-04:00"),
    } for _ in range(5)]

    breakdown = kalshi.sp500_hourly_performance()

    assert len(breakdown) == 1
    assert breakdown[0]["recommended"] is False


def test_recent_closed_positions_returns_list(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    positions = kalshi.recent_closed_positions()
    assert isinstance(positions, list)


def test_recent_closed_positions_limit(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    positions = kalshi.recent_closed_positions(n=2)
    assert len(positions) <= 2


def test_recent_closed_positions_sorted_by_date(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    positions = kalshi.recent_closed_positions()
    if len(positions) > 1:
        timestamps = [p["close_timestamp"] for p in positions]
        assert timestamps == sorted(timestamps, reverse=True)


def test_summary_tracks_wins_losses_pushes(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert kalshi.summary["wins"] >= 0
    assert kalshi.summary["losses"] >= 0
    assert kalshi.summary["pushes"] >= 0
    assert kalshi.summary["wins"] + kalshi.summary["losses"] + kalshi.summary["pushes"] == kalshi.summary["trade_count"]


def test_summary_tracks_best_worst_trade(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    assert kalshi.summary["best_trade"] is not None
    assert kalshi.summary["worst_trade"] is not None
    assert "pnl_with_fees" in kalshi.summary["best_trade"]
    assert "pnl_with_fees" in kalshi.summary["worst_trade"]
    assert kalshi.summary["best_trade"]["pnl_with_fees"] >= kalshi.summary["worst_trade"]["pnl_with_fees"]


def test_trade_has_market_category(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    for trade in kalshi.trades:
        assert "market_category" in trade
        assert isinstance(trade["market_category"], str)


def test_trade_has_timestamps(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    for trade in kalshi.trades:
        assert "open_timestamp" in trade
        assert "close_timestamp" in trade
