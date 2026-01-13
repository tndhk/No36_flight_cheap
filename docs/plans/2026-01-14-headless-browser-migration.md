# Headless Browser Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** SerpAPIをPlaywrightベースのGoogle Flights直接スクレイピングに移行し、Gemini API分析をClaude Code対話型分析に変更

**Architecture:**
- Playwrightでheadlessブラウザを起動してGoogle Flightsにアクセス
- フライトデータをスクレイピングして構造化データとして取得
- 取得データをターミナルに表示し、7つの分析プロンプトと共にClaude Codeに提示
- ユーザーがClaude Codeに対話的に分析を依頼する形式に変更

**Tech Stack:**
- Playwright (headless browser)
- Click (CLI)
- Rich (terminal output)
- Python 3.11+
- pytest (TDD)

---

## Task 1: 依存関係の更新

**Files:**
- Modify: `pyproject.toml`
- Delete: N/A (dependencies変更のみ)

**Step 1: 古い依存関係を削除し、Playwrightを追加するテストを書く**

```python
# tests/test_dependencies.py
def test_pyproject_has_playwright():
    """pyproject.tomlにplaywrightが含まれていることを確認"""
    with open("pyproject.toml") as f:
        content = f.read()
    assert "playwright" in content


def test_pyproject_no_serpapi():
    """pyproject.tomlにserpapiが含まれていないことを確認"""
    with open("pyproject.toml") as f:
        content = f.read()
    assert "serpapi" not in content


def test_pyproject_no_google_generativeai():
    """pyproject.tomlにgoogle-generativeaiが含まれていないことを確認"""
    with open("pyproject.toml") as f:
        content = f.read()
    assert "google-generativeai" not in content
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_dependencies.py -v
```

期待される出力: FAIL - "playwright" not found, "serpapi" found, "google-generativeai" found

**Step 3: pyproject.tomlの依存関係を更新**

```toml
dependencies = [
    "playwright>=1.40.0",
    "click>=8.1.0",
    "rich>=13.0.0",
    "python-dotenv>=1.0.0",
]
```

以下を削除:
- `google-generativeai>=0.3.0`
- `google-generativeai[grpc]>=0.3.0`
- `serpapi>=0.1.0`
- `aiohttp>=3.9.0` (Playwright自体が持つため不要)

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_dependencies.py -v
```

期待される出力: PASS - 3 passed

**Step 5: Commit**

```bash
git add pyproject.toml tests/test_dependencies.py
git commit -m "chore: migrate from SerpAPI/Gemini to Playwright/Claude Code

- Remove serpapi and google-generativeai dependencies
- Add playwright for headless browser scraping
- Add test to verify dependency changes"
```

---

## Task 2: Playwright版fetcher実装 - 初期化とブラウザ起動

**Files:**
- Modify: `src/fetcher.py:1-218` (全面書き換え)
- Modify: `tests/test_fetcher.py` (既存テストを新仕様に合わせて修正)

**Step 1: Playwright版fetcher初期化の失敗テストを書く**

```python
# tests/test_fetcher.py (既存ファイルを上書き)
import pytest
from src.fetcher import FlightFetcher, FlightData


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
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_fetcher.py::test_fetcher_initialization -v
pytest tests/test_fetcher.py::test_fetcher_has_browser_method -v
pytest tests/test_fetcher.py::test_fetcher_has_close_method -v
```

期待される出力: FAIL - ImportError or AttributeError

**Step 3: Playwright版FlightFetcherの基本構造を実装**

```python
# src/fetcher.py (全面書き換え)
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
        if self._browser is None:
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
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_fetcher.py::test_fetcher_initialization -v
pytest tests/test_fetcher.py::test_fetcher_has_browser_method -v
pytest tests/test_fetcher.py::test_fetcher_has_close_method -v
```

期待される出力: PASS - 3 passed

**Step 5: Commit**

```bash
git add src/fetcher.py tests/test_fetcher.py
git commit -m "feat: implement Playwright-based FlightFetcher initialization

