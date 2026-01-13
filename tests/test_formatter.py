"""Test suite for formatter module (output formatting)."""

import pytest
from io import StringIO
from src.formatter import ReportFormatter
from src.analyzer import AnalysisResult


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

    def test_format_analysis_result(self):
        """Test formatting a single analysis result."""
        formatter = ReportFormatter()
        result = AnalysisResult(
            prompt_id=1, prompt_name="Test Prompt", analysis="Test analysis text"
        )

        formatted = formatter.format_analysis(result)
        assert "Test Prompt" in formatted
        assert "Test analysis text" in formatted

    def test_format_multiple_results(self):
        """Test formatting multiple analysis results."""
        formatter = ReportFormatter()
        results = [
            AnalysisResult(
                prompt_id=1, prompt_name="Prompt 1", analysis="Analysis 1"
            ),
            AnalysisResult(
                prompt_id=2, prompt_name="Prompt 2", analysis="Analysis 2"
            ),
            AnalysisResult(
                prompt_id=3, prompt_name="Prompt 3", analysis="Analysis 3"
            ),
        ]

        formatted = formatter.format_all_analyses(results)
        assert "Prompt 1" in formatted
        assert "Prompt 2" in formatted
        assert "Prompt 3" in formatted
        assert "Analysis 1" in formatted
        assert "Analysis 2" in formatted
        assert "Analysis 3" in formatted

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


class TestReportFormatting:
    """Test complete report formatting."""

    def test_format_complete_report(self):
        """Test formatting a complete report."""
        formatter = ReportFormatter()

        header = formatter.format_header("TYO", "LAX", "2025-03-01")
        results = [
            AnalysisResult(
                prompt_id=i, prompt_name=f"Prompt {i}", analysis=f"Analysis {i}"
            )
            for i in range(1, 4)
        ]
        analyses = formatter.format_all_analyses(results)
        summary = formatter.format_summary(total_prompts=3, execution_time=2.0)

        report = f"{header}\n{analyses}\n{summary}"

        assert "TYO" in report
        assert "LAX" in report
        assert "Prompt 1" in report
        assert "Prompt 2" in report
        assert "Prompt 3" in report

    def test_format_preserves_analysis_order(self):
        """Test that formatting preserves analysis order."""
        formatter = ReportFormatter()
        results = [
            AnalysisResult(prompt_id=i, prompt_name=f"Prompt {i}", analysis=f"A{i}")
            for i in range(1, 8)
        ]

        formatted = formatter.format_all_analyses(results)

        # Check that prompts appear in order
        idx_p1 = formatted.find("Prompt 1")
        idx_p2 = formatted.find("Prompt 2")
        idx_p7 = formatted.find("Prompt 7")

        assert idx_p1 < idx_p2 < idx_p7
