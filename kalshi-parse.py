#!/usr/bin/env python3
import csv
import sys
import os

def parse_kalshi_csv(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    total_tax_basis = 0.0
    total_tax_proceeds = 0.0
    total_pnl_without_fees = 0.0
    total_pnl_with_fees = 0.0
    total_fees = 0.0
    trade_count = 0

    print(f"\n{'Ticker':<32} | {'Side':<4} | {'Qty':<6} | {'Entry':<6} | {'Exit':<6} | {'P&L (No Fees)':<14}")
    print("-" * 83)

    with open(file_path, mode='r', newline='', encoding='utf-8') as f:
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
            fees = open_fees + close_fees

            # --- IRS FORM 8949 TAX RULES ---
            # 1. Open fees are added to your Cost Basis (makes it cost more to acquire)
            total_tax_basis += (qty * entry) + open_fees
            
            # 2. Close fees reduce your Gross Proceeds (cuts down the cash you walked away with)
            total_tax_proceeds += (qty * exit_val) - close_fees
            
            total_pnl_without_fees += pnl_no_fees
            total_pnl_with_fees += pnl_with_fees
            total_fees += fees
            trade_count += 1

            pnl_str = f"${pnl_no_fees:+.2f}"
            print(f"{ticker:<32} | {side:<4} | {qty:<6.2f} | ${entry:<5.2f} | ${exit_val:<5.2f} | {pnl_str:<14}")

    print("-" * 83)
    print(f"Total Transactions Parsed: {trade_count}")
    print(f"Total Exchange Fees Paid:  ${total_fees:.2f}")
    print(f"Internal Tracked Net P&L:  ${total_pnl_without_fees:+.2f}")
    print("-" * 83)
    
    # --- IRS FORM 8949 TAX REPORTING BLOCK ---
    print("\033[1;33m=== IRS FORM 8949 / SCHEDULE D AGGREGATE SUMMARY ===\033[0m")
    print("Use these exact aggregates for a single-line summary entry:")
    print(f"  * Box to Check:            \033[1;37mBox C\033[0m (Short-term, not reported on Form 1099-B)")
    print(f"  * (a) Description:         Kalshi Event Contracts (Aggregate Summary)")
    print(f"  * (d) Gross Proceeds:      \033[1;32m${total_tax_proceeds:.2f}\033[0m")
    print(f"  * (e) Cost or Other Basis: \033[1;36m${total_tax_basis:.2f}\033[0m")
    print(f"  * (h) Gain or (Loss):      " + (f"\033[1;32m${total_pnl_with_fees:+.2f}\033[0m" if total_pnl_with_fees >= 0 else f"\033[1;31m${total_pnl_with_fees:+.2f}\033[0m"))
    print("\033[1;33m====================================================\033[0m\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 kalshi_parser.py <path_to_transactions_csv>")
        sys.exit(1)
        
    parse_kalshi_csv(sys.argv[1])

