"""
Natural Language Generator for the Explainability Module.

Generates Natural_Language_Summary using Amazon Bedrock LLM with a
template-based fallback for resilience. Supports English ("en") and
Traditional Chinese ("zh-TW").

Bedrock settings:
  - temperature: 0.3
  - max_tokens: 500

Rate limiting: < 1 req/s via RateLimiter from src/common/rate_limiter.py

Fallback triggers:
  - botocore.exceptions.ClientError
  - socket / read timeout
  - Empty or whitespace-only response from Bedrock
"""

import json
import logging
from typing import List, Tuple

from botocore.exceptions import ClientError

from src.common.aws_clients import get_aws_clients
from src.common.models import RiskAssessment, RiskLevel
from src.common.rate_limiter import RateLimiter
from src.explainability.models import FeatureContribution

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

# English templates — placeholders: {score}, {primary_factor}
_TEMPLATES_EN = {
    RiskLevel.CRITICAL: (
        "This account shows critical risk (score: {score}) due to {primary_factor}. "
        "Immediate review recommended."
    ),
    RiskLevel.HIGH: (
        "This account shows high risk (score: {score}) primarily due to {primary_factor}. "
        "Review recommended."
    ),
    RiskLevel.MEDIUM: (
        "This account shows moderate risk (score: {score}) with {primary_factor} as the main concern."
    ),
    RiskLevel.LOW: (
        "This account shows low risk (score: {score}) with normal activity patterns."
    ),
}

# Traditional Chinese templates — equivalent translations
_TEMPLATES_ZH_TW = {
    RiskLevel.CRITICAL: (
        "此帳號顯示極高風險（分數：{score}），主要原因為{primary_factor}。建議立即審查。"
    ),
    RiskLevel.HIGH: (
        "此帳號顯示高風險（分數：{score}），主要原因為{primary_factor}。建議進行審查。"
    ),
    RiskLevel.MEDIUM: (
        "此帳號顯示中等風險（分數：{score}），主要關注點為{primary_factor}。"
    ),
    RiskLevel.LOW: (
        "此帳號顯示低風險（分數：{score}），活動模式正常。"
    ),
}

_SUPPORTED_LANGUAGES = {"en", "zh-TW"}

# Bedrock model to use for NLG
_BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


