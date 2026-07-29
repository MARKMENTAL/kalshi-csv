import subprocess
import sys
from pathlib import Path


def test_cli_runs_successfully(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "TESTMARKET-WIN" in result.stdout
    assert "TESTMARKET-LOSS" in result.stdout
    assert "Total Transactions Parsed: 3" in result.stdout
    assert "Fees" in result.stdout


def test_cli_irs_summary_output(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv],
        capture_output=True,
        text=True,
    )
    assert "IRS FORM 8949" in result.stdout
    assert "Box C" in result.stdout
    assert "Date Acquired:" in result.stdout
    assert "Date Sold:" in result.stdout
    assert "Gross Proceeds:" in result.stdout
    assert "Cost or Other Basis:" in result.stdout
    assert "Gain or (Loss):" in result.stdout


def test_cli_irs_file_creation(sample_csv, tmp_path):
    irs_file = tmp_path / "irs-output.txt"
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--irs-file", str(irs_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert irs_file.exists()
    
    content = irs_file.read_text()
    assert "IRS FORM 8949" in content
    assert "Box C" in content
    assert "Date Acquired:" in content
    assert "Date Sold:" in content
    assert "Gross Proceeds:" in content
    assert "Cost or Other Basis:" in content
    assert "Gain or (Loss):" in content
    assert "\033[" not in content


def test_cli_no_color_flag(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "\033[" not in result.stdout


def test_cli_missing_file():
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", "/nonexistent/file.csv"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


def test_cli_ticker_truncation(tmp_path):
    csv_file = tmp_path / "long_ticker.csv"
    csv_file.write_text(
        "type,quantity_fp,market_ticker,side,entry_price_dollars,exit_price_dollars,"
        "open_fees_dollars,close_fees_dollars,realized_pnl_without_fees_dollars,"
        "realized_pnl_with_fees_dollars,close_timestamp,open_timestamp\n"
        "trade,1.00,VERYLONGTICKERNAME-THAT-EXCEEDS-THIRTY-CHARS,yes,0.50,1.00,"
        "0.01,0.02,0.50,0.47,2026-07-07T12:19:57-04:00,2026-07-07T09:48:19-04:00\n"
    )
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", str(csv_file), "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "VERYLONGTICKERNAME-THAT-EXCEE..." in result.stdout
    assert "VERYLONGTICKERNAME-THAT-EXCEEDS-THIRTY-CHARS" not in result.stdout


def test_cli_ascii_flag(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color", "--ascii"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "+" in result.stdout
    assert "-" in result.stdout
    assert "|" in result.stdout
    assert "┌" not in result.stdout
    assert "│" not in result.stdout


def test_cli_legacy_web_flag_in_help():
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--legacy-web" in result.stdout
    assert "--legacy-web-port" in result.stdout


def test_cli_legacy_web_port_default_in_help():
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "8080" in result.stdout


def test_cli_summary_cards_output(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "NET REALIZED P&L" in result.stdout
    assert "WIN / LOSS RECORD" in result.stdout
    assert "TOTAL VOLUME" in result.stdout
    assert "BEST/WORST SINGLE" in result.stdout


def test_cli_market_breakdown_output(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "ASSET CLASS / MARKET" in result.stdout
    assert "TRADES" in result.stdout
    assert "WIN RATE" in result.stdout
    assert "NET P&L" in result.stdout
    assert "Other Markets" in result.stdout


def test_cli_summary_cards_box_drawing(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "┌" in result.stdout
    assert "└" in result.stdout
    assert "┬" in result.stdout
    assert "┴" in result.stdout


def test_cli_summary_cards_before_irs(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout
    summary_pos = output.find("NET REALIZED P&L")
    irs_pos = output.find("IRS FORM 8949")
    assert summary_pos > 0
    assert irs_pos > 0
    assert summary_pos < irs_pos


def test_cli_market_breakdown_before_irs(sample_csv):
    result = subprocess.run(
        [sys.executable, "-m", "kalshi_csv.cli", sample_csv, "--no-color"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout
    market_pos = output.find("ASSET CLASS / MARKET")
    irs_pos = output.find("IRS FORM 8949")
    assert market_pos > 0
    assert irs_pos > 0
    assert market_pos < irs_pos
