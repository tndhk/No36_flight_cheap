"""Test suite for prompts module."""

import pytest
from src.prompts import (
    PromptTemplate,
    get_all_prompts,
    get_prompt_by_id,
    PROMPT_COUNT,
)


class TestPromptTemplate:
    """Test PromptTemplate class."""

    def test_prompt_template_initialization(self):
        """Test PromptTemplate can be initialized."""
        template = PromptTemplate(
            id=1,
            name="Test Prompt",
            system="System prompt",
            user_template="User prompt with {flight_data}",
        )
        assert template.id == 1
        assert template.name == "Test Prompt"
        assert template.system == "System prompt"
        assert template.user_template == "User prompt with {flight_data}"

    def test_prompt_template_format(self):
        """Test PromptTemplate can format user template."""
        template = PromptTemplate(
            id=1,
            name="Test Prompt",
            system="System prompt",
            user_template="Analyze flights: {flight_data}",
        )
        flight_data = "TYO to LAX, $1000"
        formatted = template.format_user(flight_data)
        assert "Analyze flights: TYO to LAX, $1000" in formatted


class TestPromptLoading:
    """Test loading prompts from spec.md."""

    def test_get_all_prompts_returns_list(self):
        """Test get_all_prompts returns a list."""
        prompts = get_all_prompts()
        assert isinstance(prompts, list)
        assert len(prompts) == PROMPT_COUNT

    def test_prompt_count_is_seven(self):
        """Test PROMPT_COUNT constant is 7."""
        assert PROMPT_COUNT == 7

    def test_all_prompts_have_required_fields(self):
        """Test all prompts have required fields."""
        prompts = get_all_prompts()
        for prompt in prompts:
            assert hasattr(prompt, "id")
            assert hasattr(prompt, "name")
            assert hasattr(prompt, "system")
            assert hasattr(prompt, "user_template")
            assert prompt.id is not None
            assert prompt.name is not None
            assert prompt.system is not None
            assert prompt.user_template is not None

    def test_prompt_ids_are_sequential(self):
        """Test prompt IDs are sequential from 1 to 7."""
        prompts = get_all_prompts()
        ids = [p.id for p in prompts]
        assert ids == list(range(1, PROMPT_COUNT + 1))

    def test_prompt_names_are_correct(self):
        """Test prompt names match spec."""
        expected_names = [
            "Hidden Route Scanner",
            "Price Manipulation Detector",
            "Geo-Pricing Bypass",
            "Timing Sweet Spot Finder",
            "Fare Rule Exploiter",
            "Airline VS OTA Comparison",
            "Price Drop Watch Strategy",
        ]
        prompts = get_all_prompts()
        actual_names = [p.name for p in prompts]
        assert actual_names == expected_names


class TestPromptRetrieval:
    """Test retrieving specific prompts."""

    def test_get_prompt_by_id_valid(self):
        """Test getting a prompt by valid ID."""
        prompt = get_prompt_by_id(1)
        assert prompt is not None
        assert prompt.id == 1
        assert prompt.name == "Hidden Route Scanner"

    def test_get_prompt_by_id_all_valid(self):
        """Test all prompt IDs can be retrieved."""
        for i in range(1, PROMPT_COUNT + 1):
            prompt = get_prompt_by_id(i)
            assert prompt is not None
            assert prompt.id == i

    def test_get_prompt_by_id_invalid(self):
        """Test getting a prompt by invalid ID returns None."""
        prompt = get_prompt_by_id(999)
        assert prompt is None

    def test_get_prompt_by_id_zero(self):
        """Test getting a prompt by ID 0 returns None."""
        prompt = get_prompt_by_id(0)
        assert prompt is None


class TestPromptContent:
    """Test prompt content from spec.md."""

    def test_hidden_route_scanner_contains_key_terms(self):
        """Test Hidden Route Scanner prompt contains expected terms."""
        prompt = get_prompt_by_id(1)
        user_text = prompt.user_template.lower()
        expected_terms = ["hidden city", "route", "nearby airport"]
        # At least one key term should be present
        assert any(term in user_text for term in expected_terms)

    def test_price_manipulation_detector_contains_key_terms(self):
        """Test Price Manipulation Detector prompt contains expected terms."""
        prompt = get_prompt_by_id(2)
        user_text = prompt.user_template.lower()
        assert "price" in user_text or "pricing" in user_text

    def test_prompt_system_message_exists(self):
        """Test all prompts have non-empty system message."""
        prompts = get_all_prompts()
        for prompt in prompts:
            assert len(prompt.system) > 0

    def test_prompt_user_template_is_template(self):
        """Test all prompts have placeholder for flight data."""
        prompts = get_all_prompts()
        for prompt in prompts:
            assert "{flight_data}" in prompt.user_template


class TestPromptIntegration:
    """Test prompt integration with flight data."""

    def test_prompt_formatting_with_sample_data(self):
        """Test formatting prompts with sample flight data."""
        sample_flight_data = """
        Flights from Tokyo (TYO) to Los Angeles (LAX):
        - Direct: JAL 001, $1200
        - Via San Francisco: JAL 002 + JAL 003, $950
        Alternative: Use Narita (NRT) to San Francisco (SFO): $850
        """

        prompts = get_all_prompts()
        for prompt in prompts:
            formatted = prompt.format_user(sample_flight_data)
            assert sample_flight_data in formatted
            assert len(formatted) > 0
