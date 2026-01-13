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
