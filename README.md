# kalshi-csv

Parse Kalshi transaction CSV files and generate IRS Form 8949 tax summaries for event contract trading.

## Installation

```bash
pip install kalshi-csv
```

## What's New in 0.2.0

- **Summary Cards**: View key metrics at a glance - Net Realized P&L, Win/Loss Record, Total Volume, and Best/Worst Single Trade
- **Market Breakdown**: See performance by market category with trade counts, win rates, and net P&L
- **Legacy Web Mode**: Browse your portfolio in a retro HTML 4.01 web interface compatible with older browsers (Netscape Navigator, IE 4+)
- **Market Categorization**: Automatic categorization of tickers into 7 market types (Global Soccer, MLB, NPB, NBA Summer League, WNBA, S&P 500, Multivariate Events, Other Markets)

## Getting Your Transactions CSV

Download your transaction history from Kalshi:

1. Go to [https://kalshi.com/account/taxes](https://kalshi.com/account/taxes)
2. Download the transaction CSV for the tax year you want to analyze
3. Pass it to `kalshi-csv` as shown below

Each tax year produces a separate CSV file.

## CSV Format

The tool expects the standard Kalshi transaction export with these columns:

```
type, quantity_fp, market_ticker, side, entry_price_dollars, exit_price_dollars,
open_fees_dollars, close_fees_dollars, realized_pnl_without_fees_dollars,
realized_pnl_with_fees_dollars, close_timestamp, open_timestamp
```

Rows without `realized_pnl_without_fees_dollars` are automatically skipped.

## CLI Usage

Parse a Kalshi transactions CSV and display the trade matrix with summary cards, market breakdown, and IRS summary:

```bash
kalshi-csv Kalshi-Transactions-2026.csv
```

Export the IRS summary to a file:

```bash
kalshi-csv Kalshi-Transactions-2026.csv --irs-file irs-summary.txt
```

Disable colored output (useful for piping or redirecting):

```bash
kalshi-csv Kalshi-Transactions-2026.csv --no-color
```

Use ASCII characters instead of Unicode box-drawing (for terminals without UTF-8 support):

```bash
kalshi-csv Kalshi-Transactions-2026.csv --ascii
```

Start a legacy web server to view your portfolio in a browser (HTML 4.01 compatible with older browsers):

```bash
kalshi-csv Kalshi-Transactions-2026.csv --legacy-web
```

Specify a custom port for the legacy web server:

```bash
kalshi-csv Kalshi-Transactions-2026.csv --legacy-web --legacy-web-port 3000
```

### Sample Output

Default mode (Unicode box-drawing):

```
┌──────────────────────────────────┬──────┬────────┬────────┬────────┬────────────────┬────────┐
│ Ticker                           │ Side │ Qty    │ Entry  │ Exit   │ P&L (No Fees)  │ Fees   │
├──────────────────────────────────┼──────┼────────┼────────┼────────┼────────────────┼────────┤
│ KXWCADVANCE-26JUL07ARGEGY-ARG    │ YES  │ 0.17   │ $0.86  │ $0.69  │ $-0.03         │ $0.00  │
│ KXWC1H-26JUL07ARGEGY-TIE         │ YES  │ 0.34   │ $0.28  │ $0.00  │ $-0.10         │ $0.00  │
│ KXMLBGAME-26JUL081940BOSCWS-BOS  │ YES  │ 0.96   │ $0.50  │ $0.91  │ $+0.39         │ $0.02  │
└──────────────────────────────────┴──────┴────────┴────────┴────────┴────────────────┴────────┘
Total Transactions Parsed: 3
Total Exchange Fees Paid:  $0.02
Internal Tracked Net P&L:  $+0.26
-----------------------------------------------------------------------------------

┌────────────────────────────┬────────────────────────────┬────────────────────────────┬────────────────────────────┐
│ NET REALIZED P&L           │ WIN / LOSS RECORD          │ TOTAL VOLUME               │ BEST/WORST SINGLE          │
├────────────────────────────┼────────────────────────────┼────────────────────────────┼────────────────────────────┤
│ $+0.26                     │ 2 - 1                      │ 3                          │ $+0.39 / $-0.10            │
│ Includes $0.02 fees        │ 0 Pushes (66.7% Win)       │ Executed Contracts         │ MLB Baseball / S&P 500     │
└────────────────────────────┴────────────────────────────┴────────────────────────────┴────────────────────────────┘

┌─────────────────────────────────────┬────────────┬──────────────┬──────────────────┐
│ ASSET CLASS / MARKET                │ TRADES     │ WIN RATE     │ NET P&L          │
├─────────────────────────────────────┼────────────┼──────────────┼──────────────────┤
│ Global Soccer / Football            │ 168        │ 54.8%        │ $+15.15          │
│ S&P 500 (INXU Intraday)             │ 110        │ 50.9%        │ $-32.21          │
│ Other Markets                       │ 87         │ 35.6%        │ $-28.63          │
│ MLB Baseball                        │ 44         │ 40.9%        │ $-13.06          │
│ NBA Summer League                   │ 43         │ 46.5%        │ $-7.09           │
│ NPB Baseball (Japan)                │ 40         │ 47.5%        │ $-10.68          │
│ Multivariate Events             │ 23         │ 8.7%         │ $-13.48          │
│ WNBA Basketball                     │ 6          │ 0.0%         │ $-5.87           │
└─────────────────────────────────────┴────────────┴──────────────┴──────────────────┘

=== IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY ===
Use these exact aggregates for a single-line summary entry:
  * Box to Check:            Box C (Short-term, not reported on Form 1099-B)
  * (a) Description:         Kalshi Event Contracts (Aggregate Summary)
  * (b) Date Acquired:       07/07/2026
  * (c) Date Sold:           07/08/2026
  * (d) Gross Proceeds:      $+2.50
  * (e) Cost or Other Basis: $2.24
  * (h) Gain or (Loss):      $+0.26
====================================================
```

ASCII mode (`--ascii`):

```
+----------------------------------+------+--------+--------+--------+----------------+--------+
| Ticker                           | Side | Qty    | Entry  | Exit   | P&L (No Fees)  | Fees   |
+----------------------------------+------+--------+--------+--------+----------------+--------+
| KXWCADVANCE-26JUL07ARGEGY-ARG    | YES  | 0.17   | $0.86  | $0.69  | $-0.03         | $0.00  |
| KXWC1H-26JUL07ARGEGY-TIE         | YES  | 0.34   | $0.28  | $0.00  | $-0.10         | $0.00  |
| KXMLBGAME-26JUL081940BOSCWS-BOS  | YES  | 0.96   | $0.50  | $0.91  | $+0.39         | $0.02  |
+----------------------------------+------+--------+--------+--------+----------------+--------+
Total Transactions Parsed: 3
Total Exchange Fees Paid:  $0.02
Internal Tracked Net P&L:  $+0.26
-----------------------------------------------------------------------------------

+----------------------------+----------------------------+----------------------------+----------------------------+
| NET REALIZED P&L           | WIN / LOSS RECORD          | TOTAL VOLUME               | BEST/WORST SINGLE          |
+----------------------------+----------------------------+----------------------------+----------------------------+
| $+0.26                     | 2 - 1                      | 3                          | $+0.39 / $-0.10            |
| Includes $0.02 fees        | 0 Pushes (66.7% Win)       | Executed Contracts         | MLB Baseball / S&P 500     |
+----------------------------+----------------------------+----------------------------+----------------------------+

+-------------------------------------+------------+--------------+------------------+
| ASSET CLASS / MARKET                | TRADES     | WIN RATE     | NET P&L          |
+-------------------------------------+------------+--------------+------------------+
| Global Soccer / Football            | 168        | 54.8%        | $+15.15          |
| S&P 500 (INXU Intraday)             | 110        | 50.9%        | $-32.21          |
| Other Markets                       | 87         | 35.6%        | $-28.63          |
| MLB Baseball                        | 44         | 40.9%        | $-13.06          |
| NBA Summer League                   | 43         | 46.5%        | $-7.09           |
| NPB Baseball (Japan)                | 40         | 47.5%        | $-10.68          |
| Multivariate Events             | 23         | 8.7%         | $-13.48          |
| WNBA Basketball                     | 6          | 0.0%         | $-5.87           |
+-------------------------------------+------------+--------------+------------------+

=== IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY ===
Use these exact aggregates for a single-line summary entry:
  * Box to Check:            Box C (Short-term, not reported on Form 1099-B)
  * (a) Description:         Kalshi Event Contracts (Aggregate Summary)
  * (b) Date Acquired:       07/07/2026
  * (c) Date Sold:           07/08/2026
  * (d) Gross Proceeds:      $+2.50
  * (e) Cost or Other Basis: $2.24
  * (h) Gain or (Loss):      $+0.26
====================================================
```

## Legacy Web Mode

View your portfolio in a web browser with a retro HTML 4.01 interface compatible with older browsers (Netscape Navigator, IE 4+):

```bash
kalshi-csv Kalshi-Transactions-2026.csv --legacy-web
```

This starts an HTTP server on `0.0.0.0:8080` by default. Access it from any machine on your network by navigating to `http://<your-ip>:8080`.

To use a different port:

```bash
kalshi-csv Kalshi-Transactions-2026.csv --legacy-web --legacy-web-port 3000
```

### What's Displayed

The web interface shows:

- **Summary Cards**: Net Realized P&L, Win/Loss Record, Total Volume, Best/Worst Single Trade
- **Market Breakdown**: Performance by category with trade counts, win rates, and net P&L
- **Recent Closed Positions**: Last 20 trades with timestamps, tickers, sides, quantities, entry/exit prices, and P&L
- **IRS Form 8949 Summary**: Tax reporting data including gross proceeds, cost basis, and gain/loss

The interface uses pure HTML 4.01 table layout with no CSS or JavaScript, ensuring compatibility with legacy browsers.

## Market Categorization

The tool automatically categorizes market tickers into the following categories:

- **Global Soccer / Football**: World Cup, Champions League, Europa League, Brasileirão, Argentino, Liga MX, and other soccer leagues
- **MLB Baseball**: Major League Baseball games and derivatives
- **NPB Baseball (Japan)**: Nippon Professional Baseball
- **NBA Summer League**: NBA Summer League games
- **WNBA Basketball**: Women's National Basketball Association
- **S&P 500 (INXU Intraday)**: S&P 500 index intraday contracts
- **Multivariate Events**: Multivariate Event (MVE) markets - parlay-style markets linking multiple individual event outcomes together
- **Other Markets**: Weather, politics, crypto, and all other markets

Categories are determined by analyzing ticker prefixes (e.g., `KXMLBGAME` → MLB Baseball, `KXINXU` → S&P 500).

## Library API

Use `kalshi-csv` as a Python library in your own scripts:

```python
from kalshi_csv import KalshiCSV

kalshi = KalshiCSV("Kalshi-Transactions-2026.csv")
kalshi.parse()

# Access individual trades
for trade in kalshi.trades:
    print(f"{trade['ticker']}: {trade['side']} {trade['qty']} @ ${trade['entry']}")
    print(f"  P&L: ${trade['pnl_with_fees']:.2f}")

# Access aggregate summary
print(f"Total trades: {kalshi.summary['trade_count']}")
print(f"Total fees: ${kalshi.summary['total_fees']:.2f}")
print(f"Total P&L: ${kalshi.summary['total_pnl_with_fees']:.2f}")

# Get IRS Form 8949 data
irs = kalshi.irs_summary()
print(f"Gross Proceeds: ${irs['gross_proceeds']:.2f}")
print(f"Cost Basis: ${irs['cost_basis']:.2f}")
print(f"Gain/Loss: ${irs['gain_or_loss']:.2f}")

# Get market breakdown by category
breakdown = kalshi.market_breakdown()
for item in breakdown:
    print(f"{item['category']}: {item['trades']} trades, {item['win_rate']:.1f}% win, ${item['net_pnl']:+.2f}")

# Get recent closed positions
recent = kalshi.recent_closed_positions(10)
for trade in recent:
    print(f"{trade['close_timestamp']}: {trade['ticker']} ${trade['pnl_with_fees']:+.2f}")
```

### Data Structures

**Trade dict** (`kalshi.trades`):
- `ticker`: Market ticker symbol
- `side`: "YES" or "NO"
- `qty`: Quantity of contracts
- `entry`: Entry price in dollars
- `exit`: Exit price in dollars
- `pnl_no_fees`: P&L without fees
- `pnl_with_fees`: P&L including fees
- `open_fees`: Opening fees
- `close_fees`: Closing fees
- `open_timestamp`: When the position was opened (datetime object or None)
- `close_timestamp`: When the position was closed (datetime object or None)
- `market_category`: Categorized market type (e.g., "MLB Baseball", "Global Soccer / Football")

**Summary dict** (`kalshi.summary`):
- `trade_count`: Number of trades parsed
- `total_fees`: Sum of all fees
- `total_pnl_without_fees`: Total P&L excluding fees
- `total_pnl_with_fees`: Total P&L including fees
- `total_tax_basis`: Total cost basis for IRS reporting
- `total_tax_proceeds`: Total proceeds for IRS reporting
- `wins`: Number of winning trades (pnl_with_fees > 0)
- `losses`: Number of losing trades (pnl_with_fees < 0)
- `pushes`: Number of break-even trades (pnl_with_fees == 0)
- `best_trade`: Trade dict with highest pnl_with_fees (or None)
- `worst_trade`: Trade dict with lowest pnl_with_fees (or None)

**IRS summary dict** (`kalshi.irs_summary()`):
- `box`: "C" (for Form 8949 Box C)
- `description`: "Kalshi Event Contracts (Aggregate Summary)"
- `gross_proceeds`: Total proceeds
- `cost_basis`: Total cost basis
- `gain_or_loss`: Net gain or loss

## IRS Form 8949

Kalshi event contracts are typically reported on **IRS Form 8949, Box C** (short-term transactions not reported on Form 1099-B). The tool calculates:

- **Gross Proceeds**: Total exit value minus close fees
- **Cost Basis**: Total entry value plus open fees
- **Gain/Loss**: Realized P&L including all fees

Use the aggregate summary for a single-line entry on Form 8949, or export to a file for your records.

**Disclaimer**: This tool provides calculations based on Kalshi transaction data. Consult a tax professional for specific tax advice.

## Source Code

This project is hosted in two locations:
- **GitHub**: [https://github.com/MARKMENTAL/kalshi-csv](https://github.com/MARKMENTAL/kalshi-csv)
- **Codeberg**: [https://codeberg.org/markmental/kalshi-csv](https://codeberg.org/markmental/kalshi-csv)

## License

[MIT](LICENSE)

