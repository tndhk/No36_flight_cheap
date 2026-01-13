"""Test suite for prompts module."""

import pytest
from src.prompts import (
    PromptInfo,
    get_all_prompts,
    format_prompts_for_claude,
    PROMPT_COUNT,
    PROMPTS,
)


class TestPromptInfo:
    """Test PromptInfo class."""

    def test_prompt_info_initialization(self):
        """Test PromptInfo can be initialized."""
        prompt = PromptInfo(
            id=1,
            name="Test Prompt",
            description="Test description",
        )
        assert prompt.id == 1
        assert prompt.name == "Test Prompt"
        assert prompt.description == "Test description"


class TestPromptLoading:
    """Test loading prompts from spec.md."""

    def test_get_all_prompts_returns_list(self):
        """Test get_all_prompts returns a list of dicts."""
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
            assert "id" in prompt
            assert "name" in prompt
            assert "description" in prompt
            assert prompt["id"] is not None
            assert prompt["name"] is not None
            assert prompt["description"] is not None

    def test_prompt_ids_are_sequential(self):
        """Test prompt IDs are sequential from 1 to 7."""
        prompts = get_all_prompts()
        ids = [p["id"] for p in prompts]
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
        actual_names = [p["name"] for p in prompts]
        assert actual_names == expected_names


class TestPromptFormatting:
    """Test formatting prompts for Claude Code."""

    def test_format_prompts_for_claude_returns_string(self):
        """Test format_prompts_for_claude returns a string."""
        output = format_prompts_for_claude()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_prompts_contains_all_prompts(self):
        """Test formatted output contains all prompt names."""
        output = format_prompts_for_claude()
        for prompt in PROMPTS:
            assert prompt.name in output

    def test_format_prompts_contains_usage_instructions(self):
        """Test formatted output contains usage instructions."""
        output = format_prompts_for_claude()
        assert "ANALYSIS PROMPTS" in output
        assert "Usage:" in output
        assert "Claude Code" in output


class TestPromptContent:
    """Test prompt content from spec.md."""

    def test_hidden_route_scanner_contains_key_terms(self):
        """Test Hidden Route Scanner prompt contains expected terms."""
        prompts = get_all_prompts()
        prompt_1 = next(p for p in prompts if p["id"] == 1)
        description = prompt_1["description"].lower()
        expected_terms = ["hidden city", "route", "nearby airport"]
        # At least one key term should be present
        assert any(term in description for term in expected_terms)

    def test_price_manipulation_detector_contains_key_terms(self):
        """Test Price Manipulation Detector prompt contains expected terms."""
        prompts = get_all_prompts()
        prompt_2 = next(p for p in prompts if p["id"] == 2)
        description = prompt_2["description"].lower()
        assert "price" in description or "pricing" in description

    def test_all_prompts_have_descriptions(self):
        """Test all prompts have non-empty descriptions."""
        prompts = get_all_prompts()
        for prompt in prompts:
            assert len(prompt["description"]) > 0

    def test_prompts_structure_for_claude_code(self):
        """Test prompts are structured correctly for Claude Code."""
        prompts = get_all_prompts()
        for prompt in prompts:
            # Each prompt should have exactly these keys
            assert set(prompt.keys()) == {"id", "name", "description"}
            # IDs should be integers
            assert isinstance(prompt["id"], int)
            # Names and descriptions should be strings
            assert isinstance(prompt["name"], str)
            assert isinstance(prompt["description"], str)
