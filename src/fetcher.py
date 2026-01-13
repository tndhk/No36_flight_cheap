"""Flight data fetcher using SerpAPI (Google Flights)."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from serpapi import Client as SerpApiClient


@dataclass
class FlightData:
    """Container for flight search results."""

    from_airport: str
    to_airport: str
    departure_date: str
    flights: List[Dict[str, Any]] = field(default_factory=list)
    return_date: Optional[str] = None

    def get_summary(self) -> str:
        """Generate a summary of flight data for LLM analysis.

        Returns:
            Formatted string with flight information.
        """
        summary = f"Flight Search: {self.from_airport} → {self.to_airport}\n"
        summary += f"Departure: {self.departure_date}\n"
        if self.return_date:
            summary += f"Return: {self.return_date}\n"

        if self.flights:
            summary += "\nAvailable Flights:\n"
            for i, flight in enumerate(self.flights, 1):
                airline = flight.get("airline", "Unknown")
                price = flight.get("price", "N/A")
                departure = flight.get("departure_time", "")
                arrival = flight.get("arrival_time", "")
                summary += f"  {i}. {airline}: ${price}"
                if departure and arrival:
                    summary += f" ({departure} - {arrival})"
                summary += "\n"
        else:
            summary += "\nNo flights found.\n"

        return summary

    def __str__(self) -> str:
        """String representation of flight data."""
        return self.get_summary()


class FlightFetcher:
    """Fetch flight data from SerpAPI (Google Flights)."""

    def __init__(self, api_key: str):
        """Initialize FlightFetcher.

        Args:
            api_key: SerpAPI API key.

        Raises:
            ValueError: If api_key is empty or None.
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_key = api_key
        self.client = SerpApiClient(api_key=api_key)

    def search_flights(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: str,
        return_date: Optional[str] = None,
        include_nearby: bool = False,
    ) -> FlightData:
        """Search for flights.

        Args:
            from_airport: Departure airport code (e.g., "TYO").
            to_airport: Arrival airport code (e.g., "LAX").
            departure_date: Departure date (YYYY-MM-DD).
            return_date: Optional return date (YYYY-MM-DD).
            include_nearby: Include nearby airports in search.

        Returns:
            FlightData object with search results.

        Raises:
            Exception: If API call fails.
        """
        # Build search parameters
        params = {
            "engine": "google_flights",
            "departure_id": from_airport,
            "arrival_id": to_airport,
            "outbound_date": departure_date,
            "currency": "USD",
            "hl": "en",
        }

        if return_date:
            params["return_date"] = return_date

        # Execute search
        try:
            response = self.client.search(params)
        except Exception as e:
            raise Exception(f"SerpAPI request failed: {str(e)}")

        # Parse response
        flights = self._parse_response(response)

        return FlightData(
            from_airport=from_airport,
            to_airport=to_airport,
            departure_date=departure_date,
            return_date=return_date,
            flights=flights,
        )

    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse SerpAPI response.

        Args:
            response: Raw response from SerpAPI.

        Returns:
            List of parsed flight dictionaries.
        """
        flights = []

        # Extract best flights
        best_flights = response.get("best_flights", [])
        for flight_group in best_flights:
            flight_legs = flight_group.get("flights", [])
            if flight_legs:
                # Use first leg as primary flight info
                first_leg = flight_legs[0]
                flight_info = {
                    "airline": first_leg.get("airline", "Unknown"),
                    "price": flight_group.get("price", 0),
                    "departure_time": first_leg.get("departure_time", ""),
                    "arrival_time": first_leg.get("arrival_time", ""),
                    "duration": flight_group.get("total_duration", 0),
                    "stops": len(flight_legs) - 1,
                }
                flights.append(flight_info)

        return flights

    def search_nearby_airports(
        self,
        from_airport: str,
        to_airport: str,
        departure_date: str,
        radius_km: int = 100,
    ) -> List[FlightData]:
        """Search nearby airports for cheaper options.

        Args:
            from_airport: Primary departure airport code.
            to_airport: Primary arrival airport code.
            departure_date: Departure date (YYYY-MM-DD).
            radius_km: Search radius in kilometers.

        Returns:
            List of FlightData objects for nearby airport combinations.
        """
        # This would require mapping airport codes to nearby airports
        # For now, return empty list as placeholder
        results = []

        # Example: Could implement with airport database lookup
        # nearby_from = self._get_nearby_airports(from_airport, radius_km)
        # nearby_to = self._get_nearby_airports(to_airport, radius_km)
        # for f in nearby_from:
        #     for t in nearby_to:
        #         result = self.search_flights(f, t, departure_date)
        #         results.append(result)

        return results