class NaturalLanguageGenerator:
    """
    Generates natural language summaries for risk assessments.

    Uses Amazon Bedrock LLM as the primary path and falls back to
    template-based generation on failure.

    Args:
        rate_limiter: Optional RateLimiter instance. A default one (< 1 req/s)
                      is created if not provided.
        model_id: Bedrock model ID to use for generation.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter = None,
        model_id: str = _BEDROCK_MODEL_ID,
    ) -> None:
        self._rate_limiter = rate_limiter or RateLimiter(max_requests_per_second=0.9)
        self._model_id = model_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        assessment: RiskAssessment,
        top_features: List[FeatureContribution],
        language: str = "en",
    ) -> Tuple[str, bool]:
        """
        Generate a natural language summary for a risk assessment.

        Args:
            assessment: The risk assessment to explain.
            top_features: Top contributing features (sorted descending).
            language: Language code — "en" or "zh-TW". Unsupported codes
                      default to "en" with a warning log.

        Returns:
            Tuple of (summary_text, is_fallback) where is_fallback is True
            when the template path was used instead of Bedrock.
        """
        # Validate / normalise language
        if language not in _SUPPORTED_LANGUAGES:
            logger.warning(
                "Unsupported language '%s'; defaulting to 'en'.", language
            )
            language = "en"

        # Attempt Bedrock generation
        try:
            summary = self._generate_with_bedrock(assessment, top_features, language)
            if summary:
                return summary, False
            # Empty response — fall through to template
            logger.warning(
                "Bedrock returned an empty response for account '%s'; "
                "falling back to template.",
                assessment.account_id,
            )
        except ClientError as exc:
            logger.warning(
                "Bedrock ClientError for account '%s': %s; falling back to template.",
                assessment.account_id,
                exc,
            )
        except Exception as exc:  # covers timeouts and other transient errors
            logger.warning(
                "Bedrock call failed for account '%s': %s; falling back to template.",
                assessment.account_id,
                exc,
            )

        # Template fallback
        summary = self._generate_from_template(assessment, top_features, language)
        return summary, True

    # ------------------------------------------------------------------
    # Bedrock path
    # ------------------------------------------------------------------

    def _generate_with_bedrock(
        self,
        assessment: RiskAssessment,
        top_features: List[FeatureContribution],
        language: str,
    ) -> str:
        """
        Call Bedrock to generate a natural language summary.

        Applies rate limiting before each call.

        Returns:
            Generated text, or empty string if the response body is empty.

        Raises:
            ClientError: On Bedrock API errors.
            Exception: On timeout or other transient failures.
        """
        prompt = self._build_prompt(assessment, top_features, language)

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        # Enforce rate limit before the API call
        self._rate_limiter.wait_if_needed()

        clients = get_aws_clients()
        response = clients.bedrock_runtime.invoke_model(
            modelId=self._model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body),
        )

        response_body = json.loads(response["body"].read())
        content = response_body.get("content", [])
        if not content:
            return ""

        text = content[0].get("text", "").strip()
        return text

    def _build_prompt(
        self,
        assessment: RiskAssessment,
        top_features: List[FeatureContribution],
        language: str,
    ) -> str:
        """
        Construct the Bedrock prompt string.

        Includes: risk_score, risk_level, risk_factors, top features,
        and a language instruction.
        """
        risk_factors_str = ", ".join(assessment.risk_factors) if assessment.risk_factors else "none"

        feature_lines = []
        for fc in top_features[:3]:
            feature_lines.append(
                f"  - {fc.feature_name}: contribution={fc.contribution:.2f}, "
                f"context={fc.context_label}"
            )
        features_str = "\n".join(feature_lines) if feature_lines else "  - (no top features)"

        if language == "zh-TW":
            language_instruction = (
                "Please write the explanation in Traditional Chinese (繁體中文)."
            )
        else:
            language_instruction = "Please write the explanation in English."

        prompt = (
            f"You are a financial risk analyst. Generate a concise natural language "
            f"explanation for the following risk assessment.\n\n"
            f"Risk Score: {assessment.risk_score}\n"
            f"Risk Level: {assessment.risk_level.value.upper()}\n"
            f"Risk Factors: {risk_factors_str}\n"
            f"Top Contributing Features:\n{features_str}\n\n"
            f"{language_instruction}\n"
            f"Keep the explanation under 3 sentences and focus on the most important "
            f"risk indicators. Do not include any preamble or meta-commentary."
        )
        return prompt

    # ------------------------------------------------------------------
    # Template fallback path
    # ------------------------------------------------------------------

    def _generate_from_template(
        self,
        assessment: RiskAssessment,
        top_features: List[FeatureContribution],
        language: str,
    ) -> str:
        """
        Generate a summary using the pre-defined templates.

        Selects the template for the given risk_level and language,
        then substitutes {score} and {primary_factor}.
        """
        templates = _TEMPLATES_ZH_TW if language == "zh-TW" else _TEMPLATES_EN
        template = templates[assessment.risk_level]

        primary_factor = self._get_primary_factor(assessment, top_features)
        score = round(assessment.risk_score, 1)

        return template.format(score=score, primary_factor=primary_factor)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_primary_factor(
        self,
        assessment: RiskAssessment,
        top_features: List[FeatureContribution],
    ) -> str:
        """
        Determine the primary risk factor for template substitution.

        Priority:
          1. First top feature name (if available)
          2. First risk factor string (if available)
          3. Generic fallback
        """
        if top_features:
            return top_features[0].feature_name
        if assessment.risk_factors:
            return assessment.risk_factors[0]
        return "unknown risk factor"
