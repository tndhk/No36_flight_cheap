"""Prompt templates for flight analysis."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PromptTemplate:
    """A prompt template with system and user messages."""

    id: int
    name: str
    system: str
    user_template: str

    def format_user(self, flight_data: str) -> str:
        """Format user template with flight data.

        Args:
            flight_data: Flight data to embed in the prompt.

        Returns:
            Formatted user message with flight data.
        """
        return self.user_template.format(flight_data=flight_data)


# Prompt definitions extracted from spec.md
PROMPTS = [
    PromptTemplate(
        id=1,
        name="Hidden Route Scanner",
        system="Act as a professional flight pricing analyst.",
        user_template="""Break my route into hidden city tickets, nearby departure and arrival airports, and multi-leg combinations airlines don't surface.

Flight Data:
{flight_data}

Compare direct vs split routes, explain the price gap, and rank the cheapest legal options.""",
    ),
    PromptTemplate(
        id=2,
        name="Price Manipulation Detector",
        system="Act as a professional flight pricing analyst.",
        user_template="""Analyze how airlines raise prices using repeated searches, cookies, browser data, device type, IP location, and time-based demand signals.

Flight Data:
{flight_data}

Explain exactly which behaviors trigger price inflation and give a precise step-by-step search method to avoid it.""",
    ),
    PromptTemplate(
        id=3,
        name="Geo-Pricing Bypass",
        system="Act as a professional flight pricing analyst.",
        user_template="""Simulate flight prices for the same route across different countries, currencies, and regional booking markets.

Flight Data:
{flight_data}

Identify where the ticket is priced lowest, explain why geo-pricing differs, and outline legal ways travelers can access those fares.""",
    ),
    PromptTemplate(
        id=4,
        name="Timing Sweet Spot Finder",
        system="Act as a professional flight pricing analyst.",
        user_template="""Use historical airline pricing behavior to identify the cheapest booking days, booking windows, and departure periods for this route.

Flight Data:
{flight_data}

Explain how demand cycles, inventory release, and fare resets influence these price drops.""",
    ),
    PromptTemplate(
        id=5,
        name="Fare Rule Exploiter",
        system="Act as a professional flight pricing analyst.",
        user_template="""Break down airline fare rules, ticket classes, routing logic, and pricing conditions in simple terms.

Flight Data:
{flight_data}

Show how airlines structure these rules to price flights differently and how travelers can select options that quietly reduce total cost.""",
    ),
    PromptTemplate(
        id=6,
        name="Airline VS OTA Comparison",
        system="Act as a professional flight pricing analyst.",
        user_template="""Compare pricing between airlines, major OTAs, regional booking sites, and lesser-known platforms.

Flight Data:
{flight_data}

Identify where service fees, markups, and hidden discounts appear, and explain which platforms usually reveal lower base fares.""",
    ),
    PromptTemplate(
        id=7,
        name="Price Drop Watch Strategy",
        system="Act as a professional flight pricing analyst.",
        user_template="""Create a detailed fare-tracking strategy that monitors price drops without triggering increases.

Flight Data:
{flight_data}

Include search frequency, timing resets, alert setup, behavioral rules, and practical examples to keep prices stable while tracking over time.""",
    ),
]

PROMPT_COUNT = len(PROMPTS)


def get_all_prompts() -> List[PromptTemplate]:
    """Get all prompt templates.

    Returns:
        List of all PromptTemplate instances.
    """
    return PROMPTS


def get_prompt_by_id(prompt_id: int) -> Optional[PromptTemplate]:
    """Get a prompt template by ID.

    Args:
        prompt_id: The ID of the prompt (1-7).

    Returns:
        The PromptTemplate if found, None otherwise.
    """
    for prompt in PROMPTS:
        if prompt.id == prompt_id:
            return prompt
    return None