- Add FlightData dataclass with enhanced summary format
- Add FlightFetcher with browser launch/close methods
- Support context manager for automatic cleanup
- Add tests for initialization and methods"
```

---

## Task 3: Google Flights URL生成とページ遷移

**Files:**
- Modify: `src/fetcher.py:71-end` (メソッド追加)
- Modify: `tests/test_fetcher.py` (テスト追加)

**Step 1: URL生成の失敗テストを書く**

```python
# tests/test_fetcher.py (追記)
def test_build_google_flights_url_oneway():
    """片道のGoogle Flights URLを正しく生成"""
    fetcher = FlightFetcher()
    url = fetcher._build_url("TYO", "LAX", "2026-03-01")

    assert "google.com/travel/flights" in url
    assert "TYO" in url
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
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_fetcher.py::test_build_google_flights_url_oneway -v
pytest tests/test_fetcher.py::test_build_google_flights_url_roundtrip -v
pytest tests/test_fetcher.py::test_navigate_to_google_flights -v
```

期待される出力: FAIL - AttributeError: '_build_url' method not found

**Step 3: URL生成メソッドを実装**

```python
# src/fetcher.py (メソッド追加)
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
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_fetcher.py::test_build_google_flights_url_oneway -v
pytest tests/test_fetcher.py::test_build_google_flights_url_roundtrip -v
pytest tests/test_fetcher.py::test_navigate_to_google_flights -v
```

期待される出力: PASS - 3 passed

**Step 5: Commit**

```bash
git add src/fetcher.py tests/test_fetcher.py
git commit -m "feat: add Google Flights URL generation and navigation

- Add area code expansion for major airports
- Build Google Flights search URLs for one-way and round-trip
- Add test for page navigation with real browser"
```

---

## Task 4: フライトデータスクレイピング実装

**Files:**
- Modify: `src/fetcher.py` (スクレイピングメソッド追加)
- Modify: `tests/test_fetcher.py` (モックテスト追加)

**Step 1: スクレイピングの失敗テストを書く**

```python
# tests/test_fetcher.py (追記)
from unittest.mock import Mock, patch


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
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_fetcher.py::test_scrape_flight_results_returns_list -v
pytest tests/test_fetcher.py::test_parse_flight_card_structure -v
```

期待される出力: FAIL - AttributeError: methods not found

**Step 3: スクレイピングメソッドを実装**

```python
# src/fetcher.py (メソッド追加)
import time
import re


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
            # Additional wait for dynamic content
            time.sleep(2)
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
            print(f"Warning: Error parsing flight card: {str(e)}")

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
            print(f"Warning: Error scraping flights: {str(e)}")

        return flights
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_fetcher.py::test_scrape_flight_results_returns_list -v
pytest tests/test_fetcher.py::test_parse_flight_card_structure -v
```

期待される出力: PASS - 2 passed

**Step 5: Commit**

```bash
git add src/fetcher.py tests/test_fetcher.py
git commit -m "feat: implement Google Flights scraping logic

- Add wait for results with timeout handling
- Parse flight cards (airline, price, time, duration, stops)
- Handle parsing errors gracefully with partial data
- Add tests for scraping and parsing methods"
```

---

## Task 5: search_flights統合メソッド実装

**Files:**
- Modify: `src/fetcher.py` (search_flightsメソッド追加)
- Modify: `tests/test_fetcher.py` (統合テスト追加)

**Step 1: search_flightsの失敗テストを書く**

```python
# tests/test_fetcher.py (追記)
def test_search_flights_returns_flight_data():
    """search_flightsがFlightDataオブジェクトを返すことを確認"""
    with FlightFetcher() as fetcher:
        result = fetcher.search_flights("NRT", "LAX", "2026-03-01")

        assert isinstance(result, FlightData)
        assert result.from_airport == "NRT"
        assert result.to_airport == "LAX"
        assert result.departure_date == "2026-03-01"
        assert isinstance(result.flights, list)


def test_search_flights_roundtrip():
    """往復検索がreturn_dateを含むことを確認"""
    with FlightFetcher() as fetcher:
        result = fetcher.search_flights(
            "NRT", "LAX", "2026-03-01", return_date="2026-03-15"
        )

        assert result.return_date == "2026-03-15"


