"""Flight analysis using Gemini API."""

import asyncio
from dataclasses import dataclass
from typing import List, Optional
import google.generativeai as genai
from src.prompts import get_all_prompts


@dataclass
class AnalysisResult:
    """Result from analyzing a single prompt."""

    prompt_id: int
    prompt_name: str
    analysis: str

    def __str__(self) -> str:
        """String representation."""
        return f"[{self.prompt_name}]\n{self.analysis}"


class FlightAnalyzer:
    """Analyze flights using Gemini API with concurrent request limiting."""

    def __init__(self, api_key: str, max_concurrent: int = 3):
        """Initialize FlightAnalyzer.

        Args:
            api_key: Gemini API key.
            max_concurrent: Maximum concurrent API requests (default: 3 for free tier).

        Raises:
            ValueError: If api_key is empty or None.
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-2.5-flash")
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def analyze_single(
        self,
        prompt_id: int,
        prompt_name: str,
        system_prompt: str,
        user_prompt: str,
    ) -> AnalysisResult:
        """Analyze with a single prompt (respecting concurrency limit).

        Args:
            prompt_id: ID of the prompt.
            prompt_name: Name of the prompt.
            system_prompt: System message.
            user_prompt: User message with flight data.

        Returns:
            AnalysisResult with analysis text.

        Raises:
            Exception: If API call fails.
        """
        async with self._semaphore:
            try:
                # Construct full prompt
                full_prompt = f"{system_prompt}\n\n{user_prompt}"

                # Call Gemini API
                response = self._model.generate_content(full_prompt)

                return AnalysisResult(
                    prompt_id=prompt_id,
                    prompt_name=prompt_name,
                    analysis=response.text,
                )
            except Exception as e:
                raise Exception(
                    f"Analysis failed for {prompt_name} (ID {prompt_id}): {str(e)}"
                )

    async def analyze_flights(self, flight_data: str) -> List[AnalysisResult]:
        """Analyze flights with all 7 prompts concurrently.

        Args:
            flight_data: Flight data formatted as string.

        Returns:
            List of AnalysisResult for each prompt (1-7).

        Raises:
            Exception: If analysis fails.
        """
        prompts = get_all_prompts()

        # Create async tasks for all prompts
        tasks = []
        for prompt in prompts:
            user_message = prompt.format_user(flight_data)
            task = self.analyze_single(
                prompt_id=prompt.id,
                prompt_name=prompt.name,
                system_prompt=prompt.system,
                user_prompt=user_message,
            )
            tasks.append(task)

        # Execute all tasks concurrently (with semaphore limit)
        results = await asyncio.gather(*tasks)

        return results

    def analyze_flights_sync(self, flight_data: str) -> List[AnalysisResult]:
        """Synchronous wrapper for analyze_flights.

        Args:
            flight_data: Flight data formatted as string.

        Returns:
            List of AnalysisResult for each prompt.
        """
        return asyncio.run(self.analyze_flights(flight_data))
