"""Command-line interface for Flight Cheap."""

import click
import time
from src.fetcher import FlightFetcher
from src.formatter import ReportFormatter
from src.prompts import format_prompts_for_claude
from rich.console import Console
from rich.table import Table


def main_search(
    from_airport: str,
    to_airport: str,
    departure_date: str,
    return_date: str = None,
    headless: bool = True,
) -> None:
    """Execute flight search and display results for Claude Code analysis.

    Args:
        from_airport: Departure airport code.
        to_airport: Arrival airport code.
        departure_date: Departure date (YYYY-MM-DD).
        return_date: Optional return date.
        headless: Run browser in headless mode (default: True).
    """
    console = Console()
    formatter = ReportFormatter()

    start_time = time.time()

    try:
        # Step 1: Fetch flight data using Playwright
        formatter.display_loading("Fetching flight data from Google Flights...")

        with FlightFetcher(headless=headless) as fetcher:
            flight_data = fetcher.search_flights(
                from_airport=from_airport,
                to_airport=to_airport,
                departure_date=departure_date,
                return_date=return_date,
            )

        execution_time = time.time() - start_time

        # Step 2: Display flight results in Rich table
        console.print(f"\n[green]Flight data fetched successfully in {execution_time:.2f}s[/green]\n")

        if flight_data.flights:
            table = Table(title=f"Flights: {from_airport} → {to_airport}")
            table.add_column("No.", style="cyan", width=4)
            table.add_column("Airline", style="magenta")
            table.add_column("Price", style="green", justify="right")
            table.add_column("Departure", style="blue")
            table.add_column("Arrival", style="blue")
            table.add_column("Duration", style="yellow")
            table.add_column("Stops", justify="center")

            for i, flight in enumerate(flight_data.flights, 1):
                table.add_row(
                    str(i),
                    flight.get("airline", "Unknown"),
                    flight.get("price", "N/A"),
                    flight.get("departure_time", ""),
                    flight.get("arrival_time", ""),
                    flight.get("duration", ""),
                    str(flight.get("stops", 0)),
                )

            console.print(table)
        else:
            console.print("[yellow]No flights found.[/yellow]")

        # Step 3: Display flight data summary for copy-paste
        console.print("\n[bold cyan]FLIGHT DATA FOR CLAUDE CODE ANALYSIS[/bold cyan]")
        console.print("=" * 80)
        console.print(flight_data.get_summary())
        console.print("=" * 80)

        # Step 4: Display analysis prompts for Claude Code
        console.print(format_prompts_for_claude())

    except Exception as e:
        formatter.display_error(str(e))
        raise


@click.command()
@click.option(
    "--from",
    "-f",
    "from_airport",
    required=True,
    help="Departure airport code (e.g., TYO, JFK)",
)
@click.option(
    "--to",
    "-t",
    "to_airport",
    required=True,
    help="Arrival airport code (e.g., LAX, LHR)",
)
@click.option(
    "--date",
    "-d",
    "departure_date",
    required=True,
    help="Departure date (YYYY-MM-DD)",
)
@click.option(
    "--return",
    "-r",
    "return_date",
    default=None,
    help="Return date (YYYY-MM-DD, optional)",
)
@click.option(
    "--visible",
    "-v",
    "visible",
    is_flag=True,
    help="Run browser in visible mode (default: headless)",
)
def search_command(
    from_airport: str,
    to_airport: str,
    departure_date: str,
    return_date: str = None,
    visible: bool = False,
) -> None:
    """Search for flights and display data for Claude Code analysis.

    Example:
        flight-cheap search --from TYO --to LAX --date 2025-03-01
        flight-cheap search -f NRT -t SFO -d 2025-03-15 -r 2025-03-22
        flight-cheap search -f TYO -t LAX -d 2025-03-01 --visible
    """
    main_search(
        from_airport=from_airport,
        to_airport=to_airport,
        departure_date=departure_date,
        return_date=return_date,
        headless=not visible,
    )


@click.group()
def cli():
    """Flight Cheap - Find the cheapest flights with AI analysis."""
    pass


# Register commands
cli.add_command(search_command, name="search")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
