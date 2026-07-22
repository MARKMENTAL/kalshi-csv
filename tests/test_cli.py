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
