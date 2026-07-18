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
    assert abs(irs["gross_proceeds"] - 1.37) < 1e-6
    assert abs(irs["cost_basis"] - 1.64) < 1e-6
    assert abs(irs["gain_or_loss"] - (-0.27)) < 1e-6


def test_file_not_found():
    kalshi = KalshiCSV("/nonexistent/path.csv")
    with pytest.raises(FileNotFoundError):
        kalshi.parse()
