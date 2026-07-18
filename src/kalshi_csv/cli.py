import argparse
import sys

from .parser import KalshiCSV
from .formatter import (
    color_white,
    color_yellow,
    color_cyan,
    format_currency_color,
)


def main():
    parser = argparse.ArgumentParser(
        description="Parse Kalshi transaction CSV and generate IRS tax summary."
    )
    parser.add_argument("csv_path", help="Path to Kalshi transactions CSV file")
    parser.add_argument(
        "--irs-file",
        help="Write IRS Form 8949 summary to this file",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )

    args = parser.parse_args()
    no_color = args.no_color

    kalshi = KalshiCSV(args.csv_path)
    kalshi.parse()

    print()
    print(
        f"{'Ticker':<32} | {'Side':<4} | {'Qty':<6} | {'Entry':<6} | {'Exit':<6} | {'P&L (No Fees)':<14}"
    )
    print("-" * 83)

    for trade in kalshi.trades:
        pnl_str = format_currency_color(trade["pnl_no_fees"], no_color)
        print(
            f"{trade['ticker']:<32} | {trade['side']:<4} | {trade['qty']:<6.2f} | "
            f"${trade['entry']:<5.2f} | ${trade['exit']:<5.2f} | {pnl_str:<14}"
        )

    print("-" * 83)
    print(f"Total Transactions Parsed: {kalshi.summary['trade_count']}")
    print(f"Total Exchange Fees Paid:  ${kalshi.summary['total_fees']:.2f}")
    print(
        f"Internal Tracked Net P&L:  "
        + format_currency_color(kalshi.summary["total_pnl_without_fees"], no_color)
    )
    print("-" * 83)

    irs = kalshi.irs_summary()
    print(color_yellow("=== IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY ===", no_color))
    print("Use these exact aggregates for a single-line summary entry:")
    print(f"  * Box to Check:            {color_white('Box C', no_color)} (Short-term, not reported on Form 1099-B)")
    print(f"  * (a) Description:         {irs['description']}")
    print(f"  * (d) Gross Proceeds:      {format_currency_color(irs['gross_proceeds'], no_color)}")
    print(f"  * (e) Cost or Other Basis: {color_cyan(f'${irs['cost_basis']:.2f}', no_color)}")
    print(f"  * (h) Gain or (Loss):      {format_currency_color(irs['gain_or_loss'], no_color)}")
    print(color_yellow("====================================================", no_color))
    print()

    if args.irs_file:
        with open(args.irs_file, "w", encoding="utf-8") as f:
            f.write("IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY\n")
            f.write("Use these exact aggregates for a single-line summary entry:\n")
            f.write(f"  * Box to Check:            Box C (Short-term, not reported on Form 1099-B)\n")
            f.write(f"  * (a) Description:         {irs['description']}\n")
            f.write(f"  * (d) Gross Proceeds:      ${irs['gross_proceeds']:.2f}\n")
            f.write(f"  * (e) Cost or Other Basis: ${irs['cost_basis']:.2f}\n")
            f.write(f"  * (h) Gain or (Loss):      ${irs['gain_or_loss']:.2f}\n")
        print(f"IRS summary written to: {args.irs_file}")


if __name__ == "__main__":
    main()
