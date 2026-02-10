"""
AI Engine Module
Integrates with Gemini 2.5 Flash for enhanced analysis
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional
from functools import wraps

import google.generativeai as genai
from core.config import settings

logger = logging.getLogger(__name__)


def rate_limit(max_calls: int = 10, period: int = 60):
    """Rate limiting decorator"""
    calls: list[float] = []

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()

            while calls and calls[0] < now - period:
                calls.pop(0)

            if len(calls) >= max_calls:
                wait_time = period - (now - calls[0])
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

            calls.append(now)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class AIEngine:
    """
    AI-powered analysis using Gemini 2.5 Flash
    Optional component that enhances analysis results
    """

    def __init__(self):
        self.enabled: bool = False
        self.model: Optional[Any] = None  # ← intentional (SDK has no types)

        if settings.AI_ENABLED and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
                self.enabled = True
                logger.info("AI Engine initialized with Gemini 2.5 Flash")
            except Exception as e:
                logger.error(f"Failed to initialize AI Engine: {e}")
        else:
            logger.info("AI Engine disabled (no API key or disabled in config)")

    async def enhance_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or self.model is None:
            return {
                "status": "disabled",
                "message": "AI Engine not available"
            }

        return {
            "code_quality": await self._analyze_code_quality(analysis_results),
            "security_recommendations": await self._analyze_security(analysis_results),
            "release_recommendations": await self._generate_release_insights(analysis_results),
        }

    @rate_limit(max_calls=5, period=60)
    async def _analyze_code_quality(self, results: Dict[str, Any]) -> str:
        if self.model is None:
            return "AI model not initialized"

        try:
            complexity = results.get("code_analysis", {}).get("complexity", {})

            prompt = f"""
Analyze these code quality metrics and provide 2–3 actionable recommendations:

- Average Complexity: {complexity.get('average', 0)}
- Max Complexity: {complexity.get('max', 0)}

Keep the response under 150 words.
"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"AI code quality analysis failed: {e}")
            return "Analysis unavailable"

    @rate_limit(max_calls=5, period=60)
    async def _analyze_security(self, results: Dict[str, Any]) -> str:
        if self.model is None:
            return "AI model not initialized"

        try:
            security = results.get("security", {})
            prompt = f"""
Security scan summary:
- Vulnerabilities: {len(security.get('vulnerabilities', []))}
- Secrets found: {len(security.get('secrets_found', []))}

Provide 2–3 priority security recommendations.
"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"AI security analysis failed: {e}")
            return "Analysis unavailable"

    @rate_limit(max_calls=5, period=60)
    async def _generate_release_insights(self, results: Dict[str, Any]) -> str:
        if self.model is None:
            return "AI model not initialized"

        try:
            risks = results.get("risks", [])
            critical = sum(1 for r in risks if r.get("priority") == "CRITICAL")

            prompt = f"""
Release assessment:
- Risk score: {results.get('risk_score', 0)}/10
- Critical issues: {critical}

Give readiness assessment and top 2 recommendations.
"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"AI release insights failed: {e}")
            return "Analysis unavailable"
