"""Command-line interface for Flight Cheap."""

import click
import os
import time
from dotenv import load_dotenv
from src.fetcher import FlightFetcher
from src.analyzer import FlightAnalyzer
from src.formatter import ReportFormatter


# Load environment variables
load_dotenv()


def main_search(
    from_airport: str,
    to_airport: str,
    departure_date: str,
    return_date: str = None,
    include_nearby: bool = False,
) -> None:
    """Execute flight search and analysis.

    Args:
        from_airport: Departure airport code.
        to_airport: Arrival airport code.
        departure_date: Departure date (YYYY-MM-DD).
        return_date: Optional return date.
        include_nearby: Include nearby airports.
    """
    # Initialize components
    serpapi_key = os.getenv("SERPAPI_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not serpapi_key or not gemini_key:
        raise ValueError(
            "Missing API keys. Please set SERPAPI_KEY and GEMINI_API_KEY in .env"
        )

    formatter = ReportFormatter()
    fetcher = FlightFetcher(api_key=serpapi_key)
    analyzer = FlightAnalyzer(api_key=gemini_key)

    start_time = time.time()

    try:
        # Step 1: Fetch flight data
        formatter.display_loading("Fetching flight data from Google Flights...")
        flight_data = fetcher.search_flights(
            from_airport=from_airport,
            to_airport=to_airport,
            departure_date=departure_date,
            return_date=return_date,
            include_nearby=include_nearby,
        )

        # Step 2: Analyze with all 7 prompts
        formatter.display_loading("Running 7 analysis prompts (this may take a moment)...")
        flight_data_str = flight_data.get_summary()
        results = analyzer.analyze_flights_sync(flight_data_str)

        # Step 3: Display report
        execution_time = time.time() - start_time
        formatter.display_report(
            from_airport=from_airport,
            to_airport=to_airport,
            departure_date=departure_date,
            results=results,
            execution_time=execution_time,
            return_date=return_date,
        )

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
    "--nearby",
    "-n",
    "include_nearby",
    is_flag=True,
    help="Include nearby airports in search",
)
def search_command(
    from_airport: str,
    to_airport: str,
    departure_date: str,
    return_date: str = None,
    include_nearby: bool = False,
) -> None:
    """Search for flights and analyze prices.

    Example:
        flight-cheap search --from TYO --to LAX --date 2025-03-01
        flight-cheap search -f NRT -t SFO -d 2025-03-15 --nearby
    """
    main_search(
        from_airport=from_airport,
        to_airport=to_airport,
        departure_date=departure_date,
        return_date=return_date,
        include_nearby=include_nearby,
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
