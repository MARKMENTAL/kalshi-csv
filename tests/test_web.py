from kalshi_csv import KalshiCSV
from kalshi_csv.web import render_portfolio_html


def test_render_html_contains_header(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "KALSHI DERIVATIVES / ACCOUNT AUDIT" in html_content
    assert "Year-End Performance Summary" in html_content


def test_render_html_contains_summary_metrics(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "NET REALIZED P&amp;L" in html_content
    assert "WIN / LOSS RECORD" in html_content
    assert "TOTAL VOLUME" in html_content
    assert "BEST/WORST SINGLE" in html_content


def test_render_html_contains_market_breakdown(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "Market Breakdown" in html_content
    assert "ASSET CLASS / MARKET" in html_content
    assert "TRADES" in html_content
    assert "WIN RATE" in html_content


def test_render_html_contains_recent_positions(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "Recent Closed Positions" in html_content
    assert "DATE/TIME" in html_content
    assert "TICKER" in html_content
    assert "SIDE" in html_content
    assert "ENTRY" in html_content
    assert "EXIT" in html_content


def test_render_html_contains_trade_data(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "TESTMARKET-WIN" in html_content
    assert "TESTMARKET-LOSS" in html_content
    assert "TESTMARKET-SMALL" in html_content


def test_render_html_html401_doctype(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"' in html_content


def test_render_html_no_css(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "<style" not in html_content
    assert "style=" not in html_content


def test_render_html_shows_win_loss_record(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "2 - 1" in html_content


def test_render_html_shows_total_volume(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert ">3<" in html_content


def test_render_html_shows_csv_filename(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "my-kalshi-data.csv")
    assert "my-kalshi-data.csv" in html_content


def test_render_html_escapes_html_in_tickers(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    kalshi.trades[0]["ticker"] = "<script>alert('xss')</script>"
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "<script>alert('xss')</script>" not in html_content
    assert "&lt;script&gt;" in html_content
