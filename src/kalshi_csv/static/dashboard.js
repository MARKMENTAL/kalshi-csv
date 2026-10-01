(() => {
    "use strict";

    window.dashboardApp = function () {
        const payload = JSON.parse(document.getElementById("dashboard-data").textContent);

        return {
            filename: payload.filename,
            periodEnd: payload.period_end,
            summary: payload.summary,
            markets: payload.markets,
            sp500Tiers: payload.sp500_tiers,
            sp500Hourly: payload.sp500_hourly,
            sp500SuggestionRevealed: false,
            trades: payload.trades,
            irs: payload.irs,
            themes: payload.themes,
            selectedTheme: "Nord",
            search: "",
            categoryFilter: "",
            sideFilter: "",
            sortKey: "close_timestamp",
            sortDirection: "desc",
            page: 1,
            pageSize: 25,

            init() {
                try {
                    const savedTheme = window.localStorage.getItem("kalshi-csv-modern-theme");
                    if (this.themes.some((theme) => theme.name === savedTheme)) {
                        this.selectedTheme = savedTheme;
                    }
                } catch (error) {
                    // The dashboard still works when browser storage is disabled.
                }
                this.applyTheme();
            },

            applyTheme() {
                const theme = this.themes.find((item) => item.name === this.selectedTheme) || this.themes[0];
                const root = document.documentElement;
                root.style.setProperty("--app-fg", theme.fg);
                root.style.setProperty("--app-bg", theme.bg);
                const rgb = theme.bg.match(/[\da-f]{2}/gi).map((part) => parseInt(part, 16));
                const brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
                root.style.colorScheme = brightness > 145 ? "light" : "dark";
                theme.ansi_normal.forEach((color, index) => root.style.setProperty(`--ansi-${index}`, color));
                theme.ansi_bright.forEach((color, index) => root.style.setProperty(`--ansi-bright-${index}`, color));
                try {
                    window.localStorage.setItem("kalshi-csv-modern-theme", theme.name);
                } catch (error) {
                    // Keep the selected theme for this page view if storage is unavailable.
                }
            },

            get categories() {
                return [...new Set(this.trades.map((trade) => trade.market_category))].sort((a, b) => a.localeCompare(b));
            },

            get sp500Suggestions() {
                return this.sp500Hourly.filter((item) => item.recommended);
            },

            get filteredTrades() {
                const needle = this.search.trim().toLocaleLowerCase();
                const filtered = this.trades.filter((trade) => {
                    const matchesSearch = !needle || trade.ticker.toLocaleLowerCase().includes(needle)
                        || trade.market_category.toLocaleLowerCase().includes(needle);
                    return matchesSearch
                        && (!this.categoryFilter || trade.market_category === this.categoryFilter)
                        && (!this.sideFilter || trade.side === this.sideFilter);
                });

                filtered.sort((left, right) => {
                    const a = left[this.sortKey] ?? "";
                    const b = right[this.sortKey] ?? "";
                    let comparison;
                    if (typeof a === "number" && typeof b === "number") {
                        comparison = a - b;
                    } else {
                        comparison = String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
                    }
                    return comparison * (this.sortDirection === "asc" ? 1 : -1);
                });
                return filtered;
            },

            get totalPages() {
                return Math.max(1, Math.ceil(this.filteredTrades.length / this.pageSize));
            },

            get paginatedTrades() {
                const start = (this.page - 1) * this.pageSize;
                return this.filteredTrades.slice(start, start + this.pageSize);
            },

            get paginationCaption() {
                const total = this.filteredTrades.length;
                if (!total) return "No trades to display";
                const start = (this.page - 1) * this.pageSize + 1;
                const end = Math.min(this.page * this.pageSize, total);
                return `Showing ${start.toLocaleString()}-${end.toLocaleString()} of ${total.toLocaleString()}`;
            },

            sortBy(key) {
                if (this.sortKey === key) {
                    this.sortDirection = this.sortDirection === "asc" ? "desc" : "asc";
                } else {
                    this.sortKey = key;
                    this.sortDirection = key === "close_timestamp" ? "desc" : "asc";
                }
                this.page = 1;
            },

            sortIndicator(key) {
                if (this.sortKey !== key) return "↕";
                return this.sortDirection === "asc" ? "↑" : "↓";
            },

            formatCurrency(value) {
                return `$${Number(value || 0).toFixed(2)}`;
            },

            formatPnl(value) {
                if (value === null || value === undefined) return "N/A";
                const number = Number(value);
                return `${number < 0 ? "-" : "+"}$${Math.abs(number).toFixed(2)}`;
            },

            formatPercent(value) {
                return `${Number(value || 0).toFixed(1)}%`;
            },

            formatSp500Price(value) {
                return value == null ? "N/A" : Number(value).toLocaleString(undefined, {
                    minimumFractionDigits: 1,
                    maximumFractionDigits: 1,
                });
            },

            pnlClass(value) {
                return Number(value) < 0 ? "negative-text" : "positive-text";
            },

            formatDate(value) {
                if (!value) return "—";
                const date = new Date(value);
                if (Number.isNaN(date.getTime())) return value;
                return date.toLocaleString(undefined, {
                    year: "numeric", month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit",
                });
            },

            marketBarStyle(value) {
                const maxValue = Math.max(...this.markets.map((market) => Math.abs(market.net_pnl)), 0.01);
                const width = Math.max(Math.abs(value) / maxValue * 48, 1);
                const left = value >= 0 ? 50 : 50 - width;
                return `left: ${left}%; width: ${width}%;`;
            },

            recordWidth(value) {
                const total = this.summary.trade_count;
                return `width: ${total ? (value / total * 100) : 0}%;`;
            },
        };
    };
})();
