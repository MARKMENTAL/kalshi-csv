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
