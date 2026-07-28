import argparse
import os
import sys

from .parser import KalshiCSV
from .formatter import (
    color_white,
    color_yellow,
    color_cyan,
    format_currency_color,
    format_currency_color_padded,
    truncate_ticker,
    format_table_header,
    format_table_separator,
    format_table_row,
    get_box_chars,
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
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Use ASCII characters instead of Unicode box-drawing",
    )
    parser.add_argument(
        "--legacy-web",
        action="store_true",
        help="Start a legacy web server (HTML 4.01) to view portfolio in browser",
    )
    parser.add_argument(
        "--legacy-web-port",
        type=int,
        default=8080,
        help="Port for legacy web server (default: 8080)",
    )

    args = parser.parse_args()
    no_color = args.no_color
    ascii_mode = args.ascii

    kalshi = KalshiCSV(args.csv_path)
    kalshi.parse()

    if args.legacy_web:
        from .web import LegacyWebServer
        csv_filename = os.path.basename(args.csv_path)
        server = LegacyWebServer(kalshi, csv_filename, port=args.legacy_web_port)
        server.serve()
        return

    headers = ["Ticker", "Side", "Qty", "Entry", "Exit", "P&L (No Fees)", "Fees"]
    widths = [32, 4, 6, 6, 6, 14, 6]

    print()
    print(format_table_separator(widths, ascii_mode, "top"))
    print(format_table_header(headers, widths, ascii_mode))
    print(format_table_separator(widths, ascii_mode, "middle"))

    for trade in kalshi.trades:
        pnl_str = format_currency_color_padded(trade["pnl_no_fees"], 14, no_color)
        fees = trade["open_fees"] + trade["close_fees"]
        ticker_display = truncate_ticker(trade["ticker"])
        
        box = get_box_chars(ascii_mode)
        row = (
            f" {ticker_display:<32} "
            f"{box['vertical']} {trade['side']:<4} "
            f"{box['vertical']} {trade['qty']:<6.2f} "
            f"{box['vertical']} ${trade['entry']:<5.2f} "
            f"{box['vertical']} ${trade['exit']:<5.2f} "
            f"{box['vertical']} {pnl_str} "
            f"{box['vertical']} ${fees:<5.2f} "
        )
        print(box["vertical"] + row + box["vertical"])

    print(format_table_separator(widths, ascii_mode, "bottom"))
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
    print(f"  * (b) Date Acquired:       {irs['date_acquired']}")
    print(f"  * (c) Date Sold:           {irs['date_sold']}")
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
            f.write(f"  * (b) Date Acquired:       {irs['date_acquired']}\n")
            f.write(f"  * (c) Date Sold:           {irs['date_sold']}\n")
            f.write(f"  * (d) Gross Proceeds:      ${irs['gross_proceeds']:.2f}\n")
            f.write(f"  * (e) Cost or Other Basis: ${irs['cost_basis']:.2f}\n")
            f.write(f"  * (h) Gain or (Loss):      ${irs['gain_or_loss']:.2f}\n")
        print(f"IRS summary written to: {args.irs_file}")


if __name__ == "__main__":
    main()
