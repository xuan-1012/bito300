"""
Output formatters for the Explainability Module.

Converts an Explanation object into JSON, plain text, HTML, or a UI short summary.
"""

import html
import json
from dataclasses import asdict

from src.common.models import RiskLevel
from src.explainability.models import Explanation

# Risk-level color coding for HTML output
_HTML_COLORS = {
    RiskLevel.CRITICAL: "red",
    RiskLevel.HIGH: "orange",
    RiskLevel.MEDIUM: "yellow",
    RiskLevel.LOW: "green",
}

# UI summary prefixes per risk level
_UI_PREFIXES = {
    RiskLevel.CRITICAL: "🚨 CRITICAL:",
    RiskLevel.HIGH: "⚠️ HIGH RISK:",
    RiskLevel.MEDIUM: "⚡ MEDIUM RISK:",
    RiskLevel.LOW: "✓ LOW RISK:",
}

_UI_SUMMARY_MAX_LEN = 200


class OutputFormatters:
    """Converts Explanation objects to various output formats."""

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    def to_json(self, explanation: Explanation) -> str:
        """
        Serialize an Explanation to a JSON string.

        Includes all required fields: account_id, risk_score, risk_level,
        reason_codes, top_features, natural_language_summary, and
        feature_contributions.
        """
        data = {
            "account_id": explanation.account_id,
            "risk_score": explanation.risk_score,
            "risk_level": explanation.risk_level.value,
            "reason_codes": explanation.reason_codes,
            "top_features": [
                {
                    "feature_name": fc.feature_name,
                    "contribution": fc.contribution,
                    "raw_value": fc.raw_value,
                    "context_label": fc.context_label,
                }
                for fc in explanation.top_features
            ],
            "natural_language_summary": explanation.natural_language_summary,
            "feature_contributions": explanation.feature_contributions,
            # Additional informational fields
            "language": explanation.language,
            "is_fallback": explanation.is_fallback,
            "is_validated": explanation.is_validated,
            "generated_at": explanation.generated_at.isoformat(),
            "generation_time_ms": explanation.generation_time_ms,
            "s3_uri": explanation.s3_uri,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Plain text
    # ------------------------------------------------------------------

    def to_text(self, explanation: Explanation) -> str:
        """
        Format an Explanation as human-readable paragraphs.
        """
        lines = []

        lines.append(
            f"Risk Assessment for Account: {explanation.account_id}"
        )
        lines.append(
            f"Risk Score: {explanation.risk_score:.1f} "
            f"({explanation.risk_level.value.upper()})"
        )
        lines.append("")

        lines.append("Summary:")
        lines.append(explanation.natural_language_summary)
        lines.append("")

        if explanation.reason_codes:
            lines.append("Reason Codes:")
            for code in explanation.reason_codes:
                lines.append(f"  - {code}")
            lines.append("")

        if explanation.top_features:
            lines.append("Top Contributing Features:")
            for fc in explanation.top_features:
                raw = (
                    f" (raw value: {fc.raw_value})"
                    if fc.raw_value is not None
                    else ""
                )
                lines.append(
                    f"  - {fc.feature_name}: {fc.contribution:.2%}{raw} "
                    f"[{fc.context_label}]"
                )
            lines.append("")

        if explanation.feature_contributions:
            lines.append("All Feature Contributions:")
            for name, contrib in explanation.feature_contributions.items():
                lines.append(f"  - {name}: {contrib:.2%}")
            lines.append("")

        lines.append(
            f"Generated at: {explanation.generated_at.isoformat()} "
            f"({explanation.generation_time_ms:.1f} ms)"
        )
        if explanation.is_fallback:
            lines.append("Note: Template-based fallback explanation was used.")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------------

    def to_html(self, explanation: Explanation) -> str:
        """
        Format an Explanation as an HTML report.

        - Color-codes the risk level header (red/orange/yellow/green).
        - HTML-escapes all text content to prevent injection.
        """
        color = _HTML_COLORS.get(explanation.risk_level, "grey")
        level_str = html.escape(explanation.risk_level.value.upper())
        account_id = html.escape(explanation.account_id)
        summary = html.escape(explanation.natural_language_summary)

        reason_items = "".join(
            f"<li>{html.escape(code)}</li>"
            for code in explanation.reason_codes
        )

        feature_rows = "".join(
            "<tr>"
            f"<td>{html.escape(fc.feature_name)}</td>"
            f"<td>{fc.contribution:.2%}</td>"
            f"<td>{html.escape(str(fc.raw_value) if fc.raw_value is not None else '')}</td>"
            f"<td>{html.escape(fc.context_label)}</td>"
            "</tr>"
            for fc in explanation.top_features
        )

        all_contrib_rows = "".join(
            "<tr>"
            f"<td>{html.escape(name)}</td>"
            f"<td>{contrib:.2%}</td>"
            "</tr>"
            for name, contrib in explanation.feature_contributions.items()
        )

        fallback_note = (
            "<p><em>Note: Template-based fallback explanation was used.</em></p>"
            if explanation.is_fallback
            else ""
        )

        return (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head><meta charset='utf-8'>"
            "<title>Risk Explanation</title></head>\n"
            "<body>\n"
            f"<h1>Risk Assessment: {account_id}</h1>\n"
            f"<h2 style='color:{color};'>"
            f"Risk Level: {level_str} "
            f"(Score: {explanation.risk_score:.1f})"
            "</h2>\n"
            "<section>\n"
            "<h3>Summary</h3>\n"
            f"<p>{summary}</p>\n"
            f"{fallback_note}"
            "</section>\n"
            "<section>\n"
            "<h3>Reason Codes</h3>\n"
            f"<ul>{reason_items}</ul>\n"
            "</section>\n"
            "<section>\n"
            "<h3>Top Contributing Features</h3>\n"
            "<table border='1'>\n"
            "<thead><tr>"
            "<th>Feature</th><th>Contribution</th>"
            "<th>Raw Value</th><th>Context</th>"
            "</tr></thead>\n"
            f"<tbody>{feature_rows}</tbody>\n"
            "</table>\n"
            "</section>\n"
            "<section>\n"
            "<h3>All Feature Contributions</h3>\n"
            "<table border='1'>\n"
            "<thead><tr><th>Feature</th><th>Contribution</th></tr></thead>\n"
            f"<tbody>{all_contrib_rows}</tbody>\n"
            "</table>\n"
            "</section>\n"
            f"<footer><small>Generated at: "
            f"{html.escape(explanation.generated_at.isoformat())} "
            f"({explanation.generation_time_ms:.1f} ms)</small></footer>\n"
            "</body>\n"
            "</html>"
        )

    # ------------------------------------------------------------------
    # UI short summary
    # ------------------------------------------------------------------

    def to_ui_summary(self, explanation: Explanation) -> str:
        """
        Generate a UI-friendly short summary (<= 200 characters).

        Format: "<prefix> Score <score> | <primary_factor>. <summary_snippet>"
        Truncated with "..." if the natural content exceeds 200 characters.
        """
        prefix = _UI_PREFIXES.get(explanation.risk_level, "")

        # Primary risk factor: first reason code, or first top feature name
        if explanation.reason_codes:
            primary_factor = explanation.reason_codes[0]
        elif explanation.top_features:
            primary_factor = explanation.top_features[0].feature_name
        else:
            primary_factor = "unknown"

        score_str = f"{explanation.risk_score:.1f}"

        # Build the core content (without truncation)
        core = f"{prefix} Score {score_str} | {primary_factor}"

        if len(core) >= _UI_SUMMARY_MAX_LEN:
            # Even the core is too long — truncate it
            return core[: _UI_SUMMARY_MAX_LEN - 3] + "..."

        # Try to append a snippet of the natural language summary
        remaining = _UI_SUMMARY_MAX_LEN - len(core) - 2  # 2 for ". "
        if remaining > 0 and explanation.natural_language_summary:
            snippet = explanation.natural_language_summary
            if len(snippet) > remaining:
                # Need to truncate; account for "..."
                snippet = snippet[: remaining - 3] + "..."
            result = f"{core}. {snippet}"
        else:
            result = core

        # Final safety check
        if len(result) > _UI_SUMMARY_MAX_LEN:
            result = result[: _UI_SUMMARY_MAX_LEN - 3] + "..."

        return result
