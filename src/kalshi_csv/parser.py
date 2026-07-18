import csv
import os


class KalshiCSV:
    """Parses Kalshi transaction CSV data and calculates tax-relevant aggregates."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.trades = []
        self.summary = {
            "trade_count": 0,
            "total_fees": 0.0,
            "total_pnl_without_fees": 0.0,
            "total_pnl_with_fees": 0.0,
            "total_tax_basis": 0.0,
            "total_tax_proceeds": 0.0,
        }

    def parse(self):
        """Processes the CSV file row-by-row and populates trades and summary."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File '{self.file_path}' not found.")

        with open(self.file_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if not row.get("realized_pnl_without_fees_dollars"):
                    continue

                qty = float(row["quantity_fp"])
                entry = float(row["entry_price_dollars"])
                exit_val = float(row["exit_price_dollars"])
                pnl_no_fees = float(row["realized_pnl_without_fees_dollars"])
                pnl_with_fees = float(row["realized_pnl_with_fees_dollars"])
                open_fees = float(row["open_fees_dollars"])
                close_fees = float(row["close_fees_dollars"])

                trade = {
                    "ticker": row["market_ticker"],
                    "side": row["side"].upper(),
                    "qty": qty,
                    "entry": entry,
                    "exit": exit_val,
                    "pnl_no_fees": pnl_no_fees,
                    "pnl_with_fees": pnl_with_fees,
                    "open_fees": open_fees,
                    "close_fees": close_fees,
                }
                self.trades.append(trade)

                self.summary["trade_count"] += 1
                self.summary["total_tax_basis"] += (qty * entry) + open_fees
                self.summary["total_tax_proceeds"] += (qty * exit_val) - close_fees
                self.summary["total_pnl_without_fees"] += pnl_no_fees
                self.summary["total_pnl_with_fees"] += pnl_with_fees
                self.summary["total_fees"] += open_fees + close_fees

        return self

    def irs_summary(self):
        """Returns a dict with IRS Form 8949 aggregate fields."""
        return {
            "box": "C",
            "description": "Kalshi Event Contracts (Aggregate Summary)",
            "gross_proceeds": self.summary["total_tax_proceeds"],
            "cost_basis": self.summary["total_tax_basis"],
            "gain_or_loss": self.summary["total_pnl_with_fees"],
        }
