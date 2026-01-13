"""Flight data fetcher using Playwright (Google Flights scraper)."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page


@dataclass
class FlightData:
    """Container for flight search results."""

    from_airport: str
    to_airport: str
    departure_date: str
    flights: List[Dict[str, Any]] = field(default_factory=list)
    return_date: Optional[str] = None

    def get_summary(self) -> str:
        """Generate a summary of flight data for analysis.

        Returns:
            Formatted string with flight information.
        """
        summary = f"Flight Search: {self.from_airport} → {self.to_airport}\n"
        summary += f"Departure: {self.departure_date}\n"
        if self.return_date:
            summary += f"Return: {self.return_date}\n"

        if self.flights:
            summary += f"\nFound {len(self.flights)} flights:\n"
            for i, flight in enumerate(self.flights, 1):
                airline = flight.get("airline", "Unknown")
                price = flight.get("price", "N/A")
                departure = flight.get("departure_time", "")
                arrival = flight.get("arrival_time", "")
                duration = flight.get("duration", "")
                stops = flight.get("stops", 0)

                summary += f"\n  Flight {i}:\n"
                summary += f"    Airline: {airline}\n"
                summary += f"    Price: {price}\n"
                summary += f"    Time: {departure} - {arrival}\n"
                summary += f"    Duration: {duration}\n"
                summary += f"    Stops: {stops}\n"
        else:
            summary += "\nNo flights found.\n"

        return summary

    def __str__(self) -> str:
        """String representation of flight data."""
        return self.get_summary()


class FlightFetcher:
    """Fetch flight data from Google Flights using Playwright."""

    def __init__(self, headless: bool = True):
        """Initialize FlightFetcher.

        Args:
            headless: Run browser in headless mode (default: True).
        """
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None

    def _launch_browser(self) -> Browser:
        """Launch Playwright browser.

        Returns:
            Browser instance.
        """
        # Check if browser is connected, not just if it exists
        if self._browser is None or not self._browser.is_connected():
            # Clean up old playwright instance if it exists
            if self._playwright:
                try:
                    self._playwright.stop()
                except:
                    pass  # Already stopped
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
        return self._browser

    def close(self):
        """Close browser and cleanup resources."""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
