"""Prompt templates for flight analysis."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class PromptInfo:
    """A prompt information for Claude Code interactive analysis."""

    id: int
    name: str
    description: str


# Prompt definitions extracted from spec.md
PROMPTS = [
    PromptInfo(
        id=1,
        name="Hidden Route Scanner",
        description="Break my route into hidden city tickets, nearby departure and arrival airports, and multi-leg combinations airlines don't surface. Compare direct vs split routes, explain the price gap, and rank the cheapest legal options.",
    ),
    PromptInfo(
        id=2,
        name="Price Manipulation Detector",
        description="Analyze how airlines raise prices using repeated searches, cookies, browser data, device type, IP location, and time-based demand signals. Explain exactly which behaviors trigger price inflation and give a precise step-by-step search method to avoid it.",
    ),
    PromptInfo(
        id=3,
        name="Geo-Pricing Bypass",
        description="Simulate flight prices for the same route across different countries, currencies, and regional booking markets. Identify where the ticket is priced lowest, explain why geo-pricing differs, and outline legal ways travelers can access those fares.",
    ),
    PromptInfo(
        id=4,
        name="Timing Sweet Spot Finder",
        description="Use historical airline pricing behavior to identify the cheapest booking days, booking windows, and departure periods for this route. Explain how demand cycles, inventory release, and fare resets influence these price drops.",
    ),
    PromptInfo(
        id=5,
        name="Fare Rule Exploiter",
        description="Break down airline fare rules, ticket classes, routing logic, and pricing conditions in simple terms. Show how airlines structure these rules to price flights differently and how travelers can select options that quietly reduce total cost.",
    ),
    PromptInfo(
        id=6,
        name="Airline VS OTA Comparison",
        description="Compare pricing between airlines, major OTAs, regional booking sites, and lesser-known platforms. Identify where service fees, markups, and hidden discounts appear, and explain which platforms usually reveal lower base fares.",
    ),
    PromptInfo(
        id=7,
        name="Price Drop Watch Strategy",
        description="Create a detailed fare-tracking strategy that monitors price drops without triggering increases. Include search frequency, timing resets, alert setup, behavioral rules, and practical examples to keep prices stable while tracking over time.",
    ),
]

PROMPT_COUNT = len(PROMPTS)


def get_all_prompts() -> List[Dict[str, any]]:
    """Get all prompts as dictionary list for Claude Code.

    Returns:
        List of prompt dictionaries with id, name, and description.
    """
    return [
        {
            "id": prompt.id,
            "name": prompt.name,
            "description": prompt.description,
        }
        for prompt in PROMPTS
    ]


def format_prompts_for_claude() -> str:
    """Format prompts for Claude Code terminal display.

    Returns:
        Formatted string with all prompts for interactive analysis.
    """
    output = "\n" + "=" * 80 + "\n"
    output += "ANALYSIS PROMPTS FOR CLAUDE CODE\n"
    output += "=" * 80 + "\n\n"
    output += "Copy the flight data above and use these prompts for analysis:\n\n"

    for prompt in PROMPTS:
        output += f"[{prompt.id}] {prompt.name}\n"
        output += f"    {prompt.description}\n\n"

    output += "=" * 80 + "\n"
    output += "Usage: Ask Claude Code to analyze the flight data using any of these prompts.\n"
    output += "Example: 'Analyze this data using prompt 1: Hidden Route Scanner'\n"
    output += "=" * 80 + "\n"

    return output
