import csv
import os
from collections import defaultdict
from datetime import datetime

from .categories import categorize_ticker


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
            "earliest_open_date": None,
            "latest_close_date": None,
            "wins": 0,
            "losses": 0,
            "pushes": 0,
            "best_trade": None,
            "worst_trade": None,
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

                open_dt = None
                close_dt = None
                if row.get("open_timestamp"):
                    try:
                        open_dt = datetime.fromisoformat(row["open_timestamp"])
                    except ValueError:
                        pass
                if row.get("close_timestamp"):
                    try:
                        close_dt = datetime.fromisoformat(row["close_timestamp"])
                    except ValueError:
                        pass

                ticker = row["market_ticker"]
                trade = {
                    "ticker": ticker,
                    "side": row["side"].upper(),
                    "qty": qty,
                    "entry": entry,
                    "exit": exit_val,
                    "pnl_no_fees": pnl_no_fees,
                    "pnl_with_fees": pnl_with_fees,
                    "open_fees": open_fees,
                    "close_fees": close_fees,
                    "open_timestamp": open_dt,
                    "close_timestamp": close_dt,
                    "market_category": categorize_ticker(ticker),
                }
                self.trades.append(trade)

                self.summary["trade_count"] += 1
                self.summary["total_tax_basis"] += (qty * entry) + open_fees
                self.summary["total_tax_proceeds"] += (qty * exit_val) - close_fees
                self.summary["total_pnl_without_fees"] += pnl_no_fees
                self.summary["total_pnl_with_fees"] += pnl_with_fees
                self.summary["total_fees"] += open_fees + close_fees

                if pnl_with_fees > 0:
                    self.summary["wins"] += 1
                elif pnl_with_fees < 0:
                    self.summary["losses"] += 1
                else:
                    self.summary["pushes"] += 1

                if (
                    self.summary["best_trade"] is None
                    or pnl_with_fees > self.summary["best_trade"]["pnl_with_fees"]
                ):
                    self.summary["best_trade"] = trade
                if (
                    self.summary["worst_trade"] is None
                    or pnl_with_fees < self.summary["worst_trade"]["pnl_with_fees"]
                ):
                    self.summary["worst_trade"] = trade

                if open_dt is not None:
                    if (
                        self.summary["earliest_open_date"] is None
                        or open_dt < self.summary["earliest_open_date"]
                    ):
                        self.summary["earliest_open_date"] = open_dt

                if close_dt is not None:
                    if (
                        self.summary["latest_close_date"] is None
                        or close_dt > self.summary["latest_close_date"]
                    ):
                        self.summary["latest_close_date"] = close_dt

        return self

    def _format_date(self, dt):
        """Formats a datetime object as MM/DD/YYYY for IRS Form 8949."""
        if dt is None:
            return ""
        return dt.strftime("%m/%d/%Y")

    def irs_summary(self):
        """Returns a dict with IRS Form 8949 aggregate fields."""
        return {
            "box": "C",
            "description": "Kalshi Event Contracts (Aggregate Summary)",
            "date_acquired": self._format_date(self.summary["earliest_open_date"]),
            "date_sold": self._format_date(self.summary["latest_close_date"]),
            "gross_proceeds": self.summary["total_tax_proceeds"],
            "cost_basis": self.summary["total_tax_basis"],
            "gain_or_loss": self.summary["total_pnl_with_fees"],
        }

    def market_breakdown(self):
        """Returns a list of dicts with market category breakdown sorted by trade count."""
        categories = defaultdict(lambda: {"trades": 0, "wins": 0, "net_pnl": 0.0})

        for trade in self.trades:
            cat = trade["market_category"]
            categories[cat]["trades"] += 1
            categories[cat]["net_pnl"] += trade["pnl_with_fees"]
            if trade["pnl_with_fees"] > 0:
                categories[cat]["wins"] += 1

        breakdown = []
        for cat, data in categories.items():
            win_rate = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
            breakdown.append({
                "category": cat,
                "trades": data["trades"],
                "win_rate": win_rate,
                "net_pnl": data["net_pnl"],
            })

        return sorted(breakdown, key=lambda x: x["trades"], reverse=True)

    def recent_closed_positions(self, n=20):
        """Returns the last n trades sorted by close_timestamp descending."""
        trades_with_close = [t for t in self.trades if t["close_timestamp"] is not None]
        sorted_trades = sorted(
            trades_with_close,
            key=lambda t: t["close_timestamp"],
            reverse=True,
        )
        return sorted_trades[:n]
