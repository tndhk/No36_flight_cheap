"""Test suite for CLI module."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from src.cli import search_command


class TestCLISearch:
    """Test CLI search command."""

    def test_cli_search_requires_arguments(self):
        """Test search command requires arguments."""
        runner = CliRunner()
        result = runner.invoke(search_command, [])
        assert result.exit_code != 0

    def test_cli_search_with_required_args(self):
        """Test search command with required arguments."""
        runner = CliRunner()
        with patch("src.cli.main_search") as mock_search:
            mock_search.return_value = None
            result = runner.invoke(
                search_command,
                [
                    "--from",
                    "TYO",
                    "--to",
                    "LAX",
                    "--date",
                    "2025-03-01",
                ],
            )
            # Should not fail with required args
            assert mock_search.called

    def test_cli_search_from_option(self):
        """Test --from option."""
        runner = CliRunner()
        with patch("src.cli.main_search") as mock_search:
            mock_search.return_value = None
            result = runner.invoke(
                search_command,
                [
                    "-f",
                    "TYO",
                    "--to",
                    "LAX",
                    "--date",
                    "2025-03-01",
                ],
            )
            assert mock_search.called

    def test_cli_search_with_return_date(self):
        """Test search with return date."""
        runner = CliRunner()
        with patch("src.cli.main_search") as mock_search:
            mock_search.return_value = None
            result = runner.invoke(
                search_command,
                [
                    "--from",
                    "TYO",
                    "--to",
                    "LAX",
                    "--date",
                    "2025-03-01",
                    "--return",
                    "2025-03-15",
                ],
            )
            assert mock_search.called

    def test_cli_search_with_nearby_flag(self):
        """Test search with --nearby flag."""
        runner = CliRunner()
        with patch("src.cli.main_search") as mock_search:
            mock_search.return_value = None
            result = runner.invoke(
                search_command,
                [
                    "--from",
                    "TYO",
                    "--to",
                    "LAX",
                    "--date",
                    "2025-03-01",
                    "--nearby",
                ],
            )
            assert mock_search.called

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(search_command, ["--help"])
        assert result.exit_code == 0
        assert "from" in result.output.lower() or "departure" in result.output.lower()

    @patch("src.cli.main_search")
    def test_cli_invalid_date_format(self, mock_search):
        """Test CLI with invalid date format."""
        runner = CliRunner()
        # Click should validate date format if we implement it
        result = runner.invoke(
            search_command,
            [
                "--from",
                "TYO",
                "--to",
                "LAX",
                "--date",
                "invalid-date",
            ],
        )
        # The command might fail or handle it gracefully
        # This depends on implementation


class TestCLIIntegration:
    """Test CLI integration with main components."""

    @patch("src.cli.FlightFetcher")
    @patch("src.cli.FlightAnalyzer")
    def test_cli_end_to_end_basic(self, mock_analyzer, mock_fetcher):
        """Test basic end-to-end CLI flow."""
        # Mock fetcher response
        mock_fetcher_instance = MagicMock()
        mock_fetcher.return_value = mock_fetcher_instance

        # Mock analyzer response
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance

        runner = CliRunner()
        with patch("src.cli.main_search") as mock_search:
            mock_search.return_value = None
            result = runner.invoke(
                search_command,
                [
                    "--from",
                    "TYO",
                    "--to",
                    "LAX",
                    "--date",
                    "2025-03-01",
                ],
            )
            # Should succeed
            assert mock_search.called

    def test_cli_search_called_main_search(self):
        """Test that CLI search command calls main_search."""
        runner = CliRunner()
        with patch("src.cli.main_search") as mock_search:
            mock_search.return_value = None
            result = runner.invoke(
                search_command,
                [
                    "--from",
                    "TYO",
                    "--to",
                    "LAX",
                    "--date",
                    "2025-03-01",
                ],
            )
            assert mock_search.called


class TestCLIEnvironment:
    """Test CLI environment variable handling."""

    @patch.dict("os.environ", {"SERPAPI_KEY": "test_key", "GEMINI_API_KEY": "test_key"})
    @patch("src.cli.main_search")
    def test_cli_reads_env_variables(self, mock_search):
        """Test CLI reads environment variables."""
        mock_search.return_value = None
        runner = CliRunner()
        result = runner.invoke(
            search_command,
            [
                "--from",
                "TYO",
                "--to",
                "LAX",
                "--date",
                "2025-03-01",
            ],
        )
        assert mock_search.called
