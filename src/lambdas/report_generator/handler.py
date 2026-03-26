"""
Report Generator Lambda Handler

Generates summary statistics, charts, and an HTML presentation report
from risk assessments stored in S3/DynamoDB.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9,
              9.4, 13.6, 16.1, 16.2, 16.3, 16.4, 16.5
"""

import base64
import io
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.common.models import AnalysisReport, RiskAssessment, RiskLevel
from src.common.aws_clients import get_aws_clients

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """Parse s3://bucket/key into (bucket, key)."""
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    path = s3_uri[len("s3://"):]
    bucket, _, key = path.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 URI (missing bucket or key): {s3_uri}")
    return bucket, key


def _dict_to_risk_assessment(raw: Dict[str, Any]) -> Optional[RiskAssessment]:
    """Convert a raw dict to a RiskAssessment, returning None on failure."""
    try:
        return RiskAssessment(
            account_id=raw["account_id"],
            risk_score=float(raw["risk_score"]),
            risk_level=RiskLevel(raw["risk_level"]),
            risk_factors=raw["risk_factors"],
            explanation=raw["explanation"],
            confidence=float(raw["confidence"]),
            timestamp=datetime.fromisoformat(raw["timestamp"]),
        )
    except Exception as exc:
        logger.error(f"Failed to parse risk assessment dict: {exc}")
        return None


# ---------------------------------------------------------------------------
# Task 8.1 – Summary statistics
# Requirements: 8.1, 8.2, 8.3, 8.4
# ---------------------------------------------------------------------------

def generate_summary_report(
    risk_assessments: List[RiskAssessment],
    total_transactions: int = 0,
) -> Dict[str, Any]:
    """
    Calculate summary statistics from a list of risk assessments.

    Args:
        risk_assessments: All risk assessments for the analysis run.
        total_transactions: Total number of raw transactions processed.

    Returns:
        Dictionary with:
            - total_accounts (int)
            - total_transactions (int)
            - risk_distribution (dict[str, int])
            - average_risk_score (float)
            - top_suspicious_accounts (list[dict])
    """
    total_accounts = len(risk_assessments)

    # Requirement 8.2: risk_distribution by risk_level
    risk_distribution: Dict[str, int] = {level.value: 0 for level in RiskLevel}
    for assessment in risk_assessments:
        risk_distribution[assessment.risk_level.value] += 1

    # Requirement 8.3: average_risk_score
    if total_accounts > 0:
        average_risk_score = sum(a.risk_score for a in risk_assessments) / total_accounts
    else:
        average_risk_score = 0.0

    # Requirement 8.4: top_suspicious_accounts sorted by risk_score descending
    sorted_assessments = sorted(risk_assessments, key=lambda a: a.risk_score, reverse=True)
    top_suspicious_accounts = [
        {
            "account_id": a.account_id,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level.value,
            "risk_factors": a.risk_factors,
            "explanation": a.explanation,
            "confidence": a.confidence,
        }
        for a in sorted_assessments[:10]
    ]

    return {
        "total_accounts": total_accounts,
        "total_transactions": total_transactions,
        "risk_distribution": risk_distribution,
        "average_risk_score": round(average_risk_score, 2),
        "top_suspicious_accounts": top_suspicious_accounts,
    }


# ---------------------------------------------------------------------------
# Task 8.2 – Chart generation
# Requirements: 8.5, 8.6, 8.7
# ---------------------------------------------------------------------------

