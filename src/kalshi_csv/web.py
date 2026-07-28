import html
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

from . import __version__


def render_portfolio_html(kalshi, csv_filename):
    """Renders the full HTML 4.01 portfolio page from parsed Kalshi data."""
    summary = kalshi.summary
    market_breakdown = kalshi.market_breakdown()
    recent_positions = kalshi.recent_closed_positions(20)

    period_end = summary["latest_close_date"]
    if period_end:
        period_end_str = period_end.strftime("%B %d, %Y").upper()
    else:
        period_end_str = "N/A"

    net_pnl = summary["total_pnl_with_fees"]
    net_pnl_color = "#006600" if net_pnl >= 0 else "#990000"
    net_pnl_str = f"${net_pnl:+.2f}"

    wins = summary["wins"]
    losses = summary["losses"]
    pushes = summary["pushes"]
    total = summary["trade_count"]
    win_pct = (wins / total * 100) if total > 0 else 0
    push_note = f" ({pushes} Push{'s' if pushes != 1 else ''})" if pushes > 0 else ""

    best_trade = summary["best_trade"]
    worst_trade = summary["worst_trade"]
    if best_trade and worst_trade:
        best_pnl = best_trade["pnl_with_fees"]
        worst_pnl = worst_trade["pnl_with_fees"]
        best_cat = best_trade["market_category"]
        worst_cat = worst_trade["market_category"]
        best_color = "#006600" if best_pnl >= 0 else "#990000"
        worst_color = "#006600" if worst_pnl >= 0 else "#990000"
        best_str = f"${best_pnl:+.2f}"
        worst_str = f"${worst_pnl:+.2f}"
        best_worst_subtext = f"{best_cat} / {worst_cat}"
    else:
        best_str = "$0.00"
        worst_str = "$0.00"
        best_color = "#006600"
        worst_color = "#990000"
        best_worst_subtext = "N/A"

    rows_html = ""
    for i, item in enumerate(market_breakdown):
        pnl = item["net_pnl"]
        pnl_color = "#006600" if pnl >= 0 else "#990000"
        pnl_str = f"${pnl:+.2f}"
        win_rate_str = f"{item['win_rate']:.1f}%"
        rows_html += f"""
                <tr>
                    <td align="left"><font face="Geneva, Verdana, sans-serif" size="2">{html.escape(item['category'])}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="2">{item['trades']}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="2">{win_rate_str}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="2" color="{pnl_color}"><b>{pnl_str}</b></font></td>
                </tr>"""
        if i < len(market_breakdown) - 1:
            rows_html += """
                <tr><td colspan="4"><hr size="1" color="#E0E0E0" noshade></td></tr>"""

    positions_html = ""
    for trade in recent_positions:
        close_dt = trade["close_timestamp"]
        date_str = close_dt.strftime("%m/%d %H:%M") if close_dt else "N/A"
        ticker = html.escape(trade["ticker"])
        side = trade["side"]
        qty = f"{trade['qty']:.2f}"
        entry = f"${trade['entry']:.2f}"
        exit_val = f"${trade['exit']:.2f}"
        pnl = trade["pnl_with_fees"]
        pnl_color = "#006600" if pnl >= 0 else "#990000"
        pnl_str = f"${pnl:+.2f}"
        positions_html += f"""
                <tr>
                    <td align="left"><font face="Courier New, Courier, monospace" size="1">{date_str}</font></td>
                    <td align="left"><font face="Courier New, Courier, monospace" size="1">{ticker}</font></td>
                    <td align="center"><font face="Courier New, Courier, monospace" size="1">{side}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="1">{qty}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="1">{entry}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="1">{exit_val}</font></td>
                    <td align="right"><font face="Courier New, Courier, monospace" size="1" color="{pnl_color}"><b>{pnl_str}</b></font></td>
                </tr>"""

    page = f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <title>Kalshi Portfolio Statement</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body bgcolor="#FFFFFF" text="#111111" link="#111111" vlink="#444444" alink="#000000" topmargin="20" leftmargin="20" marginwidth="20" marginheight="20">

