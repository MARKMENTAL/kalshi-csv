# kalshi-csv

Parse Kalshi transaction CSV files and generate IRS Form 8949 tax summaries for event contract trading.

## Installation

```bash
pip install kalshi-csv
```

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

print(f"Total trades: {kalshi.summary['trade_count']}")
print(f"Total P&L: ${kalshi.summary['total_pnl_with_fees']:.2f}")

irs = kalshi.irs_summary()
print(f"Gross Proceeds: ${irs['gross_proceeds']:.2f}")
print(f"Cost Basis: ${irs['cost_basis']:.2f}")
print(f"Gain/Loss: ${irs['gain_or_loss']:.2f}")
```

## IRS Form 8949

Kalshi event contracts are typically reported on **IRS Form 8949, Box C** (short-term transactions not reported on Form 1099-B). The tool calculates:

- **Gross Proceeds**: Total exit value minus close fees
- **Cost Basis**: Total entry value plus open fees
- **Gain/Loss**: Realized P&L including all fees

Use the aggregate summary for a single-line entry on Form 8949, or export to a file for your records.

**Disclaimer**: This tool provides calculations based on Kalshi transaction data. Consult a tax professional for specific tax advice.

## License

MIT

