"""Test suite for formatter module (output formatting)."""

import pytest
from io import StringIO
from src.formatter import ReportFormatter


class TestReportFormatter:
    """Test ReportFormatter class."""

    def test_formatter_initialization(self):
        """Test ReportFormatter can be initialized."""
        formatter = ReportFormatter()
        assert formatter is not None

    def test_format_header(self):
        """Test formatting report header."""
        formatter = ReportFormatter()
        header = formatter.format_header(
            from_airport="TYO", to_airport="LAX", departure_date="2025-03-01"
        )
        assert "TYO" in header
        assert "LAX" in header
        assert "2025-03-01" in header

    def test_format_summary(self):
        """Test formatting summary section."""
        formatter = ReportFormatter()
        summary = formatter.format_summary(
            total_prompts=7,
            execution_time=5.5,
        )
        assert "7" in summary or "total" in summary.lower()

    def test_formatter_output_is_string(self):
        """Test formatter output is string."""
        formatter = ReportFormatter()
        header = formatter.format_header("TYO", "LAX", "2025-03-01")
        assert isinstance(header, str)
        assert len(header) > 0

    def test_format_with_return_date(self):
        """Test formatting with return date."""
        formatter = ReportFormatter()
        header = formatter.format_header(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            return_date="2025-03-15",
        )
        assert "TYO" in header
        assert "LAX" in header
        assert "2025-03-01" in header
        assert "2025-03-15" in header
