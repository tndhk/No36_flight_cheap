"""Output formatting for flight analysis reports."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


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