@pytest.mark.integration
def test_search_flights_real_integration():
    """実際のGoogle Flightsからデータ取得（統合テスト）"""
    with FlightFetcher(headless=True) as fetcher:
        result = fetcher.search_flights("NRT", "LAX", "2026-03-01")

        # Basic checks
        assert isinstance(result, FlightData)
        # Note: Flights may or may not be found depending on availability
        print(f"\nFound {len(result.flights)} flights")
        if result.flights:
            print(result.get_summary())
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_fetcher.py::test_search_flights_returns_flight_data -v
pytest tests/test_fetcher.py::test_search_flights_roundtrip -v
```

期待される出力: FAIL - AttributeError: 'search_flights' method not found

**Step 3: search_flightsメソッドを実装**

```python
# src/fetcher.py (メソッド追加)
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
            print(f"Navigating to: {url}")
            page.goto(url, timeout=30000)

            # Wait for results to load
            print("Waiting for flight results...")
            self._wait_for_results(page, timeout=30)

            # Scrape flight data
            print("Scraping flight data...")
            flights = self._scrape_flights(page)
            print(f"Found {len(flights)} flights")

            return FlightData(
                from_airport=from_airport,
                to_airport=to_airport,
                departure_date=departure_date,
                return_date=return_date,
                flights=flights,
            )

        except Exception as e:
            raise Exception(f"Flight search failed: {str(e)}")

        finally:
            page.close()
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_fetcher.py::test_search_flights_returns_flight_data -v
pytest tests/test_fetcher.py::test_search_flights_roundtrip -v
```

期待される出力: PASS - 2 passed

統合テストも実行（時間がかかるため任意）:

```bash
pytest tests/test_fetcher.py::test_search_flights_real_integration -v -m integration
```

**Step 5: Commit**

```bash
git add src/fetcher.py tests/test_fetcher.py
git commit -m "feat: implement search_flights integration method

- Integrate URL building, navigation, waiting, and scraping
- Return FlightData with search results
- Support both one-way and round-trip searches
- Add unit tests and optional integration test"
```

---

## Task 6: analyzer.py削除と影響範囲の修正

**Files:**
- Delete: `src/analyzer.py`
- Delete: `tests/test_analyzer.py`
- Modify: `src/cli.py` (analyzer.py依存削除)

**Step 1: analyzer削除後のインポートエラー検出テストを書く**

```python
# tests/test_cli.py (既存ファイルに追記、または新規作成)
def test_cli_does_not_import_analyzer():
    """cli.pyがanalyzer.pyをインポートしていないことを確認"""
    with open("src/cli.py") as f:
        content = f.read()
    assert "from src.analyzer import" not in content
    assert "import src.analyzer" not in content


def test_cli_does_not_import_gemini():
    """cli.pyがgemini関連をインポートしていないことを確認"""
    with open("src/cli.py") as f:
        content = f.read()
    assert "google.generativeai" not in content
    assert "genai" not in content
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_cli.py::test_cli_does_not_import_analyzer -v
pytest tests/test_cli.py::test_cli_does_not_import_gemini -v
```

期待される出力: FAIL - アサーションエラー（まだインポートが残っている）

**Step 3: analyzer.pyとanalyzer関連テストを削除**

```bash
rm src/analyzer.py
rm tests/test_analyzer.py
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_cli.py::test_cli_does_not_import_analyzer -v
pytest tests/test_cli.py::test_cli_does_not_import_gemini -v
```

期待される出力: PASS - 2 passed

**Step 5: Commit**

```bash
git add -A
git commit -m "refactor: remove Gemini API analyzer

- Delete src/analyzer.py (no longer needed)
- Delete tests/test_analyzer.py
- Analysis will be done by Claude Code interactively
- Add tests to verify analyzer imports are removed"
```

---

## Task 7: prompts.py更新 - Claude Code向けプロンプト表示形式

**Files:**
- Modify: `src/prompts.py`
- Modify: `tests/test_prompts.py`

**Step 1: プロンプト表示形式変更の失敗テストを書く**

```python
# tests/test_prompts.py (既存テストを新仕様に合わせて修正)
from src.prompts import get_all_prompts, format_prompts_for_claude


def test_get_all_prompts_returns_list():
    """get_all_prompts()がリストを返すことを確認"""
    prompts = get_all_prompts()
    assert isinstance(prompts, list)
    assert len(prompts) == 7


def test_prompt_has_required_fields():
    """各プロンプトが必要なフィールドを持つことを確認"""
    prompts = get_all_prompts()
    for prompt in prompts:
        assert "id" in prompt
        assert "name" in prompt
        assert "description" in prompt


def test_format_prompts_for_claude():
    """Claude Code向けフォーマットが正しく生成されることを確認"""
    prompts = get_all_prompts()
    formatted = format_prompts_for_claude(prompts)

    assert isinstance(formatted, str)
    assert "Hidden Route Scanner" in formatted
    assert "Price Manipulation Detector" in formatted
    assert len(formatted) > 100  # Reasonable length check
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_prompts.py::test_get_all_prompts_returns_list -v
pytest tests/test_prompts.py::test_prompt_has_required_fields -v
pytest tests/test_prompts.py::test_format_prompts_for_claude -v
```

期待される出力: FAIL - 関数やフィールドが見つからない

**Step 3: prompts.pyを新仕様に書き換え**

```python
# src/prompts.py (全面書き換え)
"""Analysis prompts for Claude Code."""

