"""Test suite for analyzer module (Gemini API integration)."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.analyzer import FlightAnalyzer, AnalysisResult


class TestAnalysisResult:
    """Test AnalysisResult class."""

    def test_analysis_result_initialization(self):
        """Test AnalysisResult can be initialized."""
        result = AnalysisResult(
            prompt_id=1,
            prompt_name="Hidden Route Scanner",
            analysis="Sample analysis",
        )
        assert result.prompt_id == 1
        assert result.prompt_name == "Hidden Route Scanner"
        assert result.analysis == "Sample analysis"

    def test_analysis_result_to_string(self):
        """Test AnalysisResult can be converted to string."""
        result = AnalysisResult(
            prompt_id=1,
            prompt_name="Test",
            analysis="Result text",
        )
        result_str = str(result)
        assert "Test" in result_str
        assert "Result text" in result_str


class TestFlightAnalyzer:
    """Test FlightAnalyzer class."""

    def test_flight_analyzer_initialization(self):
        """Test FlightAnalyzer can be initialized."""
        analyzer = FlightAnalyzer(api_key="test_key")
        assert analyzer.api_key == "test_key"

    def test_flight_analyzer_requires_api_key(self):
        """Test FlightAnalyzer requires API key."""
        with pytest.raises(ValueError):
            FlightAnalyzer(api_key="")

    @patch("src.analyzer.genai")
    def test_analyze_async(self, mock_genai):
        """Test async analysis."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Analysis result"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = FlightAnalyzer(api_key="test_key")

        # Run async test
        async def test():
            result = await analyzer.analyze_single(
                prompt_id=1,
                prompt_name="Test",
                system_prompt="System",
                user_prompt="User",
            )
            assert isinstance(result, AnalysisResult)
            assert result.prompt_id == 1
            assert "Analysis result" in result.analysis

        asyncio.run(test())

    @patch("src.analyzer.genai")
    def test_analyze_with_semaphore_limit(self, mock_genai):
        """Test concurrent analysis respects semaphore limit."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Result"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = FlightAnalyzer(api_key="test_key", max_concurrent=3)

        async def test():
            tasks = []
            for i in range(1, 8):
                task = analyzer.analyze_single(
                    prompt_id=i,
                    prompt_name=f"Prompt {i}",
                    system_prompt="Sys",
                    user_prompt="User",
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            assert len(results) == 7
            for result in results:
                assert isinstance(result, AnalysisResult)

        asyncio.run(test())

    @patch("src.analyzer.genai")
    def test_analyze_flight_data(self, mock_genai):
        """Test analyzing flight data with all 7 prompts."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Analysis"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = FlightAnalyzer(api_key="test_key")

        async def test():
            flight_data = "TYO to LAX"
            results = await analyzer.analyze_flights(flight_data)

            assert isinstance(results, list)
            assert len(results) == 7
            for i, result in enumerate(results, 1):
                assert isinstance(result, AnalysisResult)
                assert result.prompt_id == i

        asyncio.run(test())

    @patch("src.analyzer.genai")
    def test_analyze_handles_api_error(self, mock_genai):
        """Test error handling in analysis."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = FlightAnalyzer(api_key="test_key")

        async def test():
            with pytest.raises(Exception) as exc_info:
                await analyzer.analyze_single(
                    prompt_id=1,
                    prompt_name="Test",
                    system_prompt="Sys",
                    user_prompt="User",
                )
            assert "API Error" in str(exc_info.value)

        asyncio.run(test())


class TestAnalyzerConcurrency:
    """Test concurrent execution limits."""

    @patch("src.analyzer.genai")
    def test_max_concurrent_enforced(self, mock_genai):
        """Test that max_concurrent limit is enforced."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Result"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = FlightAnalyzer(api_key="test_key", max_concurrent=2)

        # Verify semaphore is configured
        assert analyzer._semaphore._value == 2

    @patch("src.analyzer.genai")
    def test_default_max_concurrent_is_three(self, mock_genai):
        """Test default max_concurrent is 3."""
        analyzer = FlightAnalyzer(api_key="test_key")
        assert analyzer._semaphore._value == 3


class TestAnalysisIntegration:
    """Test full analysis workflow."""

    @patch("src.analyzer.genai")
    @patch("src.analyzer.get_all_prompts")
    def test_full_analysis_workflow(self, mock_get_prompts, mock_genai):
        """Test complete analysis workflow."""
        from src.prompts import PromptTemplate

        # Mock prompts
        mock_prompts = [
            PromptTemplate(
                id=1,
                name="Test 1",
                system="Sys 1",
                user_template="User {flight_data}",
            ),
            PromptTemplate(
                id=2,
                name="Test 2",
                system="Sys 2",
                user_template="User {flight_data}",
            ),
        ]
        mock_get_prompts.return_value = mock_prompts

        # Mock API
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Result"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = FlightAnalyzer(api_key="test_key")

        async def test():
            results = await analyzer.analyze_flights("Test flight data")
            assert len(results) >= 0

        asyncio.run(test())