def _chart_to_base64(fig) -> str:
    """Render a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _upload_bytes_to_s3(aws_clients, bucket: str, key: str, data: bytes, content_type: str) -> str:
    """Upload raw bytes to S3 with AES256 encryption and return the S3 URI."""
    aws_clients.s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
        ServerSideEncryption="AES256",
    )
    return f"s3://{bucket}/{key}"


def generate_risk_distribution_chart(
    risk_assessments: List[RiskAssessment],
    aws_clients,
    bucket: str,
    key_prefix: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate a risk-level distribution pie chart and upload to S3.

    Requirements: 8.5, 8.7

    Returns:
        (s3_uri, base64_png) – s3_uri is None when upload fails;
        base64_png is None when matplotlib is unavailable.
    """
    risk_distribution: Dict[str, int] = {level.value: 0 for level in RiskLevel}
    for a in risk_assessments:
        risk_distribution[a.risk_level.value] += 1

    colors = {
        RiskLevel.LOW.value: "#4CAF50",
        RiskLevel.MEDIUM.value: "#FF9800",
        RiskLevel.HIGH.value: "#F44336",
        RiskLevel.CRITICAL.value: "#9C27B0",
    }

    labels = []
    sizes = []
    chart_colors = []
    for level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
        count = risk_distribution[level.value]
        if count > 0:
            labels.append(f"{level.value.capitalize()} ({count})")
            sizes.append(count)
            chart_colors.append(colors[level.value])

    base64_png: Optional[str] = None
    s3_uri: Optional[str] = None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6))
        if sizes:
            ax.pie(sizes, labels=labels, colors=chart_colors, autopct="%1.1f%%", startangle=90)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Risk Level Distribution", fontsize=16, fontweight="bold", pad=20)
        fig.tight_layout()

        base64_png = _chart_to_base64(fig)
        plt.close(fig)

        # Upload to S3 (Requirement 8.7)
        buf = io.BytesIO(base64.b64decode(base64_png))
        key = f"{key_prefix}risk_distribution.png"
        try:
            s3_uri = _upload_bytes_to_s3(aws_clients, bucket, key, buf.read(), "image/png")
            logger.info(f"Risk distribution chart stored at {s3_uri}")
        except Exception as upload_err:
            logger.warning(f"Failed to upload risk distribution chart: {upload_err}")

    except ImportError:
        logger.warning("matplotlib not available – skipping risk distribution chart generation")

    return s3_uri, base64_png