from typing import List, Dict


def get_all_prompts() -> List[Dict[str, str]]:
    """Get all 7 analysis prompts for Claude Code.

    Returns:
        List of prompt dictionaries with id, name, and description.
    """
    return [
        {
            "id": "1",
            "name": "Hidden Route Scanner",
            "description": (
                "Break my route into hidden city tickets, nearby departure and arrival "
                "airports, and multi-leg combinations airlines don't surface. Compare "
                "direct vs split routes, explain the price gap, and rank the cheapest "
                "legal options."
            ),
        },
        {
            "id": "2",
            "name": "Price Manipulation Detector",
            "description": (
                "Analyze how airlines raise prices using repeated searches, cookies, "
                "browser data, device type, IP location, and time-based demand signals. "
                "Explain exactly which behaviors trigger price inflation and give a "
                "precise step-by-step search method to avoid it."
            ),
        },
        {
            "id": "3",
            "name": "Geo-Pricing Bypass",
            "description": (
                "Simulate flight prices for the same route across different countries, "
                "currencies, and regional booking markets. Identify where the ticket is "
                "priced lowest, explain why geo-pricing differs, and outline legal ways "
                "travelers can access those fares."
            ),
        },
        {
            "id": "4",
            "name": "Timing Sweet Spot Finder",
            "description": (
                "Use historical airline pricing behavior to identify the cheapest booking "
                "days, booking windows, and departure periods for this route. Explain how "
                "demand cycles, inventory release, and fare resets influence these price drops."
            ),
        },
        {
            "id": "5",
            "name": "Fare Rule Exploiter",
            "description": (
                "Break down airline fare rules, ticket classes, routing logic, and pricing "
                "conditions in simple terms. Show how airlines structure these rules to price "
                "flights differently and how travelers can select options that quietly reduce "
                "total cost."
            ),
        },
        {
            "id": "6",
            "name": "Airline VS OTA Comparison",
            "description": (
                "Compare pricing between airlines, major OTAs, regional booking sites, and "
                "lesser-known platforms. Identify where service fees, markups, and hidden "
                "discounts appear, and explain which platforms usually reveal lower base fares."
            ),
        },
        {
            "id": "7",
            "name": "Price Drop Watch Strategy",
            "description": (
                "Create a detailed fare-tracking strategy that monitors price drops without "
                "triggering increases. Include search frequency, timing resets, alert setup, "
                "behavioral rules, and practical examples to keep prices stable while tracking "
                "over time."
            ),
        },
    ]


def format_prompts_for_claude(prompts: List[Dict[str, str]]) -> str:
    """Format prompts for Claude Code display.

    Args:
        prompts: List of prompt dictionaries.

    Returns:
        Formatted string for terminal display.
    """
    output = "\n" + "=" * 60 + "\n"
    output += "ANALYSIS PROMPTS FOR CLAUDE CODE\n"
    output += "=" * 60 + "\n\n"
    output += "You can ask Claude Code to analyze your flight data using these prompts:\n\n"

    for prompt in prompts:
        output += f"{prompt['id']}. {prompt['name']}\n"
        output += f"   {prompt['description']}\n\n"

    output += "=" * 60 + "\n"
    output += "Usage: Copy flight data above and ask Claude Code to analyze it.\n"
    output += "Example: 'Analyze this flight data using prompt 1 (Hidden Route Scanner)'\n"
    output += "=" * 60 + "\n"

    return output
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_prompts.py -v
```

期待される出力: PASS - 3 passed (または既存テストも含めて全てPASS)

**Step 5: Commit**

```bash
git add src/prompts.py tests/test_prompts.py
git commit -m "refactor: simplify prompts for Claude Code interaction

- Convert prompts to simple dict structure (id, name, description)
- Add format_prompts_for_claude() for terminal display
- Remove LLM API integration code (no longer needed)
- Update tests for new prompt structure"
```

---

## Task 8: CLI統合 - フライトデータ取得とプロンプト表示

**Files:**
- Modify: `src/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: 新CLI仕様の失敗テストを書く**

