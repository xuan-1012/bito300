"""
Unit tests for Risk Analyzer.

Tests specific known values for:
- Bedrock prompt construction
- LLM response parsing
- Fallback scoring with various feature combinations
- Risk level classification
- Rate limiter integration

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
"""

import json
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, call
from io import BytesIO

from src.common.models import TransactionFeatures, RiskAssessment, RiskLevel
from src.common.rate_limiter import RateLimiter
from src.lambdas.risk_analyzer.handler import (
    RISK_ANALYSIS_PROMPT,
    analyze_risk_with_bedrock,
    _parse_llm_response,
    fallback_risk_scoring,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_features(
    account_id: str = "acc_test",
    total_volume: float = 50_000.0,
    transaction_count: int = 10,
    avg_transaction_size: float = 5_000.0,
    max_transaction_size: float = 10_000.0,
    unique_counterparties: int = 5,
    night_transaction_ratio: float = 0.1,
    rapid_transaction_count: int = 2,
    round_number_ratio: float = 0.2,
    concentration_score: float = 0.3,
    velocity_score: float = 2.0,
) -> TransactionFeatures:
    """Create a TransactionFeatures object with sensible defaults."""
    return TransactionFeatures(
        account_id=account_id,
        total_volume=total_volume,
        transaction_count=transaction_count,
        avg_transaction_size=avg_transaction_size,
        max_transaction_size=max_transaction_size,
        unique_counterparties=unique_counterparties,
        night_transaction_ratio=night_transaction_ratio,
        rapid_transaction_count=rapid_transaction_count,
        round_number_ratio=round_number_ratio,
        concentration_score=concentration_score,
        velocity_score=velocity_score,
    )


def make_bedrock_response(payload: dict) -> dict:
    """Build a mock Bedrock invoke_model response dict."""
    body_bytes = json.dumps({
        "content": [{"text": json.dumps(payload)}]
    }).encode("utf-8")
    return {"body": BytesIO(body_bytes)}


def make_rate_limiter() -> RateLimiter:
    """Return a rate limiter with wait_if_needed mocked out."""
    rl = RateLimiter(max_requests_per_second=0.9)
    rl.wait_if_needed = MagicMock()
    return rl


# ---------------------------------------------------------------------------
# Tests: Bedrock prompt construction (Requirement 4.1)
# ---------------------------------------------------------------------------

class TestPromptConstruction:
    """Verify that RISK_ANALYSIS_PROMPT contains all required feature placeholders."""

    def test_prompt_contains_total_volume_placeholder(self):
        assert "{total_volume}" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_transaction_count_placeholder(self):
        assert "{transaction_count}" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_avg_transaction_size_placeholder(self):
        assert "{avg_transaction_size}" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_max_transaction_size_placeholder(self):
        assert "{max_transaction_size}" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_unique_counterparties_placeholder(self):
        assert "{unique_counterparties}" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_night_transaction_ratio_placeholder(self):
        assert "{night_transaction_ratio" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_rapid_transaction_count_placeholder(self):
        assert "{rapid_transaction_count}" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_round_number_ratio_placeholder(self):
        assert "{round_number_ratio" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_concentration_score_placeholder(self):
        assert "{concentration_score" in RISK_ANALYSIS_PROMPT

    def test_prompt_contains_velocity_score_placeholder(self):
        assert "{velocity_score" in RISK_ANALYSIS_PROMPT

    def test_prompt_specifies_json_response_format(self):
        assert "risk_score" in RISK_ANALYSIS_PROMPT
        assert "risk_level" in RISK_ANALYSIS_PROMPT
        assert "risk_factors" in RISK_ANALYSIS_PROMPT
        assert "explanation" in RISK_ANALYSIS_PROMPT
        assert "confidence" in RISK_ANALYSIS_PROMPT

    def test_prompt_formats_with_features(self):
        features = make_features(
            total_volume=12345.67,
            transaction_count=42,
            velocity_score=3.5,
        )
        formatted = RISK_ANALYSIS_PROMPT.format(
            total_volume=features.total_volume,
            transaction_count=features.transaction_count,
            avg_transaction_size=features.avg_transaction_size,
            max_transaction_size=features.max_transaction_size,
            unique_counterparties=features.unique_counterparties,
            night_transaction_ratio=features.night_transaction_ratio,
            rapid_transaction_count=features.rapid_transaction_count,
            round_number_ratio=features.round_number_ratio,
            concentration_score=features.concentration_score,
            velocity_score=features.velocity_score,
        )
        assert "12345.67" in formatted
        assert "42" in formatted


# ---------------------------------------------------------------------------
# Tests: LLM response parsing (Requirements 4.3, 4.4, 4.5)
# ---------------------------------------------------------------------------

class TestParseLLMResponse:
    """Tests for _parse_llm_response(). Requirements 4.3, 4.4, 4.5"""

    def _valid_payload(self, **overrides) -> dict:
        base = {
            "risk_score": 45,
            "risk_level": "medium",
            "risk_factors": ["High volume", "Night transactions"],
            "explanation": "Moderate risk detected.",
            "confidence": 0.85,
        }
        base.update(overrides)
        return base

    def test_parses_valid_response(self):
        result = _parse_llm_response(json.dumps(self._valid_payload()))
        assert result["risk_score"] == pytest.approx(45.0)
        assert result["risk_level"] == "medium"
        assert result["risk_factors"] == ["High volume", "Night transactions"]
        assert result["explanation"] == "Moderate risk detected."
        assert result["confidence"] == pytest.approx(0.85)

    def test_extracts_json_from_surrounding_text(self):
        payload = self._valid_payload()
        text = "Here is my assessment:\n" + json.dumps(payload) + "\nEnd of response."
        result = _parse_llm_response(text)
        assert result["risk_score"] == pytest.approx(45.0)

    def test_raises_on_no_json(self):
        with pytest.raises(ValueError, match="No JSON object found"):
            _parse_llm_response("This is just plain text with no JSON.")

    def test_raises_on_missing_risk_score(self):
        payload = self._valid_payload()
        del payload["risk_score"]
        with pytest.raises(ValueError, match="missing required fields"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_missing_risk_level(self):
        payload = self._valid_payload()
        del payload["risk_level"]
        with pytest.raises(ValueError, match="missing required fields"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_missing_risk_factors(self):
        payload = self._valid_payload()
        del payload["risk_factors"]
        with pytest.raises(ValueError, match="missing required fields"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_missing_explanation(self):
        payload = self._valid_payload()
        del payload["explanation"]
        with pytest.raises(ValueError, match="missing required fields"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_missing_confidence(self):
        payload = self._valid_payload()
        del payload["confidence"]
        with pytest.raises(ValueError, match="missing required fields"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_risk_score_above_100(self):
        payload = self._valid_payload(risk_score=101)
        with pytest.raises(ValueError, match="risk_score"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_risk_score_below_0(self):
        payload = self._valid_payload(risk_score=-1)
        with pytest.raises(ValueError, match="risk_score"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_invalid_risk_level(self):
        payload = self._valid_payload(risk_level="extreme")
        with pytest.raises(ValueError, match="Invalid risk_level"):
            _parse_llm_response(json.dumps(payload))

    def test_corrects_mismatched_risk_level(self):
        # score=80 → CRITICAL, but LLM says "high"
        payload = self._valid_payload(risk_score=80, risk_level="high")
        result = _parse_llm_response(json.dumps(payload))
        assert result["risk_level"] == "critical"

    def test_raises_on_empty_risk_factors(self):
        payload = self._valid_payload(risk_factors=[])
        with pytest.raises(ValueError, match="risk_factors must be a non-empty list"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_risk_factors_not_list(self):
        payload = self._valid_payload(risk_factors="single factor")
        with pytest.raises(ValueError, match="risk_factors must be a non-empty list"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_confidence_above_1(self):
        payload = self._valid_payload(confidence=1.1)
        with pytest.raises(ValueError, match="confidence"):
            _parse_llm_response(json.dumps(payload))

    def test_raises_on_confidence_below_0(self):
        payload = self._valid_payload(confidence=-0.1)
        with pytest.raises(ValueError, match="confidence"):
            _parse_llm_response(json.dumps(payload))

    def test_boundary_risk_score_0(self):
        payload = self._valid_payload(risk_score=0, risk_level="low")
        result = _parse_llm_response(json.dumps(payload))
        assert result["risk_score"] == pytest.approx(0.0)

    def test_boundary_risk_score_100(self):
        payload = self._valid_payload(risk_score=100, risk_level="critical")
        result = _parse_llm_response(json.dumps(payload))
        assert result["risk_score"] == pytest.approx(100.0)

    def test_boundary_confidence_0(self):
        payload = self._valid_payload(confidence=0.0)
        result = _parse_llm_response(json.dumps(payload))
        assert result["confidence"] == pytest.approx(0.0)

    def test_boundary_confidence_1(self):
        payload = self._valid_payload(confidence=1.0)
        result = _parse_llm_response(json.dumps(payload))
        assert result["confidence"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Tests: Fallback rule-based scoring (Requirements 6.1 – 6.9)
# ---------------------------------------------------------------------------

class TestFallbackRiskScoring:
    """Tests for fallback_risk_scoring(). Requirements 6.1 – 6.9"""

    def test_no_risk_factors_gives_low_score(self):
        """All features below thresholds → score = 0, level = LOW."""
        features = make_features(
            total_volume=1_000.0,
            night_transaction_ratio=0.1,
            round_number_ratio=0.1,
            concentration_score=0.1,
            rapid_transaction_count=2,
            velocity_score=1.0,
        )
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score == pytest.approx(0.0)
        assert assessment.risk_level == RiskLevel.LOW

    def test_high_volume_adds_20_points(self):
        """total_volume > 100,000 → +20 pts. Requirement 6.2"""
        features = make_features(total_volume=200_000.0)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score >= 20.0
        assert "High transaction volume" in assessment.risk_factors

    def test_high_night_ratio_adds_15_points(self):
        """night_transaction_ratio > 0.3 → +15 pts. Requirement 6.3"""
        features = make_features(night_transaction_ratio=0.5)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score >= 15.0
        assert "Frequent night transactions" in assessment.risk_factors

    def test_high_round_number_ratio_adds_20_points(self):
        """round_number_ratio > 0.5 → +20 pts. Requirement 6.4"""
        features = make_features(round_number_ratio=0.8)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score >= 20.0
        assert "Suspicious round number amounts" in assessment.risk_factors

    def test_high_concentration_adds_15_points(self):
        """concentration_score > 0.7 → +15 pts. Requirement 6.5"""
        features = make_features(concentration_score=0.9)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score >= 15.0
        assert "High counterparty concentration" in assessment.risk_factors

    def test_rapid_transactions_adds_15_points(self):
        """rapid_transaction_count > 10 → +15 pts. Requirement 6.6"""
        features = make_features(rapid_transaction_count=15)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score >= 15.0
        assert "Rapid successive transactions" in assessment.risk_factors

    def test_high_velocity_adds_15_points(self):
        """velocity_score > 10 → +15 pts. Requirement 6.7"""
        features = make_features(velocity_score=20.0)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score >= 15.0
        assert "High transaction velocity" in assessment.risk_factors

    def test_all_risk_factors_triggered_caps_at_100(self):
        """All thresholds exceeded → score capped at 100. Requirement 6.8"""
        features = make_features(
            total_volume=200_000.0,
            night_transaction_ratio=0.5,
            round_number_ratio=0.8,
            concentration_score=0.9,
            rapid_transaction_count=15,
            velocity_score=20.0,
        )
        assessment = fallback_risk_scoring(features)
        # 20 + 15 + 20 + 15 + 15 + 15 = 100
        assert assessment.risk_score == pytest.approx(100.0)
        assert assessment.risk_level == RiskLevel.CRITICAL

    def test_confidence_is_0_7(self):
        """Fallback always sets confidence=0.7. Requirement 6.9 / 4.8"""
        features = make_features()
        assessment = fallback_risk_scoring(features)
        assert assessment.confidence == pytest.approx(0.7)

    def test_account_id_preserved(self):
        features = make_features(account_id="my_account")
        assessment = fallback_risk_scoring(features)
        assert assessment.account_id == "my_account"

    def test_returns_risk_assessment_type(self):
        features = make_features()
        assessment = fallback_risk_scoring(features)
        assert isinstance(assessment, RiskAssessment)

    def test_timestamp_is_datetime(self):
        features = make_features()
        assessment = fallback_risk_scoring(features)
        assert isinstance(assessment.timestamp, datetime)

    def test_explanation_mentions_risk_factors(self):
        features = make_features(total_volume=200_000.0)
        assessment = fallback_risk_scoring(features)
        assert "High transaction volume" in assessment.explanation

    def test_no_risk_factors_gives_default_message(self):
        """When no rules trigger, a default message is used."""
        features = make_features()
        assessment = fallback_risk_scoring(features)
        assert "No significant risk indicators detected" in assessment.risk_factors

    def test_boundary_volume_exactly_100000_no_trigger(self):
        """total_volume == 100,000 does NOT trigger (must be strictly >). Requirement 6.2"""
        features = make_features(total_volume=100_000.0)
        assessment = fallback_risk_scoring(features)
        assert "High transaction volume" not in assessment.risk_factors

    def test_boundary_night_ratio_exactly_0_3_no_trigger(self):
        """night_transaction_ratio == 0.3 does NOT trigger. Requirement 6.3"""
        features = make_features(night_transaction_ratio=0.3)
        assessment = fallback_risk_scoring(features)
        assert "Frequent night transactions" not in assessment.risk_factors

    def test_boundary_round_ratio_exactly_0_5_no_trigger(self):
        """round_number_ratio == 0.5 does NOT trigger. Requirement 6.4"""
        features = make_features(round_number_ratio=0.5)
        assessment = fallback_risk_scoring(features)
        assert "Suspicious round number amounts" not in assessment.risk_factors

    def test_boundary_concentration_exactly_0_7_no_trigger(self):
        """concentration_score == 0.7 does NOT trigger. Requirement 6.5"""
        features = make_features(concentration_score=0.7)
        assessment = fallback_risk_scoring(features)
        assert "High counterparty concentration" not in assessment.risk_factors

    def test_boundary_rapid_count_exactly_10_no_trigger(self):
        """rapid_transaction_count == 10 does NOT trigger. Requirement 6.6"""
        features = make_features(rapid_transaction_count=10)
        assessment = fallback_risk_scoring(features)
        assert "Rapid successive transactions" not in assessment.risk_factors

    def test_boundary_velocity_exactly_10_no_trigger(self):
        """velocity_score == 10 does NOT trigger. Requirement 6.7"""
        features = make_features(velocity_score=10.0)
        assessment = fallback_risk_scoring(features)
        assert "High transaction velocity" not in assessment.risk_factors


# ---------------------------------------------------------------------------
# Tests: Risk level classification (Requirements 7.1 – 7.5)
# ---------------------------------------------------------------------------

class TestRiskLevelClassification:
    """Tests for risk level boundaries via fallback_risk_scoring. Requirements 7.1 – 7.5"""

    def _score_for(self, features: TransactionFeatures) -> float:
        return fallback_risk_scoring(features).risk_score

    def test_score_0_is_low(self):
        features = make_features()
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_level == RiskLevel.LOW

    def test_score_20_is_low(self):
        # Only high volume triggers (+20) → score=20 → LOW
        features = make_features(total_volume=200_000.0)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score == pytest.approx(20.0)
        assert assessment.risk_level == RiskLevel.LOW

    def test_score_35_is_medium(self):
        # volume (+20) + night (+15) = 35 → MEDIUM
        features = make_features(total_volume=200_000.0, night_transaction_ratio=0.5)
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score == pytest.approx(35.0)
        assert assessment.risk_level == RiskLevel.MEDIUM

    def test_score_55_is_high(self):
        # volume (+20) + night (+15) + round (+20) = 55 → HIGH
        features = make_features(
            total_volume=200_000.0,
            night_transaction_ratio=0.5,
            round_number_ratio=0.8,
        )
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score == pytest.approx(55.0)
        assert assessment.risk_level == RiskLevel.HIGH

    def test_score_100_is_critical(self):
        features = make_features(
            total_volume=200_000.0,
            night_transaction_ratio=0.5,
            round_number_ratio=0.8,
            concentration_score=0.9,
            rapid_transaction_count=15,
            velocity_score=20.0,
        )
        assessment = fallback_risk_scoring(features)
        assert assessment.risk_score == pytest.approx(100.0)
        assert assessment.risk_level == RiskLevel.CRITICAL

    def test_risk_level_matches_score_for_all_combinations(self):
        """risk_level must always match risk_score range."""
        test_cases = [
            make_features(),
            make_features(total_volume=200_000.0),
            make_features(total_volume=200_000.0, night_transaction_ratio=0.5),
            make_features(total_volume=200_000.0, night_transaction_ratio=0.5, round_number_ratio=0.8),
            make_features(
                total_volume=200_000.0,
                night_transaction_ratio=0.5,
                round_number_ratio=0.8,
                concentration_score=0.9,
            ),
        ]
        for features in test_cases:
            assessment = fallback_risk_scoring(features)
            expected = RiskLevel.from_score(assessment.risk_score)
            assert assessment.risk_level == expected, (
                f"score={assessment.risk_score}: expected {expected.value}, "
                f"got {assessment.risk_level.value}"
            )


# ---------------------------------------------------------------------------
# Tests: analyze_risk_with_bedrock – rate limiter integration (Requirement 4.2)
# ---------------------------------------------------------------------------

class TestAnalyzeRiskWithBedrock:
    """Tests for analyze_risk_with_bedrock(). Requirements 4.1, 4.2, 4.3, 4.4, 4.5"""

    def _valid_llm_payload(self, score: float = 45.0, level: str = "medium") -> dict:
        return {
            "risk_score": score,
            "risk_level": level,
            "risk_factors": ["Moderate volume"],
            "explanation": "Moderate risk.",
            "confidence": 0.9,
        }

    def test_calls_rate_limiter_before_bedrock(self):
        """Rate limiter must be called before the Bedrock API. Requirement 4.2"""
        features = make_features()
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.return_value = make_bedrock_response(
            self._valid_llm_payload()
        )

        call_order = []
        rate_limiter.wait_if_needed.side_effect = lambda: call_order.append("rate_limiter")
        bedrock_client.invoke_model.side_effect = lambda **kwargs: (
            call_order.append("bedrock") or make_bedrock_response(self._valid_llm_payload())
        )

        analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        assert call_order[0] == "rate_limiter", "Rate limiter must be called before Bedrock"
        assert "bedrock" in call_order

    def test_rate_limiter_called_exactly_once(self):
        """Rate limiter is called exactly once per analysis. Requirement 4.2"""
        features = make_features()
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.return_value = make_bedrock_response(
            self._valid_llm_payload()
        )

        analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        rate_limiter.wait_if_needed.assert_called_once()

    def test_returns_risk_assessment_on_success(self):
        """Successful Bedrock call returns a RiskAssessment. Requirement 4.3"""
        features = make_features()
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.return_value = make_bedrock_response(
            self._valid_llm_payload(score=45.0, level="medium")
        )

        assessment = analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        assert isinstance(assessment, RiskAssessment)
        assert assessment.account_id == features.account_id
        assert assessment.risk_score == pytest.approx(45.0)
        assert assessment.risk_level == RiskLevel.MEDIUM

    def test_falls_back_on_bedrock_exception(self):
        """Bedrock failure triggers fallback scoring. Requirement 4.6"""
        features = make_features()
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.side_effect = Exception("Bedrock unavailable")

        assessment = analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        # Fallback always sets confidence=0.7
        assert assessment.confidence == pytest.approx(0.7)
        assert assessment.account_id == features.account_id

    def test_falls_back_on_invalid_llm_response(self):
        """Invalid LLM JSON triggers fallback scoring. Requirement 4.6"""
        features = make_features()
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        # Return a response with no JSON
        body_bytes = json.dumps({
            "content": [{"text": "I cannot assess this."}]
        }).encode("utf-8")
        bedrock_client.invoke_model.return_value = {"body": BytesIO(body_bytes)}

        assessment = analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        assert assessment.confidence == pytest.approx(0.7)

    def test_bedrock_invoked_with_correct_model_id(self):
        """Bedrock is called with the expected model ID."""
        features = make_features()
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.return_value = make_bedrock_response(
            self._valid_llm_payload()
        )

        analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        call_kwargs = bedrock_client.invoke_model.call_args[1]
        assert call_kwargs["modelId"] == "anthropic.claude-3-sonnet-20240229-v1:0"

    def test_prompt_includes_feature_values(self):
        """The prompt sent to Bedrock contains the actual feature values."""
        features = make_features(total_volume=99_999.0, transaction_count=7)
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.return_value = make_bedrock_response(
            self._valid_llm_payload()
        )

        analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        call_kwargs = bedrock_client.invoke_model.call_args[1]
        body = json.loads(call_kwargs["body"])
        prompt_text = body["messages"][0]["content"]
        assert "99999.0" in prompt_text
        assert "7" in prompt_text

    def test_assessment_account_id_matches_features(self):
        """Returned assessment has the same account_id as the input features."""
        features = make_features(account_id="special_account")
        rate_limiter = make_rate_limiter()
        bedrock_client = MagicMock()
        bedrock_client.invoke_model.return_value = make_bedrock_response(
            self._valid_llm_payload()
        )

        assessment = analyze_risk_with_bedrock(features, rate_limiter, bedrock_client)

        assert assessment.account_id == "special_account"