def generate_risk_score_histogram(
    risk_assessments: List[RiskAssessment],
    aws_clients,
    bucket: str,
    key_prefix: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate a risk score histogram and upload to S3.

    Requirements: 8.6, 8.7

    Returns:
        (s3_uri, base64_png)
    """
    scores = [a.risk_score for a in risk_assessments]

    base64_png: Optional[str] = None
    s3_uri: Optional[str] = None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        if scores:
            ax.hist(scores, bins=20, range=(0, 100), color="#2196F3", edgecolor="white", alpha=0.85)
        ax.set_xlabel("Risk Score", fontsize=13)
        ax.set_ylabel("Number of Accounts", fontsize=13)
        ax.set_title("Risk Score Distribution", fontsize=16, fontweight="bold")
        ax.set_xlim(0, 100)

        # Add vertical lines for risk level boundaries
        for boundary, label, color in [
            (25, "LOW/MED", "#4CAF50"),
            (50, "MED/HIGH", "#FF9800"),
            (75, "HIGH/CRIT", "#F44336"),
        ]:
            ax.axvline(x=boundary, color=color, linestyle="--", linewidth=1.5, alpha=0.7)
            ax.text(boundary + 1, ax.get_ylim()[1] * 0.95, label, color=color, fontsize=9)

        fig.tight_layout()
        base64_png = _chart_to_base64(fig)
        plt.close(fig)

        buf = io.BytesIO(base64.b64decode(base64_png))
        key = f"{key_prefix}risk_score_histogram.png"
        try:
            s3_uri = _upload_bytes_to_s3(aws_clients, bucket, key, buf.read(), "image/png")
            logger.info(f"Risk score histogram stored at {s3_uri}")
        except Exception as upload_err:
            logger.warning(f"Failed to upload risk score histogram: {upload_err}")

    except ImportError:
        logger.warning("matplotlib not available – skipping risk score histogram generation")

    return s3_uri, base64_png


# ---------------------------------------------------------------------------
# Task 8.3 – HTML presentation generator
# Requirements: 8.8, 16.1, 16.2, 16.3, 16.4
# ---------------------------------------------------------------------------

def _embed_chart(base64_png: Optional[str], alt: str) -> str:
    """Return an <img> tag with embedded base64 PNG, or a placeholder."""
    if base64_png:
        return f'<img src="data:image/png;base64,{base64_png}" alt="{alt}" class="chart-img">'
    return f'<div class="chart-placeholder"><p>Chart unavailable ({alt})</p></div>'


def generate_presentation_slides(
    summary: Dict[str, Any],
    pie_chart_b64: Optional[str],
    histogram_b64: Optional[str],
    created_at: datetime,
) -> str:
    """
    Generate a professional HTML presentation report.

    Requirements: 8.8, 16.1, 16.2, 16.3, 16.4

    Args:
        summary: Output of generate_summary_report().
        pie_chart_b64: Base64-encoded PNG of the risk distribution pie chart.
        histogram_b64: Base64-encoded PNG of the risk score histogram.
        created_at: Report creation timestamp.

    Returns:
        HTML string.
    """
    risk_dist = summary.get("risk_distribution", {})
    top_accounts = summary.get("top_suspicious_accounts", [])
    avg_score = summary.get("average_risk_score", 0.0)
    total_accounts = summary.get("total_accounts", 0)
    total_transactions = summary.get("total_transactions", 0)

    # Risk level badge colours
    level_colors = {
        "low": "#4CAF50",
        "medium": "#FF9800",
        "high": "#F44336",
        "critical": "#9C27B0",
    }

    # Build top-accounts table rows
    table_rows = ""
    for rank, acct in enumerate(top_accounts[:10], start=1):
        level = acct.get("risk_level", "low")
        color = level_colors.get(level, "#999")
        factors = ", ".join(acct.get("risk_factors", []))
        explanation = acct.get("explanation", "")
        table_rows += f"""
        <tr>
          <td class="rank">{rank}</td>
          <td class="account-id">{acct.get('account_id', '')}</td>
          <td><span class="badge" style="background:{color}">{level.upper()}</span></td>
          <td class="score">{acct.get('risk_score', 0):.1f}</td>
          <td class="factors">{factors}</td>
          <td class="explanation">{explanation}</td>
        </tr>"""

    # Distribution summary cards
    dist_cards = ""
    for level in ["critical", "high", "medium", "low"]:
        count = risk_dist.get(level, 0)
        color = level_colors.get(level, "#999")
        dist_cards += f"""
        <div class="stat-card" style="border-top: 4px solid {color}">
          <div class="stat-value" style="color:{color}">{count}</div>
          <div class="stat-label">{level.upper()}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crypto Suspicious Account Detection Report</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #333; }}
    .header {{ background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
               color: white; padding: 40px; text-align: center; }}
    .header h1 {{ font-size: 2.2em; margin-bottom: 8px; }}
    .header p {{ opacity: 0.85; font-size: 1em; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
    .section {{ background: white; border-radius: 10px; padding: 30px;
                margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
    .section h2 {{ font-size: 1.5em; color: #1a237e; margin-bottom: 20px;
                   padding-bottom: 10px; border-bottom: 2px solid #e8eaf6; }}
    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                   gap: 20px; margin-bottom: 20px; }}
    .stat-card {{ background: #fafafa; border-radius: 8px; padding: 20px;
                  text-align: center; border-top: 4px solid #1a237e; }}
    .stat-value {{ font-size: 2.2em; font-weight: 700; color: #1a237e; }}
    .stat-label {{ font-size: 0.85em; color: #666; margin-top: 6px; text-transform: uppercase;
                   letter-spacing: 0.5px; }}
    .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
    .chart-img {{ width: 100%; border-radius: 8px; border: 1px solid #e0e0e0; }}
    .chart-placeholder {{ background: #f5f5f5; border-radius: 8px; padding: 40px;
                          text-align: center; color: #999; border: 1px dashed #ccc; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
    th {{ background: #1a237e; color: white; padding: 12px 10px; text-align: left;
          font-weight: 600; }}
    td {{ padding: 10px; border-bottom: 1px solid #e8eaf6; vertical-align: top; }}
    tr:hover td {{ background: #f5f7ff; }}
    .rank {{ font-weight: 700; color: #1a237e; text-align: center; width: 40px; }}
    .account-id {{ font-family: monospace; font-size: 0.85em; color: #555; }}
    .score {{ font-weight: 700; text-align: center; }}
    .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px;
              color: white; font-size: 0.78em; font-weight: 700; }}
    .factors {{ color: #555; font-size: 0.85em; }}
    .explanation {{ color: #666; font-size: 0.82em; max-width: 300px; }}
    .footer {{ text-align: center; color: #999; font-size: 0.85em; padding: 20px; }}
    @media (max-width: 768px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🔍 Crypto Suspicious Account Detection</h1>
    <p>Risk Analysis Report &nbsp;|&nbsp; Generated: {created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
  </div>

  <div class="container">

    <!-- Executive Summary (Requirement 16.1) -->
    <div class="section">
      <h2>📊 Executive Summary</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{total_accounts}</div>
          <div class="stat-label">Accounts Analyzed</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{total_transactions}</div>
          <div class="stat-label">Transactions Processed</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{avg_score:.1f}</div>
          <div class="stat-label">Avg Risk Score</div>
        </div>
        {dist_cards}
      </div>
    </div>

    <!-- Charts (Requirement 16.2) -->
    <div class="section">
      <h2>📈 Risk Visualizations</h2>
      <div class="charts-grid">
        <div>
          <h3 style="margin-bottom:12px;color:#555;font-size:1em;">Risk Level Distribution</h3>
          {_embed_chart(pie_chart_b64, "Risk Level Distribution Pie Chart")}
        </div>
        <div>
          <h3 style="margin-bottom:12px;color:#555;font-size:1em;">Risk Score Histogram</h3>
          {_embed_chart(histogram_b64, "Risk Score Histogram")}
        </div>
      </div>
    </div>

    <!-- Top 10 Suspicious Accounts (Requirement 16.3) -->
    <div class="section">
      <h2>🚨 Top 10 Suspicious Accounts</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Account ID</th>
            <th>Risk Level</th>
            <th>Score</th>
            <th>Risk Factors</th>
            <th>Explanation</th>
          </tr>
        </thead>
        <tbody>
          {table_rows if table_rows else '<tr><td colspan="6" style="text-align:center;color:#999;">No accounts to display</td></tr>'}
        </tbody>
      </table>
    </div>

  </div>

  <div class="footer">
    <p>Crypto Suspicious Account Detection System &nbsp;|&nbsp; Powered by AWS Bedrock &amp; Lambda</p>
    <p style="margin-top:4px;">Report ID: {uuid.uuid4()}</p>
  </div>
</body>
</html>"""

    return html


# ---------------------------------------------------------------------------
# Task 8.4 – Lambda handler
# Requirements: 8.1–8.9, 9.4, 13.6, 16.5
# ---------------------------------------------------------------------------

def _read_assessments_from_s3(aws_clients, s3_uri: str) -> List[Dict[str, Any]]:
    """Read risk assessments JSON from S3."""
    bucket, key = _parse_s3_uri(s3_uri)
    logger.info(f"Reading risk assessments from s3://{bucket}/{key}")
    response = aws_clients.s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response["Body"].read().decode("utf-8"))


def _read_assessments_from_dynamodb(aws_clients, table_name: str) -> List[Dict[str, Any]]:
    """Scan DynamoDB table for all risk assessments."""
    table = aws_clients.dynamodb.Table(table_name)
    items: List[Dict[str, Any]] = []
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return items


def lambda_handler(event, context):
    """
    Report Generator Lambda handler.

    Reads risk assessments from S3 (and optionally DynamoDB), generates
    summary statistics, charts, and an HTML presentation, stores all outputs
    to S3, and returns a pre-signed URL valid for 24 hours.

    Requirements: 8.1–8.9, 9.4, 13.6, 16.5

    Args:
        event: Lambda event containing:
            - s3_uri (str): S3 URI of risk assessments JSON
            - total_transactions (int, optional): total transactions processed
        context: Lambda context

    Returns:
        dict: statusCode + body with report_s3_uri and presigned_url
    """
    start_execution = datetime.now()
    logger.info(f"Report Generator Lambda invoked at {start_execution.isoformat()}")
    logger.info(f"Event: {json.dumps(event, default=str)}")

    try:
        # Resolve s3_uri from event
        s3_uri = event.get("s3_uri")
        if not s3_uri:
            body = event.get("body", {})
            if isinstance(body, str):
                body = json.loads(body)
            s3_uri = body.get("s3_uri")
        if not s3_uri:
            raise ValueError("s3_uri not found in event")

        total_transactions: int = int(event.get("total_transactions", 0))

        aws_clients = get_aws_clients()
        report_bucket = os.environ.get("REPORTS_BUCKET", "crypto-detection-reports")
        timestamp = start_execution.strftime("%Y%m%d_%H%M%S")
        key_prefix = f"reports/{timestamp}/"

        # --- Read risk assessments ---
        raw_assessments = _read_assessments_from_s3(aws_clients, s3_uri)
        logger.info(f"Read {len(raw_assessments)} risk assessments from S3")

        # Optionally enrich from DynamoDB (best-effort)
        table_name = os.environ.get("DYNAMODB_TABLE", "crypto-detection-accounts")
        try:
            ddb_items = _read_assessments_from_dynamodb(aws_clients, table_name)
            logger.info(f"Read {len(ddb_items)} items from DynamoDB")
        except Exception as ddb_err:
            logger.warning(f"Could not read from DynamoDB (non-fatal): {ddb_err}")

        # Parse into RiskAssessment objects
        assessments: List[RiskAssessment] = []
        for raw in raw_assessments:
            parsed = _dict_to_risk_assessment(raw)
            if parsed:
                assessments.append(parsed)
        logger.info(f"Successfully parsed {len(assessments)} risk assessments")

        # --- Task 8.1: Summary statistics ---
        summary = generate_summary_report(assessments, total_transactions)

        # Store summary.json (Requirement 9.4)
        summary_key = f"{key_prefix}summary.json"
        aws_clients.s3.put_object(
            Bucket=report_bucket,
            Key=summary_key,
            Body=json.dumps(summary, default=str, indent=2),
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )
        logger.info(f"Summary stored at s3://{report_bucket}/{summary_key}")

        # Store top_suspicious_accounts.json
        top_key = f"{key_prefix}top_suspicious_accounts.json"
        aws_clients.s3.put_object(
            Bucket=report_bucket,
            Key=top_key,
            Body=json.dumps(summary["top_suspicious_accounts"], default=str, indent=2),
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )

        # --- Task 8.2: Charts ---
        pie_s3_uri, pie_b64 = generate_risk_distribution_chart(
            assessments, aws_clients, report_bucket, key_prefix
        )
        hist_s3_uri, hist_b64 = generate_risk_score_histogram(
            assessments, aws_clients, report_bucket, key_prefix
        )
        chart_uris = [u for u in [pie_s3_uri, hist_s3_uri] if u]

        # --- Task 8.3: HTML presentation ---
        html_content = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=pie_b64,
            histogram_b64=hist_b64,
            created_at=start_execution,
        )

        # Store presentation.html (Requirement 9.4)
        html_key = f"{key_prefix}presentation.html"
        aws_clients.s3.put_object(
            Bucket=report_bucket,
            Key=html_key,
            Body=html_content.encode("utf-8"),
            ContentType="text/html",
            ServerSideEncryption="AES256",
        )
        report_s3_uri = f"s3://{report_bucket}/{html_key}"

        # Requirement 13.6: Log report S3 URI
        logger.info(f"Report S3 URI: {report_s3_uri}")

        # Requirement 16.5: Generate pre-signed URL valid for 24 hours
        presigned_url: Optional[str] = None
        try:
            presigned_url = aws_clients.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": report_bucket, "Key": html_key},
                ExpiresIn=86400,  # 24 hours
            )
            logger.info("Pre-signed URL generated (valid 24 hours)")
        except Exception as url_err:
            logger.warning(f"Failed to generate pre-signed URL: {url_err}")

        # Build AnalysisReport model for validation
        risk_dist_enum = {
            RiskLevel(k): v for k, v in summary["risk_distribution"].items()
        }
        report_id = str(uuid.uuid4())
        analysis_report = AnalysisReport(
            report_id=report_id,
            created_at=start_execution,
            total_accounts=summary["total_accounts"],
            total_transactions=summary["total_transactions"],
            risk_distribution=risk_dist_enum,
            average_risk_score=summary["average_risk_score"],
            top_suspicious_accounts=[a["account_id"] for a in summary["top_suspicious_accounts"]],
            charts=chart_uris,
            summary={"key_prefix": key_prefix, "timestamp": timestamp},
        )

        end_execution = datetime.now()
        duration = (end_execution - start_execution).total_seconds()
        logger.info(f"Report Generator completed in {duration:.2f}s")

        response_body = {
            "report_s3_uri": report_s3_uri,
            "presigned_url": presigned_url,
            "report_id": analysis_report.report_id,
            "total_accounts": analysis_report.total_accounts,
            "total_transactions": analysis_report.total_transactions,
            "average_risk_score": analysis_report.average_risk_score,
            "risk_distribution": summary["risk_distribution"],
            "chart_uris": chart_uris,
            "execution_duration_seconds": duration,
        }

        return {
            "statusCode": 200,
            "body": json.dumps(response_body, default=str),
        }

    except Exception as exc:
        logger.error(f"Unexpected error in Report Generator: {exc}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal error", "message": str(exc)}),
        }