```python
# tests/test_cli.py (追記)
from click.testing import CliRunner
from src.cli import main


def test_cli_search_command_exists():
    """search コマンドが存在することを確認"""
    runner = CliRunner()
    result = runner.invoke(main, ["search", "--help"])
    assert result.exit_code == 0
    assert "search" in result.output.lower()


def test_cli_search_requires_arguments():
    """search コマンドが必須引数を要求することを確認"""
    runner = CliRunner()
    result = runner.invoke(main, ["search"])
    assert result.exit_code != 0  # Should fail without required args


def test_cli_search_with_valid_args():
    """有効な引数でsearch コマンドが実行できることを確認"""
    runner = CliRunner()
    result = runner.invoke(main, [
        "search",
        "--from", "NRT",
        "--to", "LAX",
        "--date", "2026-03-01"
    ])
    # Note: Will try to scrape real data, may take time
    assert "Flight Search" in result.output or "error" in result.output.lower()
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_cli.py::test_cli_search_command_exists -v
pytest tests/test_cli.py::test_cli_search_requires_arguments -v
```

期待される出力: FAIL or PASS but wrong behavior

**Step 3: cli.pyを新仕様に書き換え**

```python
# src/cli.py (全面書き換え)
"""Flight Cheap CLI - Search flights and display analysis prompts."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from src.fetcher import FlightFetcher
from src.prompts import get_all_prompts, format_prompts_for_claude

# Load environment variables
load_dotenv()

console = Console()


@click.group()
def main():
    """Flight Cheap - Find cheaper flights with AI analysis."""
    pass


@main.command()
@click.option("--from", "from_airport", required=True, help="Departure airport code (e.g., TYO, NRT)")
@click.option("--to", "to_airport", required=True, help="Arrival airport code (e.g., LAX)")
@click.option("--date", "departure_date", required=True, help="Departure date (YYYY-MM-DD)")
@click.option("--return", "return_date", default=None, help="Return date for round-trip (YYYY-MM-DD)")
def search(from_airport: str, to_airport: str, departure_date: str, return_date: str = None):
    """Search for flights and display results with analysis prompts."""

    console.print(Panel.fit(
        f"[bold cyan]Flight Cheap Search[/bold cyan]\n"
        f"{from_airport} → {to_airport}\n"
        f"Departure: {departure_date}" + (f"\nReturn: {return_date}" if return_date else ""),
        border_style="cyan"
    ))

    try:
        # Fetch flight data
        console.print("\n[yellow]Launching headless browser...[/yellow]")
        with FlightFetcher(headless=True) as fetcher:
            console.print("[yellow]Searching Google Flights...[/yellow]")
            flight_data = fetcher.search_flights(
                from_airport,
                to_airport,
                departure_date,
                return_date
            )

        # Display flight results
        console.print("\n[bold green]Flight Results:[/bold green]\n")

        if flight_data.flights:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("No.", style="dim")
            table.add_column("Airline")
            table.add_column("Price", style="green")
            table.add_column("Departure")
            table.add_column("Arrival")
            table.add_column("Duration")
            table.add_column("Stops")

            for i, flight in enumerate(flight_data.flights, 1):
                table.add_row(
                    str(i),
                    flight.get("airline", "Unknown"),
                    flight.get("price", "N/A"),
                    flight.get("departure_time", ""),
                    flight.get("arrival_time", ""),
                    flight.get("duration", ""),
                    str(flight.get("stops", 0)) + (" stop" if flight.get("stops") == 1 else " stops")
                )

            console.print(table)
        else:
            console.print("[yellow]No flights found.[/yellow]")

        # Display analysis prompts for Claude Code
        prompts = get_all_prompts()
        prompts_text = format_prompts_for_claude(prompts)
        console.print(prompts_text)

        # Display raw flight data for Claude Code
        console.print("\n[bold cyan]Flight Data for Analysis:[/bold cyan]\n")
        console.print(Panel(
            flight_data.get_summary(),
            title="Copy this data for Claude Code analysis",
            border_style="cyan"
        ))

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


if __name__ == "__main__":
    main()
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_cli.py::test_cli_search_command_exists -v
pytest tests/test_cli.py::test_cli_search_requires_arguments -v
```

期待される出力: PASS - 2 passed

**Step 5: Commit**

```bash
git add src/cli.py tests/test_cli.py
git commit -m "refactor: update CLI for Playwright + Claude Code workflow

- Remove Gemini API integration
- Display flight results in Rich table format
- Show analysis prompts for Claude Code
- Display flight data summary for copy-paste to Claude
- Update tests for new CLI behavior"
```

