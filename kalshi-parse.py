#!/usr/bin/env python3
import csv
import sys
import os

class KalshiCSV:
    """Parses Kalshi transaction CSV data and handles terminal color-coding 
    and tax summary generation.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.trade_count = 0
        self.total_tax_basis = 0.0
        self.total_tax_proceeds = 0.0
        self.total_pnl_without_fees = 0.0
        self.total_pnl_with_fees = 0.0
        self.total_fees = 0.0

    def parse(self):
        """Processes the CSV file row-by-row and prints the live trade matrix."""
        if not os.path.exists(self.file_path):
            print(f"Error: File '{self.file_path}' not found.")
            sys.exit(1)

        print(f"\n{'Ticker':<32} | {'Side':<4} | {'Qty':<6} | {'Entry':<6} | {'Exit':<6} | {'P&L (No Fees)':<14}")
        print("-" * 83)

        with open(self.file_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if not row.get('realized_pnl_without_fees_dollars'):
                    continue
                    
                ticker = row['market_ticker']
                side = row['side'].upper()
                qty = float(row['quantity_fp'])
                entry = float(row['entry_price_dollars'])
                exit_val = float(row['exit_price_dollars'])
                
                pnl_no_fees = float(row['realized_pnl_without_fees_dollars'])
                pnl_with_fees = float(row['realized_pnl_with_fees_dollars'])
                
                open_fees = float(row['open_fees_dollars'])
                close_fees = float(row['close_fees_dollars'])
                
                # --- Aggregate Calculations ---
                self.total_tax_basis += (qty * entry) + open_fees
                self.total_tax_proceeds += (qty * exit_val) - close_fees
                self.total_pnl_without_fees += pnl_no_fees
                self.total_pnl_with_fees += pnl_with_fees
                self.total_fees += (open_fees + close_fees)
                self.trade_count += 1

                # Format row P&L using the color methods
                pnl_str = self.format_currency_color(pnl_no_fees)
                print(f"{ticker:<32} | {side:<4} | {qty:<6.2f} | ${entry:<5.2f} | ${exit_val:<5.2f} | {pnl_str:<14}")

        print("-" * 83)
        print(f"Total Transactions Parsed: {self.trade_count}")
        print(f"Total Exchange Fees Paid:  ${self.total_fees:.2f}")
        print(f"Internal Tracked Net P&L:  " + self.format_currency_color(self.total_pnl_without_fees))
        print("-" * 83)

    def color_green(self, text):
        """Wraps text in ANSI green."""
        return f"\033[1;32m{text}\033[0m"

    def color_red(self, text):
        """Wraps text in ANSI red."""
        return f"\033[1;31m{text}\033[0m"

    def format_currency_color(self, value):
        """Returns a signed, colorized string based on profit or loss status."""
        val_str = f"${value:+.2f}"
        return self.color_green(val_str) if value >= 0 else self.color_red(val_str)

    def summarizeIRS(self):
        """Outputs the structured block needed for a single-line entry on IRS Form 8949."""
        print("\033[1;33m=== IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY ===\033[0m")
        print("Use these exact aggregates for a single-line summary entry:")
        print(f"  * Box to Check:            \033[1;37mBox C\033[0m (Short-term, not reported on Form 1099-B)")
        print(f"  * (a) Description:         Kalshi Event Contracts (Aggregate Summary)")
        print(f"  * (d) Gross Proceeds:      " + self.color_green(f"${self.total_tax_proceeds:.2f}"))
        print(f"  * (e) Cost or Other Basis: \033[1;36m${self.total_tax_basis:.2f}\033[0m")
        print(f"  * (h) Gain or (Loss):      " + self.format_currency_color(self.total_pnl_with_fees))
        print("\033[1;33m====================================================\033[0m\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 kalshi_parser.py <path_to_transactions_csv>")
        sys.exit(1)
        
    # Instantiate, parse the matrix, and drop the IRS aggregate summary
    parser = KalshiCSV(sys.argv[1])
    parser.parse()
    parser.summarizeIRS()

