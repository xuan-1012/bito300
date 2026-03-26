"""
ExplainabilityModule — top-level orchestrator for the Explainability Module.

Wires together:
  - FeatureContributionCalculator
  - ReasonCodeAssigner
  - NaturalLanguageGenerator
  - RuleExplainer
  - OutputFormatters
  - ExplanationValidator
  - ExplanationPersistence

Public API:
  explain(assessment, language, use_bedrock) -> Explanation
  explain_batch(assessments, language, use_bedrock) -> BatchResult

Requirements: 1.1–1.9, 6.1–6.7, 8.1–8.8, 15.1–15.7, 16.1–16.8
"""

import logging
import time
from datetime import datetime, timezone
from typing import List, Optional

from src.common.models import RiskAssessment, RiskLevel
from src.explainability.feature_contribution import FeatureContributionCalculator
from src.explainability.formatters import OutputFormatters
from src.explainability.models import BatchResult, Explanation
from src.explainability.nlg import NaturalLanguageGenerator
from src.explainability.persistence import ExplanationPersistence
from src.explainability.reason_codes import ReasonCodeAssigner
from src.explainability.rule_explainer import RuleExplainer
from src.explainability.validator import ExplanationValidator, ExplanationValidationError

logger = logging.getLogger(__name__)


class ExplainabilityModule:
    """
    Orchestrates the full explanation generation pipeline for a single account
    or a batch of accounts.

    Args:
        persistence: Optional ExplanationPersistence instance. When None,
                     persistence is skipped (useful for testing).
        feature_calculator: Optional FeatureContributionCalculator override.
        reason_assigner: Optional ReasonCodeAssigner override.
        nlg: Optional NaturalLanguageGenerator override.
        rule_explainer: Optional RuleExplainer override.
        formatters: Optional OutputFormatters override.
        validator: Optional ExplanationValidator override.
    """

    def __init__(
        self,
        persistence: Optional[ExplanationPersistence] = None,
        feature_calculator: Optional[FeatureContributionCalculator] = None,
        reason_assigner: Optional[ReasonCodeAssigner] = None,
        nlg: Optional[NaturalLanguageGenerator] = None,
        rule_explainer: Optional[RuleExplainer] = None,
        formatters: Optional[OutputFormatters] = None,
        validator: Optional[ExplanationValidator] = None,
    ) -> None:
        self._persistence = persistence
        self._feature_calculator = feature_calculator or FeatureContributionCalculator()
        self._reason_assigner = reason_assigner or ReasonCodeAssigner()
        self._nlg = nlg or NaturalLanguageGenerator()
        self._rule_explainer = rule_explainer or RuleExplainer()
        self._formatters = formatters or OutputFormatters()
        self._validator = validator or ExplanationValidator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def explain(
        self,
        assessment: RiskAssessment,
        language: str = "en",
        use_bedrock: bool = True,
    ) -> Explanation:
        """
        Generate a full Explanation for a single RiskAssessment.

        Args:
            assessment: The risk assessment to explain.
            language: Language code — "en" or "zh-TW".
            use_bedrock: When True, attempt Bedrock LLM generation first.

        Returns:
            A validated, persisted Explanation object.

        Raises:
            ValueError: If risk_score is outside [0, 100].
            ExplanationValidationError: If the generated explanation fails validation.
        """
        # Requirement 1.2 / error-handling spec: validate risk_score immediately
        if not (0 <= assessment.risk_score <= 100):
            raise ValueError(
                f"risk_score must be between 0 and 100, got {assessment.risk_score}"
            )

        start_time = time.monotonic()

        # 1. Feature contributions
        contributions = self._feature_calculator.calculate(assessment)
        top_features = self._feature_calculator.get_top_features(
            contributions, assessment=assessment
        )

        # 2. Reason codes
        reason_codes = self._reason_assigner.assign(assessment.risk_factors or [])

        # 3. Rule decomposition (rule-based assessments only)
        triggered_rules = None
        if getattr(assessment, "triggered_rules", None):
            triggered_rules = self._rule_explainer.explain(assessment)

        # 4. Natural language generation
        # When use_bedrock=False, skip Bedrock and go straight to templates.
        if use_bedrock:
            summary, is_fallback = self._nlg.generate(
                assessment, top_features, language=language
            )
        else:
            summary = self._nlg._generate_from_template(
                assessment, top_features, language=language
            )
            is_fallback = True

        generation_time_ms = (time.monotonic() - start_time) * 1000.0

        # 5. Build Explanation
        explanation = Explanation(
            account_id=assessment.account_id,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            reason_codes=reason_codes,
            top_features=top_features,
            feature_contributions=contributions,
            natural_language_summary=summary,
            language=language,
            is_fallback=is_fallback,
            is_validated=False,
            generated_at=datetime.now(timezone.utc),
            generation_time_ms=generation_time_ms,
            triggered_rules=triggered_rules,
        )

        # 6. Validate
        try:
            self._validator.validate(explanation)
        except ExplanationValidationError as exc:
            # Requirement 13.7: log validation error
            logger.error(
                "Explanation validation failed: error=%s, risk_level=%s",
                str(exc),
                assessment.risk_level.value,
            )
            raise

        # 7. Persist (optional — skipped when no persistence layer configured)
        if self._persistence is not None:
            try:
                s3_uri = self._persistence.store(explanation)
                explanation.s3_uri = s3_uri
            except IOError as exc:
                # Log but do not fail — explanation is still returned
                logger.error(
                    "Failed to persist explanation: error=%s, risk_level=%s",
                    str(exc),
                    explanation.risk_level.value,
                )

        # 8. CloudWatch audit log (Req 16.1–16.7: no account_id or amounts)
        method = "template" if is_fallback else "bedrock"
        logger.info(
            "Explanation generated: method=%s, generation_time_ms=%.1f, "
            "risk_level=%s",
            method,
            generation_time_ms,
            explanation.risk_level.value,
        )

        return explanation

    def explain_batch(
        self,
        assessments: List[RiskAssessment],
        language: str = "en",
        use_bedrock: bool = True,
    ) -> BatchResult:
        """
        Generate explanations for a list of RiskAssessment objects.

        Processing is sequential. Errors for individual accounts are captured
        in BatchResult.errors and do not abort the batch.

        Args:
            assessments: List of RiskAssessment objects to explain.
            language: Language code — "en" or "zh-TW".
            use_bedrock: When True, attempt Bedrock LLM generation first.

        Returns:
            BatchResult with explanations, counts, and per-account errors.
            Never raises — always returns a BatchResult.
        """
        total = len(assessments)
        explanations: List[Explanation] = []
        errors = {}

        for assessment in assessments:
            try:
                explanation = self.explain(
                    assessment, language=language, use_bedrock=use_bedrock
                )
                explanations.append(explanation)
            except Exception as exc:
                account_id = getattr(assessment, "account_id", "<unknown>")
                error_msg = str(exc)
                errors[account_id] = error_msg
                # Requirement 6.4: log error and continue
                logger.error(
                    "Batch explanation failed for one account: "
                    "error=%s, risk_level=%s",
                    error_msg,
                    getattr(assessment.risk_level, "value", "unknown")
                    if hasattr(assessment, "risk_level")
                    else "unknown",
                )

        successful = len(explanations)
        failed = len(errors)

        # Requirement 16.1: log batch generation event (no account identifiers)
        logger.info(
            "Batch explanation complete: total=%d, successful=%d, failed=%d",
            total,
            successful,
            failed,
        )

        return BatchResult(
            explanations=explanations,
            total=total,
            successful=successful,
            failed=failed,
            errors=errors,
        )
