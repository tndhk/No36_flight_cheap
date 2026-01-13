"""Test suite for fetcher module (SerpAPI integration)."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.fetcher import FlightFetcher, FlightData


class TestFlightData:
    """Test FlightData class."""

    def test_flight_data_initialization(self):
        """Test FlightData can be initialized."""
        data = FlightData(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            flights=[{"airline": "JAL", "price": 1200}],
        )
        assert data.from_airport == "TYO"
        assert data.to_airport == "LAX"
        assert data.departure_date == "2025-03-01"
        assert len(data.flights) == 1

    def test_flight_data_with_return_flight(self):
        """Test FlightData with return flight."""
        data = FlightData(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            return_date="2025-03-15",
            flights=[],
        )
        assert data.return_date == "2025-03-15"

    def test_flight_data_to_string(self):
        """Test FlightData can be converted to string."""
        data = FlightData(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            flights=[{"airline": "JAL", "price": 1200}],
        )
        result = str(data)
        assert "TYO" in result
        assert "LAX" in result
        assert "2025-03-01" in result


class TestFlightFetcher:
    """Test FlightFetcher class."""

    def test_flight_fetcher_initialization(self):
        """Test FlightFetcher can be initialized."""
        fetcher = FlightFetcher(api_key="test_key")
        assert fetcher.api_key == "test_key"

    @patch("src.fetcher.SerpApiClient")
    def test_search_flights_returns_flight_data(self, mock_serpapi):
        """Test search_flights returns FlightData."""
        mock_client = MagicMock()
        mock_serpapi.return_value = mock_client

        mock_response = {
            "best_flights": [
                {
                    "flights": [
                        {
                            "airline": "JAL",
                            "departure_airport": {"name": "TYO"},
                            "arrival_airport": {"name": "LAX"},
                            "price": 1200,
                        }
                    ]
                }
            ]
        }
        mock_client.search.return_value = mock_response

        fetcher = FlightFetcher(api_key="test_key")
        result = fetcher.search_flights(
            from_airport="TYO", to_airport="LAX", departure_date="2025-03-01"
        )

        assert isinstance(result, FlightData)
        assert result.from_airport == "TYO"
        assert result.to_airport == "LAX"

    @patch("src.fetcher.SerpApiClient")
    def test_search_flights_with_return_date(self, mock_serpapi):
        """Test search_flights with return date."""
        mock_client = MagicMock()
        mock_serpapi.return_value = mock_client
        mock_client.search.return_value = {
            "best_flights": [],
            "return_flights": [],
        }

        fetcher = FlightFetcher(api_key="test_key")
        result = fetcher.search_flights(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            return_date="2025-03-15",
        )

        assert result.return_date == "2025-03-15"

    @patch("src.fetcher.SerpApiClient")
    def test_search_flights_empty_result(self, mock_serpapi):
        """Test search_flights with empty result."""
        mock_client = MagicMock()
        mock_serpapi.return_value = mock_client
        mock_client.search.return_value = {"best_flights": []}

        fetcher = FlightFetcher(api_key="test_key")
        result = fetcher.search_flights(
            from_airport="TYO", to_airport="LAX", departure_date="2025-03-01"
        )

        assert isinstance(result, FlightData)
        assert len(result.flights) == 0

    @patch("src.fetcher.SerpApiClient")
    def test_search_nearby_airports(self, mock_serpapi):
        """Test searching with nearby airports option."""
        mock_client = MagicMock()
        mock_serpapi.return_value = mock_client
        mock_client.search.return_value = {"best_flights": []}

        fetcher = FlightFetcher(api_key="test_key")
        result = fetcher.search_flights(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            include_nearby=True,
        )

        assert isinstance(result, FlightData)
        # The mock should have been called
        assert mock_client.search.called

    @patch("src.fetcher.SerpApiClient")
    def test_search_flights_api_error(self, mock_serpapi):
        """Test search_flights handles API errors gracefully."""
        mock_client = MagicMock()
        mock_serpapi.return_value = mock_client
        mock_client.search.side_effect = Exception("API Error")

        fetcher = FlightFetcher(api_key="test_key")

        with pytest.raises(Exception) as exc_info:
            fetcher.search_flights(
                from_airport="TYO", to_airport="LAX", departure_date="2025-03-01"
            )

        assert "API Error" in str(exc_info.value)

    def test_flight_fetcher_requires_api_key(self):
        """Test FlightFetcher requires API key."""
        with pytest.raises((ValueError, TypeError)):
            FlightFetcher(api_key=None)

    def test_flight_fetcher_with_empty_api_key(self):
        """Test FlightFetcher with empty API key."""
        with pytest.raises(ValueError):
            FlightFetcher(api_key="")


class TestFlightDataFormatting:
    """Test FlightData formatting for LLM analysis."""

    def test_flight_data_summary_format(self):
        """Test FlightData generates summary suitable for LLM."""
        data = FlightData(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            flights=[
                {
                    "airline": "JAL",
                    "price": 1200,
                    "departure_time": "10:00",
                    "arrival_time": "13:00",
                }
            ],
        )

        summary = data.get_summary()
        assert isinstance(summary, str)
        assert "TYO" in summary
        assert "LAX" in summary
        assert "JAL" in summary
        assert "1200" in summary

    def test_flight_data_multiple_flights(self):
        """Test FlightData with multiple flight options."""
        data = FlightData(
            from_airport="TYO",
            to_airport="LAX",
            departure_date="2025-03-01",
            flights=[
                {"airline": "JAL", "price": 1200},
                {"airline": "ANA", "price": 1100},
                {"airline": "UAL", "price": 1050},
            ],
        )

        assert len(data.flights) == 3
        summary = data.get_summary()
        assert "JAL" in summary
        assert "ANA" in summary
        assert "UAL" in summary
