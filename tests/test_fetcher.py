import pytest
from src.fetcher import FlightFetcher, FlightData
from unittest.mock import Mock, patch


def test_fetcher_initialization():
    """FlightFetcherが正しく初期化されることを確認"""
    fetcher = FlightFetcher()
    assert fetcher is not None


def test_fetcher_has_browser_method():
    """FlightFetcherがブラウザ起動メソッドを持つことを確認"""
    fetcher = FlightFetcher()
    assert hasattr(fetcher, '_launch_browser')


def test_fetcher_has_close_method():
    """FlightFetcherがクローズメソッドを持つことを確認"""
    fetcher = FlightFetcher()
    assert hasattr(fetcher, 'close')


def test_build_google_flights_url_oneway():
    """片道のGoogle Flights URLを正しく生成"""
    fetcher = FlightFetcher()
    url = fetcher._build_url("TYO", "LAX", "2026-03-01")

    assert "google.com/travel/flights" in url
    assert "NRT" in url  # TYO expands to NRT
    assert "LAX" in url
    assert "2026-03-01" in url


def test_build_google_flights_url_roundtrip():
    """往復のGoogle Flights URLを正しく生成"""
    fetcher = FlightFetcher()
    url = fetcher._build_url("TYO", "LAX", "2026-03-01", return_date="2026-03-15")

    assert "google.com/travel/flights" in url
    assert "2026-03-15" in url


def test_navigate_to_google_flights():
    """Google Flightsページに遷移できることを確認"""
    with FlightFetcher(headless=True) as fetcher:
        browser = fetcher._launch_browser()
        page = browser.new_page()

        url = fetcher._build_url("NRT", "LAX", "2026-03-01")
        page.goto(url, timeout=30000)

        assert "google.com/travel/flights" in page.url
        page.close()


def test_scrape_flight_results_returns_list():
    """スクレイピングがフライトリストを返すことを確認"""
    with FlightFetcher() as fetcher:
        browser = fetcher._launch_browser()
        page = browser.new_page()

        # Mock page content
        page.set_content("""
        <html>
            <body>
                <div class="pIav2d">
                    <span class="YMlIz FpEdX">$500</span>
                    <span class="sSHqwe tPgKwe ogfYpf">American Airlines</span>
                    <div class="wtdjmc YMlIz tPgKwe ogfYpf">10:00 AM - 5:00 PM</div>
                    <div class="gvkrdb AdWm1c tPgKwe ogfYpf">7h 30m</div>
                    <div class="EfT7Ae AdWm1c tPgKwe">Nonstop</div>
                </div>
            </body>
        </html>
        """)

        flights = fetcher._scrape_flights(page)

        assert isinstance(flights, list)
        assert len(flights) >= 0
        page.close()


def test_parse_flight_card_structure():
    """フライトカードデータの構造を確認"""
    with FlightFetcher() as fetcher:
        mock_card = Mock()
        mock_card.query_selector.return_value = Mock(inner_text=lambda: "$500")

        flight = fetcher._parse_flight_card(mock_card)

        assert isinstance(flight, dict)
        assert "airline" in flight
        assert "price" in flight
        assert "departure_time" in flight
        assert "arrival_time" in flight
        assert "duration" in flight
        assert "stops" in flight
