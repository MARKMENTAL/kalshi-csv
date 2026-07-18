# kalshi-csv

Parse Kalshi transaction CSV files and generate IRS Form 8949 tax summaries for event contract trading.

## Installation

```bash
pip install kalshi-csv
```

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

Parse a Kalshi transactions CSV and display the trade matrix with IRS summary:

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

### Sample Output

```
Ticker                             | Side | Qty    | Entry  | Exit   | P&L (No Fees)
-------------------------------------------------------------------------------
KXWCADVANCE-26JUL07ARGEGY-ARG      | YES  | 0.17   | $0.86  | $0.69  | -$0.03
KXWC1H-26JUL07ARGEGY-TIE           | YES  | 0.34   | $0.28  | $0.00  | -$0.10
KXMLBGAME-26JUL081940BOSCWS-BOS    | YES  | 0.96   | $0.50  | $0.91  | $0.39
-------------------------------------------------------------------------------
Total Transactions Parsed: 3
Total Exchange Fees Paid:  $0.05
Internal Tracked Net P&L:  $0.26
-------------------------------------------------------------------------------
=== IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY ===
Use these exact aggregates for a single-line summary entry:
  * Box to Check:            Box C (Short-term, not reported on Form 1099-B)
  * (a) Description:         Kalshi Event Contracts (Aggregate Summary)
  * (d) Gross Proceeds:      $2.50
  * (e) Cost or Other Basis: $2.24
  * (h) Gain or (Loss):      $0.26
====================================================
```

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

**Summary dict** (`kalshi.summary`):
- `trade_count`: Number of trades parsed
- `total_fees`: Sum of all fees
- `total_pnl_without_fees`: Total P&L excluding fees
- `total_pnl_with_fees`: Total P&L including fees
- `total_tax_basis`: Total cost basis for IRS reporting
- `total_tax_proceeds`: Total proceeds for IRS reporting

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