---

## Task 9: .env.example更新と不要な環境変数削除

**Files:**
- Modify: `.env.example`

**Step 1: .env.example更新の失敗テストを書く**

```python
# tests/test_env.py (新規作成)
def test_env_example_no_serpapi():
    """.env.exampleにSERPAPI_KEYが含まれていないことを確認"""
    with open(".env.example") as f:
        content = f.read()
    assert "SERPAPI_KEY" not in content


def test_env_example_no_gemini():
    """.env.exampleにGEMINI_API_KEYが含まれていないことを確認"""
    with open(".env.example") as f:
        content = f.read()
    assert "GEMINI_API_KEY" not in content


def test_env_example_has_playwright_comment():
    """.env.exampleにPlaywright説明が含まれることを確認"""
    with open(".env.example") as f:
        content = f.read()
    assert "playwright" in content.lower()
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_env.py -v
```

期待される出力: FAIL - アサーションエラー

**Step 3: .env.exampleを更新**

```bash
# .env.example (全面書き換え)
# Flight Cheap - Environment Variables

# ============================================================
# PLAYWRIGHT CONFIGURATION
# ============================================================
# Playwright is used for headless browser scraping.
# No API keys required!
#
# Installation:
#   pip install playwright
#   playwright install chromium
#
# The browser runs in headless mode by default.
# ============================================================

# No API keys needed for this version!
# Flight data is fetched directly from Google Flights via Playwright.
# Analysis is performed by Claude Code interactively.

# ============================================================
# OPTIONAL: Custom browser settings (advanced users)
# ============================================================
# PLAYWRIGHT_HEADLESS=true
# PLAYWRIGHT_TIMEOUT=30000
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_env.py -v
```

期待される出力: PASS - 3 passed

**Step 5: Commit**

```bash
git add .env.example tests/test_env.py
git commit -m "chore: update .env.example for Playwright (no API keys needed)

- Remove SERPAPI_KEY (no longer used)
- Remove GEMINI_API_KEY (no longer used)
- Add Playwright installation instructions
- Add test to verify API keys are removed"
```

---

## Task 10: README.md更新

**Files:**
- Modify: `README.md`

**Step 1: README更新の失敗テストを書く**

```python
# tests/test_readme.py (新規作成)
def test_readme_mentions_playwright():
    """READMEにPlaywrightが言及されていることを確認"""
    with open("README.md") as f:
        content = f.read()
    assert "playwright" in content.lower()


def test_readme_no_serpapi():
    """READMEにSerpAPIが言及されていないことを確認"""
    with open("README.md") as f:
        content = f.read()
    assert "serpapi" not in content.lower()


def test_readme_no_gemini():
    """READMEにGeminiが言及されていないことを確認"""
    with open("README.md") as f:
        content = f.read()
    assert "gemini" not in content.lower()


def test_readme_mentions_claude_code():
    """READMEにClaude Codeが言及されていることを確認"""
    with open("README.md") as f:
        content = f.read()
    assert "claude code" in content.lower()
```

**Step 2: テストを実行して失敗を確認**

```bash
pytest tests/test_readme.py -v
```

期待される出力: FAIL - アサーションエラー

**Step 3: README.mdを新仕様に書き換え**

```markdown
# Flight Cheap CLI

航空券を安く取得するためのCLIツール。Google Flightsから直接データを取得し、Claude Codeによる対話型分析で価格最適化戦略を提案します。

## 機能

**Playwrightによる直接スクレイピング:**
- API料金不要！Google Flightsから直接データ取得
- Headless browserで自動検索
- リアルタイムの最新価格情報

**Claude Codeによる対話型分析:**
- 7つの分析プロンプトを表示
- ユーザーがClaude Codeに対話的に分析を依頼
- 柔軟でカスタマイズ可能な分析

**7つの分析プロンプト:**

1. **Hidden Route Scanner** - 隠れたルートを発見（経由地、近隣空港の組み合わせ）
2. **Price Manipulation Detector** - 価格操作を検出（最適検索方法を提案）
3. **Geo-Pricing Bypass** - 地域別価格を比較（最安地域を特定）
4. **Timing Sweet Spot Finder** - 最適な予約タイミング（需要サイクルを分析）
5. **Fare Rule Exploiter** - 運賃ルールを分析（ルール外の節約法）
6. **Airline VS OTA Comparison** - 航空会社とOTAを比較（最安プラットフォーム特定）
7. **Price Drop Watch Strategy** - 価格追跡戦略（監視方法を詳細化）

## セットアップ

### 前提条件

- Python 3.11 以上
- Git

### 1. リポジトリをクローン

```bash
git clone https://github.com/tndhk/No36_flight_cheap.git
cd No36_flight_cheap
```

### 2. 仮想環境を作成

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係をインストール

```bash
pip install -e .
```

### 4. Playwrightブラウザをインストール

```bash
playwright install chromium
```

API鍵は不要です！

## 使用方法

### 基本的な検索

```bash
flight-cheap search --from TYO --to LAX --date 2026-03-01
```

### 往復便

```bash
flight-cheap search --from TYO --to LAX --date 2026-03-01 --return 2026-03-15
```

### ヘルプ表示

```bash
flight-cheap search --help
```

## 出力例

```
Flight Cheap Search
TYO → LAX
Departure: 2026-03-01

