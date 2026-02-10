"""Tests for CLI."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from monteplan.cli.main import cli


class TestCLI:
    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.3.0" in result.output

    def test_run_defaults(self) -> None:
        """Run with defaults and small path count."""
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--paths", "100", "--seed", "42"])
        assert result.exit_code == 0
        assert "Success probability" in result.output

    def test_run_with_config(self, tmp_path: Path) -> None:
        """Run with a config file."""
        golden = Path(__file__).parent / "golden" / "basic_retirement.json"
        runner = CliRunner()
        output_file = tmp_path / "results.json"
        result = runner.invoke(
            cli,
            ["run", "--config", str(golden), "--output", str(output_file), "--paths", "100"],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert "Success probability" in result.output

    def test_run_output_file(self, tmp_path: Path) -> None:
        """Results should be written to output file."""
        output_file = tmp_path / "out.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["run", "--paths", "50", "--seed", "1", "--output", str(output_file)],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        import json

        data = json.loads(output_file.read_text())
        assert "success_probability" in data
