import csv
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

import yfinance as yf

from .categories import categorize_ticker


SP500_MARKET_CATEGORY = "S&P 500 (INXU Intraday)"
SP500_PRICE_TIERS = (
    "<=$0.40 (Out-of-the-Money Speculative)",
    ">$0.40-$0.70 (At-the-Money / Coincident)",
    ">$0.70-$0.85 (Likely / Moderate ITM)",
    ">$0.85 (Deep ITM / High Probability)",
)
NEW_YORK_TZ = ZoneInfo("America/New_York")
SP500_TICKER_RE = re.compile(
    r"^KXINXU-(?P<date>\d{2}[A-Z]{3}\d{2})H(?P<hour>\d{4})-T(?P<strike>\d+(?:\.\d+)?)$"
)


def _parse_sp500_ticker_date(date_str):
    """Parse a Kalshi YYMMMDD date string (e.g. 26SEP24 -> 2026-09-24)."""
    try:
        return datetime.strptime(date_str, "%y%b%d").date()
    except ValueError:
        return None


def _sp500_price_tier(entry):
    if not 0 <= entry <= 1:
        return None
    if entry <= 0.40:
        return SP500_PRICE_TIERS[0]
    if entry <= 0.70:
        return SP500_PRICE_TIERS[1]
    if entry <= 0.85:
        return SP500_PRICE_TIERS[2]
    return SP500_PRICE_TIERS[3]


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

    def sp500_price_tier_breakdown(self):
        """Returns S&P 500 trade performance grouped by contract entry price."""
        tiers = {
            label: {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "win_pnl": 0.0,
                "loss_pnl": 0.0,
                "net_pnl": 0.0,
            }
            for label in SP500_PRICE_TIERS
        }

        for trade in self.trades:
            if trade["market_category"] != SP500_MARKET_CATEGORY:
                continue

            label = _sp500_price_tier(trade["entry"])
            if label is None:
                continue

            pnl = trade["pnl_with_fees"]
            tier = tiers[label]
            tier["trades"] += 1
            tier["net_pnl"] += pnl
            if pnl > 0:
                tier["wins"] += 1
                tier["win_pnl"] += pnl
            elif pnl < 0:
                tier["losses"] += 1
                tier["loss_pnl"] += pnl

        breakdown = []
        for label, data in tiers.items():
            if data["trades"] == 0:
                continue

            breakdown.append({
                "price_tier": label,
                "trades": data["trades"],
                "win_rate": data["wins"] / data["trades"] * 100,
                "average_win": data["win_pnl"] / data["wins"] if data["wins"] else None,
                "average_loss": data["loss_pnl"] / data["losses"] if data["losses"] else None,
                "net_pnl": data["net_pnl"],
            })

        return breakdown

    def sp500_hourly_performance(self, min_trades=5):
        """Summarize S&P 500 performance by entry-price tier and target hour.

        Contract target hours come from the Hhhmm field in the market ticker.
        The top five qualifying tier/hour combinations are marked as
        historical recommendations. Eligible groups must meet the sample
        threshold and have positive net P&L; ranking uses win rate and then
        net P&L.
        """
        groups = {}
        for trade in self.trades:
            if trade["market_category"] != SP500_MARKET_CATEGORY:
                continue

            price_tier = _sp500_price_tier(trade["entry"])
            ticker_data = self._parse_sp500_ticker(trade.get("ticker", ""))
            if price_tier is None or ticker_data is None:
                continue

            target_hour = ticker_data["cutoff_hour"]
            key = (price_tier, target_hour)
            group = groups.setdefault(key, {
                "price_tier": price_tier,
                "hour": target_hour,
                "trades": [],
            })
            group["trades"].append(trade)

        breakdown = []
        trades_by_group = {}
        for key, group in groups.items():
            trades = group["trades"]
            trades_by_group[key] = trades
            group["trades"] = len(trades)
            group["wins"] = sum(1 for t in trades if t["pnl_with_fees"] > 0)
            group["losses"] = sum(1 for t in trades if t["pnl_with_fees"] < 0)
            group["pushes"] = sum(1 for t in trades if t["pnl_with_fees"] == 0)
            group["net_pnl"] = sum(t["pnl_with_fees"] for t in trades)
            group["win_rate"] = group["wins"] / group["trades"] * 100
            group["average_pnl"] = group["net_pnl"] / group["trades"]
            group["target_hour"] = "{:02d}:00 ET".format(group["hour"])
            group["recommended"] = False
            group["market_context"] = self._sp500_market_context(trades)
            avg_open, avg_close = self._sp500_avg_prices(group)
            group["avg_sp500_open"] = avg_open
            group["avg_sp500_close"] = avg_close
            breakdown.append(group)

        tier_order = {label: index for index, label in enumerate(SP500_PRICE_TIERS)}
        breakdown.sort(key=lambda item: (
            tier_order[item["price_tier"]],
            item["hour"],
        ))

        eligible = [
            item for item in breakdown
            if item["trades"] >= min_trades and item["net_pnl"] > 0
        ]
        eligible.sort(key=lambda item: (item["win_rate"], item["net_pnl"]), reverse=True)
        for item in eligible[:5]:
            item["recommended"] = True
            key = (item["price_tier"], item["hour"])
            item["top_trades"] = self._sp500_top_trades(trades_by_group[key])

        return breakdown

    @staticmethod
    def _sp500_top_trades(trades, limit=3):
        """Return up to `limit` winning trades sorted by net P&L descending."""
        winners = [t for t in trades if t["pnl_with_fees"] > 0]
        winners.sort(key=lambda t: t["pnl_with_fees"], reverse=True)
        top_trades = []
        for trade in winners[:limit]:
            open_dt = trade.get("open_timestamp")
            if open_dt is not None:
                if open_dt.tzinfo is None:
                    open_dt = open_dt.replace(tzinfo=NEW_YORK_TZ)
                else:
                    open_dt = open_dt.astimezone(NEW_YORK_TZ)
                open_time_et = open_dt.strftime("%b %d, %Y %I:%M %p ET")
            else:
                open_time_et = ""
            top_trades.append({
                "ticker": trade["ticker"],
                "side": trade["side"],
                "entry": trade["entry"],
                "exit": trade["exit"],
                "pnl": trade["pnl_with_fees"],
                "open_time_et": open_time_et,
            })
        return top_trades

    @staticmethod
    def _parse_sp500_ticker(ticker):
        """Extract target date, cutoff hour, and strike from an S&P ticker."""
        match = SP500_TICKER_RE.match(ticker)
        if not match:
            return None
        date = _parse_sp500_ticker_date(match.group("date"))
        if date is None:
            return None
        hour = int(match.group("hour")[:2])
        if hour > 23:
            return None
        return {
            "target_date": date,
            "cutoff_hour": hour,
            "strike": float(match.group("strike")),
        }

    def _fetch_sp500_prices(self, start, end):
        """Fetch intraday ^GSPC prices, returning an empty series on failure."""
        try:
            data = yf.download(
                "^GSPC",
                start=start,
                end=end,
                interval="1h",
                progress=False,
                auto_adjust=False,
            )
            if data.empty:
                return None
            close = data["Close"]
            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            return close.dropna()
        except Exception:
            return None

    def _sp500_price_at(self, prices, dt):
        """Return the closest available S&P price at or before dt."""
        if prices is None or prices.empty:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=NEW_YORK_TZ)
        dt = dt.astimezone(ZoneInfo("UTC"))
        idx = prices.index
        if idx.tzinfo is None:
            idx = idx.tz_localize("UTC")
        pos = idx.searchsorted(dt, side="right") - 1
        if pos < 0:
            return None
        return float(prices.iloc[pos])

    def _sp500_market_context(self, trades):
        """Build S&P price context for a group of S&P trades."""
        if not trades:
            return None
        parsed = [self._parse_sp500_ticker(t["ticker"]) for t in trades]
        parsed = [p for p in parsed if p]
        if not parsed:
            return None
        strikes = [p["strike"] for p in parsed]
        strike = sum(strikes) / len(strikes)
        opens = [t["open_timestamp"] for t in trades if t.get("open_timestamp")]
        closes = [t["close_timestamp"] for t in trades if t.get("close_timestamp")]
        if not opens:
            return None
        min_dt = min(opens)
        max_dt = max(closes) if closes else max(opens)
        start = min_dt.astimezone(NEW_YORK_TZ).date() - timedelta(days=1)
        end = max_dt.astimezone(NEW_YORK_TZ).date() + timedelta(days=2)
        prices = self._fetch_sp500_prices(start, end)
        if prices is None:
            return {"strike": strike, "available": False}
        open_prices = [self._sp500_price_at(prices, dt) for dt in opens]
        open_prices = [p for p in open_prices if p is not None]
        close_prices = [self._sp500_price_at(prices, dt) for dt in closes]
        close_prices = [p for p in close_prices if p is not None]
        if not open_prices or not close_prices:
            return {"strike": strike, "available": False}
        avg_open = sum(open_prices) / len(open_prices)
        avg_close = sum(close_prices) / len(close_prices)
        # Compare at the ticker's scheduled cutoff time when available.
        cutoff_prices = []
        for p in parsed:
            cutoff_dt = datetime(
                p["target_date"].year,
                p["target_date"].month,
                p["target_date"].day,
                p["cutoff_hour"],
                tzinfo=NEW_YORK_TZ,
            )
            cp = self._sp500_price_at(prices, cutoff_dt)
            if cp is not None:
                cutoff_prices.append(cp)
        cutoff_above = None
        if cutoff_prices:
            avg_cutoff = sum(cutoff_prices) / len(cutoff_prices)
            cutoff_above = avg_cutoff > strike
        return {
            "strike": strike,
            "available": True,
            "avg_open": avg_open,
            "avg_close": avg_close,
            "open_above": avg_open > strike,
            "close_above": avg_close > strike,
            "move": avg_close - avg_open,
            "cutoff_above": cutoff_above,
        }

    @staticmethod
    def _sp500_avg_prices(group):
        """Return average S&P prices at trade open and close for a group."""
        ctx = group.get("market_context")
        if not ctx or not ctx.get("available"):
            return None, None
        return ctx.get("avg_open"), ctx.get("avg_close")

    def recent_closed_positions(self, n=20):
        """Returns the last n trades sorted by close_timestamp descending."""
        trades_with_close = [t for t in self.trades if t["close_timestamp"] is not None]
        sorted_trades = sorted(
            trades_with_close,
            key=lambda t: t["close_timestamp"],
            reverse=True,
        )
        return sorted_trades[:n]
