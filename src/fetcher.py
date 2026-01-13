"""Flight data fetcher using Playwright (Google Flights scraper)."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page
import logging
import re

logger = logging.getLogger(__name__)


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

    def _expand_area_code(self, code: str) -> str:
        """Expand area code to specific airport.

        For Google Flights URLs, we use the first major airport.

        Args:
            code: Airport or area code.

        Returns:
            Specific airport code (uppercase).
        """
        area_to_airports = {
            "TYO": "NRT",  # Tokyo → Narita (primary)
            "NYC": "JFK",  # New York → JFK (primary)
            "LON": "LHR",  # London → Heathrow (primary)
            "PAR": "CDG",  # Paris → Charles de Gaulle (primary)
            "BER": "BER",  # Berlin
            "ROM": "FCO",  # Rome → Fiumicino (primary)
            "MIL": "MXP",  # Milan → Malpensa (primary)
        }
        return area_to_airports.get(code.upper(), code.upper())

    def _build_url(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: str,
        return_date: Optional[str] = None,
    ) -> str:
        """Build Google Flights URL.

        Args:
            from_airport: Departure airport code.
            to_airport: Arrival airport code.
            departure_date: Departure date (YYYY-MM-DD).
            return_date: Optional return date (YYYY-MM-DD).

        Returns:
            Google Flights URL.
        """
        from_code = self._expand_area_code(from_airport)
        to_code = self._expand_area_code(to_airport)

        if return_date:
            # Round-trip
            url = (
                f"https://www.google.com/travel/flights"
                f"?q=flights%20from%20{from_code}%20to%20{to_code}"
                f"%20on%20{departure_date}%20return%20{return_date}"
            )
        else:
            # One-way
            url = (
                f"https://www.google.com/travel/flights"
                f"?q=flights%20from%20{from_code}%20to%20{to_code}"
                f"%20on%20{departure_date}"
            )

        return url

    def _wait_for_results(self, page: Page, timeout: int = 30):
        """Wait for flight results to load.

        Args:
            page: Playwright page object.
            timeout: Timeout in seconds (default: 30).

        Raises:
            TimeoutError: If results don't load within timeout.
        """
        try:
            # Wait for flight result cards to appear
            page.wait_for_selector(".pIav2d", timeout=timeout * 1000)
            # Wait for network to be idle (dynamic content loaded)
            page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        except Exception as e:
            raise TimeoutError(f"Flight results did not load within {timeout}s: {str(e)}")

    def _parse_flight_card(self, card) -> Dict[str, Any]:
        """Parse a single flight card element.

        Args:
            card: Playwright element handle for flight card.

        Returns:
            Dictionary with flight information.
        """
        flight_info = {
            "airline": "Unknown",
            "price": "N/A",
            "departure_time": "",
            "arrival_time": "",
            "duration": "",
            "stops": 0,
        }

        try:
            # Price (e.g., "$500")
            price_elem = card.query_selector(".YMlIz.FpEdX, span[aria-label*='$']")
            if price_elem:
                price_text = price_elem.inner_text()
                flight_info["price"] = price_text.strip()

            # Airline name
            airline_elem = card.query_selector(".sSHqwe, .tPgKwe.ogfYpf")
            if airline_elem:
                flight_info["airline"] = airline_elem.inner_text().strip()

            # Time (e.g., "10:00 AM - 5:00 PM")
            time_elem = card.query_selector(".wtdjmc, div[aria-label*='Departure time']")
            if time_elem:
                time_text = time_elem.inner_text().strip()
                times = time_text.split("-")
                if len(times) == 2:
                    flight_info["departure_time"] = times[0].strip()
                    flight_info["arrival_time"] = times[1].strip()

            # Duration (e.g., "7h 30m")
            duration_elem = card.query_selector(".gvkrdb, div[aria-label*='Total duration']")
            if duration_elem:
                flight_info["duration"] = duration_elem.inner_text().strip()

            # Stops (e.g., "Nonstop", "1 stop", "2 stops")
            stops_elem = card.query_selector(".EfT7Ae, div[aria-label*='stop']")
            if stops_elem:
                stops_text = stops_elem.inner_text().strip().lower()
                if "nonstop" in stops_text:
                    flight_info["stops"] = 0
                else:
                    # Extract number from "1 stop", "2 stops", etc.
                    match = re.search(r"(\d+)", stops_text)
                    if match:
                        flight_info["stops"] = int(match.group(1))

        except Exception as e:
            # Log error but continue with partial data
            logger.warning(f"Error parsing flight card: {str(e)}")

        return flight_info

    def _scrape_flights(self, page: Page) -> List[Dict[str, Any]]:
        """Scrape flight data from Google Flights page.

        Args:
            page: Playwright page object.

        Returns:
            List of flight dictionaries.
        """
        flights = []

        try:
            # Find all flight result cards
            cards = page.query_selector_all(".pIav2d")

            for card in cards:
                flight = self._parse_flight_card(card)
                flights.append(flight)

        except Exception as e:
            logger.warning(f"Error scraping flights: {str(e)}")

        return flights

    def search_flights(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: str,
        return_date: Optional[str] = None,
    ) -> FlightData:
        """Search for flights on Google Flights.

        Args:
            from_airport: Departure airport code (e.g., "TYO", "NRT").
            to_airport: Arrival airport code (e.g., "LAX").
            departure_date: Departure date (YYYY-MM-DD).
            return_date: Optional return date (YYYY-MM-DD) for round-trip.

        Returns:
            FlightData object with search results.

        Raises:
            Exception: If scraping fails.
        """
        browser = self._launch_browser()
        page = browser.new_page()

        try:
            # Build URL and navigate
            url = self._build_url(from_airport, to_airport, departure_date, return_date)
            logger.info(f"Navigating to: {url}")
            page.goto(url, timeout=30000)

            # Wait for results to load
            logger.info("Waiting for flight results...")
            self._wait_for_results(page, timeout=30)

            # Scrape flight data
            logger.info("Scraping flight data...")
            flights = self._scrape_flights(page)
            logger.info(f"Found {len(flights)} flights")

            return FlightData(
                from_airport=from_airport,
                to_airport=to_airport,
                departure_date=departure_date,
                return_date=return_date,
                flights=flights,
            )

        except Exception as e:
            raise Exception(f"Flight search failed: {str(e)}") from e

        finally:
            page.close()
            # Note: Browser is NOT closed here because:
            # - FlightFetcher is designed to be used as a context manager
            # - Multiple search_flights() calls can reuse the same browser
            # - __exit__() handles browser cleanup when context ends