<center>
<table width="720" border="0" cellspacing="0" cellpadding="0">

    <tr>
        <td align="left">
            <font face="Courier New, Courier, monospace" size="2"><b>KALSHI DERIVATIVES / ACCOUNT AUDIT</b></font><br>
            <font face="Georgia, Times New Roman, serif" size="5"><b>Year-End Performance Summary</b></font><br>
            <font face="Geneva, Verdana, sans-serif" size="1" color="#666666">PERIOD ENDING: {html.escape(period_end_str)} &nbsp;|&nbsp; SOURCE: {html.escape(csv_filename)}</font>
        </td>
    </tr>

    <tr>
        <td padding="10">
            <hr size="2" color="#111111" noshade>
        </td>
    </tr>

    <tr>
        <td>
            <table width="100%" border="0" cellspacing="0" cellpadding="6">
                <tr valign="top">
                    <td width="25%">
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#666666">NET REALIZED P&amp;L</font><br>
                        <font face="Courier New, Courier, monospace" size="4" color="{net_pnl_color}"><b>{net_pnl_str}</b></font><br>
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#888888">Includes ${summary['total_fees']:.2f} fees</font>
                    </td>
                    <td width="25%">
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#666666">WIN / LOSS RECORD</font><br>
                        <font face="Courier New, Courier, monospace" size="4"><b>{wins} - {losses}</b></font><br>
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#888888">{pushes} Push{'s' if pushes != 1 else ''} ({win_pct:.1f}% Win)</font>
                    </td>
                    <td width="25%">
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#666666">TOTAL VOLUME</font><br>
                        <font face="Courier New, Courier, monospace" size="4"><b>{total}</b></font><br>
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#888888">Executed Contracts</font>
                    </td>
                    <td width="25%">
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#666666">BEST/WORST SINGLE</font><br>
                        <font face="Courier New, Courier, monospace" size="2"><font color="{best_color}"><b>{best_str}</b></font> / <font color="{worst_color}"><b>{worst_str}</b></font></font><br>
                        <font face="Geneva, Verdana, sans-serif" size="1" color="#888888">{html.escape(best_worst_subtext)}</font>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <tr><td><br><hr size="1" color="#CCCCCC" noshade><br></td></tr>

    <tr>
        <td>
            <font face="Georgia, Times New Roman, serif" size="3"><b>Market Breakdown</b></font>
            <br><br>

            <table width="100%" border="0" cellspacing="0" cellpadding="4">
                <tr bgcolor="#EEEEEE">
                    <td width="45%" align="left"><font face="Geneva, Verdana, sans-serif" size="1"><b>ASSET CLASS / MARKET</b></font></td>
                    <td width="15%" align="right"><font face="Geneva, Verdana, sans-serif" size="1"><b>TRADES</b></font></td>
                    <td width="20%" align="right"><font face="Geneva, Verdana, sans-serif" size="1"><b>WIN RATE</b></font></td>
                    <td width="20%" align="right"><font face="Geneva, Verdana, sans-serif" size="1"><b>NET P&amp;L</b></font></td>
                </tr>
                {rows_html}
            </table>
        </td>
    </tr>

    <tr><td><br><hr size="1" color="#CCCCCC" noshade><br></td></tr>

    <tr>
        <td>
            <font face="Georgia, Times New Roman, serif" size="3"><b>Recent Closed Positions</b></font>
            <br><br>

            <table width="100%" border="0" cellspacing="0" cellpadding="3">
                <tr bgcolor="#EEEEEE">
                    <th align="left"><font face="Geneva, Verdana, sans-serif" size="1">DATE/TIME</font></th>
                    <th align="left"><font face="Geneva, Verdana, sans-serif" size="1">TICKER</font></th>
                    <th align="center"><font face="Geneva, Verdana, sans-serif" size="1">SIDE</font></th>
                    <th align="right"><font face="Geneva, Verdana, sans-serif" size="1">QTY</font></th>
                    <th align="right"><font face="Geneva, Verdana, sans-serif" size="1">ENTRY</font></th>
                    <th align="right"><font face="Geneva, Verdana, sans-serif" size="1">EXIT</font></th>
                    <th align="right"><font face="Geneva, Verdana, sans-serif" size="1">P&amp;L</font></th>
                </tr>
                {positions_html}
            </table>
        </td>
    </tr>

    <tr><td><br><hr size="2" color="#111111" noshade></td></tr>
    <tr>
        <td align="center">
            <font face="Geneva, Verdana, sans-serif" size="1" color="#666666">
                {html.escape(csv_filename)} &bull; rendered with vanilla HTML 4.01 strict table markup &bull; kalshi-csv v{__version__}
            </font>
        </td>
    </tr>

</table>
</center>

</body>
</html>"""
    return page


class LegacyWebHandler(BaseHTTPRequestHandler):
    """HTTP request handler that serves the legacy portfolio page."""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=iso-8859-1")
            self.end_headers()
            html_content = self.server.html_content
            self.wfile.write(html_content.encode("iso-8859-1"))
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        pass


class LegacyWebServer:
    """HTTP server for the legacy portfolio view."""

    def __init__(self, kalshi, csv_filename, host="0.0.0.0", port=8080):
        self.kalshi = kalshi
        self.csv_filename = csv_filename
        self.host = host
        self.port = port
        self.html_content = render_portfolio_html(kalshi, csv_filename)

    def serve(self):
        """Starts the HTTP server and blocks until interrupted."""
        server = HTTPServer((self.host, self.port), LegacyWebHandler)
        server.html_content = self.html_content
        print(f"Serving legacy portfolio view at http://{self.host}:{self.port}/")
        print("Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            server.server_close()