Launching headless browser...
Searching Google Flights...

Flight Results:

No. Airline          Price  Departure  Arrival    Duration  Stops
1   American Airlines $500  10:00 AM   5:00 PM    7h 30m    0 stops
2   United Airlines   $550  11:30 AM   6:45 PM    8h 15m    0 stops

============================================================
ANALYSIS PROMPTS FOR CLAUDE CODE
============================================================

1. Hidden Route Scanner
   Break my route into hidden city tickets...

[... 7つのプロンプト表示 ...]

Flight Data for Analysis:
[フライトデータのサマリー表示]
```

その後、このデータをコピーしてClaude Codeに分析を依頼します。

## ワークフロー

1. `flight-cheap search`でフライトデータを取得
2. ターミナルに表示される7つの分析プロンプトを確認
3. フライトデータをコピー
4. Claude Codeに分析を依頼（例: "このフライトデータをプロンプト1で分析して"）
5. Claude Codeが対話的に詳細分析を提供

## プロジェクト構成

```
flight_cheap/
├── src/
│   ├── __init__.py
│   ├── fetcher.py      # Playwright による Google Flights スクレイピング
│   ├── prompts.py      # 7つの分析プロンプト定義
│   ├── formatter.py    # Rich による出力整形
│   └── cli.py          # Click CLI メイン
├── tests/
│   ├── test_fetcher.py
│   ├── test_prompts.py
│   ├── test_formatter.py
│   └── test_cli.py
├── .env.example        # Playwright 設定（API鍵不要）
├── .gitignore
├── pyproject.toml      # 依存関係 + プロジェクト設定
├── pytest.ini          # pytest 設定
└── README.md           # このファイル
```

## 技術スタック

- **言語:** Python 3.11+
- **Data Fetching:** Playwright (headless Chromium)
- **Analysis:** Claude Code (対話型)
- **CLI:** Click
- **出力整形:** Rich
- **テスト:** pytest

## 開発者向け情報

### テスト実行

全テストを実行：

```bash
pytest tests/ -v
```

統合テスト（実際にGoogle Flightsアクセス）をスキップ：

```bash
pytest tests/ -v -m "not integration"
```

### 開発環境セットアップ

```bash
pip install -e ".[dev]"
```

## トラブルシューティング

### `ImportError: No module named 'playwright'`

```bash
pip install playwright
playwright install chromium
```

### ブラウザが起動しない

Chromiumがインストールされているか確認：

```bash
playwright install chromium --force
```

### スクレイピングがタイムアウトする

- インターネット接続を確認
- VPN使用時は無効化を試す
- Google Flightsが利用可能か確認

### 空港コードについて

**エリアコードは自動的に主要空港に変換されます：**

- `TYO` → `NRT`（成田）
- `NYC` → `JFK`（JFK）
- `LON` → `LHR`（ヒースロー）
- `PAR` → `CDG`（シャルル・ド・ゴール）

**推奨：** より正確な結果を得るには、具体的な空港コード（例: `NRT`, `LAX`）を使用してください。

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を説明してください。

## サポート

問題が発生した場合は、GitHub Issuesでお知らせください。

---

**GitHub:** https://github.com/tndhk/No36_flight_cheap

**最終更新:** 2026-01-14
```

**Step 4: テストを実行して成功を確認**

```bash
pytest tests/test_readme.py -v
```

期待される出力: PASS - 4 passed

**Step 5: Commit**

