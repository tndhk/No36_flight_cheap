"""Output formatting for flight analysis reports."""

from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.analyzer import AnalysisResult


class ReportFormatter:
    """Format flight analysis results for terminal output."""

    def __init__(self):
        """Initialize ReportFormatter."""
        self.console = Console()

    def format_header(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: str,
        return_date: Optional[str] = None,
    ) -> str:
        """Format report header with flight details.

        Args:
            from_airport: Departure airport code.
            to_airport: Arrival airport code.
            departure_date: Departure date.
            return_date: Optional return date.

        Returns:
            Formatted header string.
        """
        header = f"Flight Cheap Analysis: {from_airport} → {to_airport}\n"
        header += f"Departure: {departure_date}"
        if return_date:
            header += f" | Return: {return_date}"
        header += "\n" + "=" * 60

        return header

    def format_analysis(self, result: AnalysisResult) -> str:
        """Format a single analysis result.

        Args:
            result: AnalysisResult to format.

        Returns:
            Formatted analysis string.
        """
        output = f"\n[{result.prompt_name}]\n"
        output += "-" * 40 + "\n"
        output += result.analysis
        output += "\n"

        return output

    def format_all_analyses(self, results: List[AnalysisResult]) -> str:
        """Format all analysis results.

        Args:
            results: List of AnalysisResult objects.

        Returns:
            Formatted string with all analyses.
        """
        output = ""
        for result in results:
            output += self.format_analysis(result)

        return output

    def format_summary(
        self, total_prompts: int, execution_time: float
    ) -> str:
        """Format summary section.

        Args:
            total_prompts: Number of prompts executed.
            execution_time: Time taken for analysis.

        Returns:
            Formatted summary string.
        """
        summary = "\n" + "=" * 60 + "\n"
        summary += "SUMMARY\n"
        summary += "-" * 40 + "\n"
        summary += f"Total Analysis Prompts: {total_prompts}\n"
        summary += f"Execution Time: {execution_time:.2f}s\n"

        return summary

    def display_report(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: str,
        results: List[AnalysisResult],
        execution_time: float,
        return_date: Optional[str] = None,
    ) -> None:
        """Display complete report to console.

        Args:
            from_airport: Departure airport code.
            to_airport: Arrival airport code.
            departure_date: Departure date.
            results: List of analysis results.
            execution_time: Time taken for execution.
            return_date: Optional return date.
        """
        # Format all sections
        header = self.format_header(
            from_airport, to_airport, departure_date, return_date
        )
        analyses = self.format_all_analyses(results)
        summary = self.format_summary(len(results), execution_time)

        # Display using rich
        self.console.print(header, style="bold blue")
        self.console.print(analyses)
        self.console.print(summary, style="bold green")

    def display_loading(self, message: str = "Analyzing flights...") -> None:
        """Display loading message.

        Args:
            message: Loading message to display.
        """
        self.console.print(f"[yellow]{message}[/yellow]")

    def display_error(self, error_message: str) -> None:
        """Display error message.

        Args:
            error_message: Error message to display.
        """
        self.console.print(f"[red]Error: {error_message}[/red]")
