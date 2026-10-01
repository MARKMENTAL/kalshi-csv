import json
import threading
from http.server import HTTPServer
from pathlib import Path
from urllib.request import urlopen

from kalshi_csv import KalshiCSV
from kalshi_csv.web import ModernWebHandler, render_modern_dashboard_html, render_portfolio_html


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


def test_render_html_contains_sp500_price_tier_breakdown(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    kalshi.trades[0]["market_category"] = "S&P 500 (INXU Intraday)"
    kalshi.trades[0]["entry"] = 0.20

    html_content = render_portfolio_html(kalshi, "test.csv")

    assert "S&amp;P 500 Contract Performance by Entry Price Tier" in html_content
    assert "&lt;=$0.40 (Out-of-the-Money Speculative)" in html_content
    assert "ENTRY PRICE TIER" in html_content
    assert "AVERAGE WIN" in html_content
    assert "AVERAGE LOSS" in html_content
    assert "TOTAL NET P&amp;L" in html_content
    assert "+$0.47" in html_content
    assert "N/A" in html_content


def test_render_html_omits_sp500_price_tiers_without_sp500_trades(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()

    html_content = render_portfolio_html(kalshi, "test.csv")

    assert "S&amp;P 500 Contract Performance by Entry Price Tier" not in html_content


def test_modern_dashboard_includes_all_trades_and_interactive_controls(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()

    html_content = render_modern_dashboard_html(kalshi, "test.csv")

    assert "<!doctype html>" in html_content
    assert "TESTMARKET-WIN" in html_content
    assert "TESTMARKET-LOSS" in html_content
    assert "TESTMARKET-SMALL" in html_content
    assert "dashboard.js" in html_content
    assert "alpine.min.js" in html_content
    assert "x-model=\"search\"" in html_content
    assert "S&amp;P 500 price tiers" in html_content
    assert "S&amp;P 500 top hourly setups" in html_content
    assert "CONTRACT TARGET HOUR" in html_content
    assert "Show top 5 historical setups" in html_content
    assert "No historical setup meets the minimum sample" in html_content
    assert "This historical summary is not a forecast" in html_content
    assert "AVG S&amp;P OPEN" in html_content
    assert "AVG S&amp;P CLOSE" in html_content
    assert "Show top winning trades" in html_content
    assert "Hide top winning trades" in html_content
    assert "sp500_hourly" in html_content


def test_modern_dashboard_serializes_hourly_sp500_performance(sample_csv, monkeypatch):
    from kalshi_csv import parser as parser_module

    monkeypatch.setattr(
        parser_module.KalshiCSV,
        "_sp500_market_context",
        lambda self, trades: None,
    )
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    kalshi.trades[0]["market_category"] = "S&P 500 (INXU Intraday)"
    kalshi.trades[0]["ticker"] = "KXINXU-26JUL07H1300-T7615"

    html_content = render_modern_dashboard_html(kalshi, "test.csv")
    data_block = html_content.split(
        '<script id="dashboard-data" type="application/json">', 1
    )[1].split("</script>", 1)[0]
    payload = json.loads(data_block)

    assert payload["sp500_hourly"] == [{
        "price_tier": ">$0.40-$0.70 (At-the-Money / Coincident)",
        "hour": 13,
        "trades": 1,
        "wins": 1,
        "losses": 0,
        "pushes": 0,
        "net_pnl": 0.47,
        "win_rate": 100.0,
        "average_pnl": 0.47,
        "target_hour": "13:00 ET",
        "recommended": False,
        "market_context": None,
        "avg_sp500_open": None,
        "avg_sp500_close": None,
    }]


def test_modern_dashboard_serializes_top_winning_suggestion_trades(sample_csv, monkeypatch):
    from kalshi_csv import parser as parser_module

    monkeypatch.setattr(
        parser_module.KalshiCSV,
        "_sp500_market_context",
        lambda self, trades: None,
    )
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    base_trade = dict(kalshi.trades[0])
    base_trade["market_category"] = "S&P 500 (INXU Intraday)"
    base_trade["ticker"] = "KXINXU-26JUL07H1600-T7615"
    base_trade["side"] = "YES"
    base_trade["entry"] = 0.50
    base_trade["exit"] = 1.0
    kalshi.trades = [
        dict(base_trade, pnl_with_fees=pnl)
        for pnl in (0.2, 0.5, 0.3, 0.4, 0.1)
    ]

    html_content = render_modern_dashboard_html(kalshi, "test.csv")
    data_block = html_content.split(
        '<script id="dashboard-data" type="application/json">', 1
    )[1].split("</script>", 1)[0]
    payload = json.loads(data_block)
    suggestion = next(item for item in payload["sp500_hourly"] if item["recommended"])

    assert [trade["pnl"] for trade in suggestion["top_trades"]] == [0.5, 0.4, 0.3]
    assert suggestion["top_trades"][0]["open_time_et"] == "Jul 07, 2026 09:48 AM ET"
    assert all(trade["pnl"] > 0 for trade in suggestion["top_trades"])
    assert "_trades" not in suggestion


def test_modern_dashboard_escapes_csv_values_inside_json_data(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    kalshi.trades[0]["ticker"] = "</script><script>alert('xss')</script>"

    html_content = render_modern_dashboard_html(kalshi, "test.csv")

    assert "</script><script>alert('xss')" not in html_content
    assert "\\u003c/script\\u003e" in html_content


def test_modern_theme_registry_contains_complete_palettes():
    theme_path = Path(__file__).parents[1] / "src" / "kalshi_csv" / "themes.json"
    themes = json.loads(theme_path.read_text(encoding="utf-8"))

    assert len(themes) == 40
    assert "Nord" in {theme["name"] for theme in themes}
    assert all(len(theme["ansi_normal"]) == 8 for theme in themes)
    assert all(len(theme["ansi_bright"]) == 8 for theme in themes)
    assert all(theme["fg"].startswith("#") and theme["bg"].startswith("#") for theme in themes)


def test_modern_web_handler_serves_page_and_local_assets(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    server = HTTPServer(("127.0.0.1", 0), ModernWebHandler)
    server.html_content = render_modern_dashboard_html(kalshi, "test.csv")
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    base_url = "http://127.0.0.1:{}".format(server.server_address[1])

    try:
        with urlopen(base_url + "/") as response:
            page = response.read().decode("utf-8")
            assert response.headers.get_content_type() == "text/html"
            assert "Portfolio <span>dashboard</span>" in page

        with urlopen(base_url + "/static/modern.css") as response:
            css = response.read().decode("utf-8")
            assert response.headers.get_content_type() == "text/css"
            assert "--app-bg" in css

        with urlopen(base_url + "/static/alpine.min.js") as response:
            alpine = response.read()
            assert response.headers.get_content_type() == "application/javascript"
            assert len(alpine) > 40_000

        with urlopen(base_url + "/static/ALPINE-LICENSE.md") as response:
            assert b"MIT License" in response.read()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


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


def test_render_html_contains_irs_section(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert "IRS Form 8949 / Schedule D Summary" in html_content
    assert "Box to Check:" in html_content
    assert "Description:" in html_content
    assert "Date Acquired:" in html_content
    assert "Date Sold:" in html_content
    assert "Gross Proceeds:" in html_content
    assert "Cost or Other Basis:" in html_content
    assert "Gain or (Loss):" in html_content


def test_render_html_irs_values(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    assert ">C<" in html_content
    assert "Kalshi Event Contracts (Aggregate Summary)" in html_content
    assert html_content.count(">VARIOUS<") >= 2


def test_render_html_irs_after_positions(sample_csv):
    kalshi = KalshiCSV(sample_csv)
    kalshi.parse()
    html_content = render_portfolio_html(kalshi, "test.csv")
    positions_pos = html_content.find("Recent Closed Positions")
    irs_pos = html_content.find("IRS Form 8949")
    assert positions_pos > 0
    assert irs_pos > 0
    assert positions_pos < irs_pos