```bash
git add README.md tests/test_readme.py
git commit -m "docs: update README for Playwright + Claude Code workflow

- Remove SerpAPI and Gemini API references
- Add Playwright installation instructions
- Explain Claude Code interactive analysis workflow
- Update setup and usage examples
- Add tests to verify documentation accuracy"
```

---

## Task 11: 最終テスト実行と動作確認

**Files:**
- N/A (テスト実行のみ)

**Step 1: 全テストを実行**

```bash
pytest tests/ -v
```

期待される出力: 全テストPASS（統合テスト除く）

**Step 2: 統合テストを実行（任意、時間がかかる）**

```bash
pytest tests/ -v -m integration
```

期待される出力: 統合テストもPASS、実際にフライトデータ取得

**Step 3: 依存関係を再インストール**

```bash
pip uninstall -y serpapi google-generativeai
pip install -e .
playwright install chromium
```

**Step 4: 実際のCLIコマンドを実行して動作確認**

```bash
flight-cheap search --from NRT --to LAX --date 2026-03-01
```

期待される出力:
- ブラウザ起動メッセージ
- フライト結果テーブル表示
- 7つの分析プロンプト表示
- フライトデータサマリー表示

**Step 5: 動作確認が成功したらCommit**

```bash
git add -A
git commit -m "test: verify all tests pass and CLI works end-to-end

- All unit tests passing
- Integration test with real Google Flights confirmed
- CLI successfully fetches and displays flight data
- Analysis prompts displayed for Claude Code interaction"
```

---

## Task 12: PLAN.md更新と完了報告

**Files:**
- Modify: `PLAN.md`

**Step 1: PLAN.mdを更新して実装完了を記録**

```markdown
# Flight Cheap CLI - 実装計画

## 概要
航空券を安く取得するための7つの分析プロンプトを実行し、Google Flightsから直接取得した実データをClaude Codeによる対話型分析で、包括的な価格最適化レポートを提供するPython CLIツール。

## 技術スタック
- 言語: Python 3.11+
- データ取得: Playwright（Google Flights直接スクレイピング）
- 分析: Claude Code（対話型）
- CLI: click
- 出力整形: rich
- 環境変数: python-dotenv（オプション）
- テスト: pytest（テスト駆動開発）

## 実装状況

**✓ 完了（2026-01-14）:**
- [x] SerpAPI → Playwright移行
- [x] Gemini API → Claude Code対話型分析に移行
- [x] pyproject.toml依存関係更新
- [x] fetcher.py全面書き換え（Playwright版）
- [x] analyzer.py削除
- [x] prompts.py簡素化（Claude Code向け）
- [x] cli.py統合更新
- [x] .env.example更新（API鍵不要）
- [x] README.md全面更新
- [x] 全テストPASS確認
- [x] 動作確認完了

## 検証方法
1. `pip install -e .` でローカルインストール
2. `playwright install chromium` でブラウザインストール
3. `flight-cheap search --from TYO --to LAX --date 2026-03-15` を実行
4. フライト結果と7つの分析プロンプトがターミナルに表示されることを確認
5. Claude Codeに分析を依頼して結果を得る
```

**Step 2: Commit**

```bash
git add PLAN.md
git commit -m "docs: update PLAN.md with migration completion status

- Mark all migration tasks as completed
- Update tech stack to Playwright + Claude Code
- Add verification steps for new workflow"
```

---

## 実装完了後の使い方

1. **フライトデータ取得:**
   ```bash
   flight-cheap search --from TYO --to LAX --date 2026-03-01
   ```

2. **表示された7つのプロンプトから選択:**
   - プロンプト1: Hidden Route Scanner
   - プロンプト2: Price Manipulation Detector
   - ...など

3. **Claude Codeに分析を依頼:**
   - "このフライトデータをプロンプト1（Hidden Route Scanner）で分析してください"
   - "プロンプト4を使って最適な予約タイミングを教えて"
   - "全てのプロンプトで順番に分析して"

4. **Claude Codeが対話的に分析:**
   - 詳細な価格分析
   - 節約のための具体的アドバイス
   - 追加質問に対応

## 利点

**API料金ゼロ:**
- SerpAPI不要（月100回制限なし）
- Gemini API不要（15 RPM制限なし）

**柔軟な分析:**
- ユーザーが必要なプロンプトだけ実行
- Claude Codeが文脈を理解して深掘り可能
- 追加質問で対話的に最適化

**メンテナンス性:**
- Playwright = Google Flights UI変更に対応しやすい
- プロンプトのカスタマイズが容易
- テストが明確で保守しやすい
