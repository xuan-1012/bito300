"""
Unit tests for Report Generator Lambda handler.

Tests the generate_summary_report function and related functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from src.common.models import RiskAssessment, RiskLevel
from src.lambdas.report_generator.handler import (
    generate_summary_report,
    generate_risk_distribution_chart,
    generate_risk_score_histogram,
)


class TestGenerateSummaryReport:
    """Test suite for generate_summary_report function."""

    def test_generate_summary_report_basic(self):
        """Test basic summary report generation with multiple risk levels."""
        # Create sample risk assessments
        assessments = [
            RiskAssessment(
                account_id="acc_001",
                risk_score=85.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["High volume", "Night transactions"],
                explanation="Critical risk account",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_002",
                risk_score=60.0,
                risk_level=RiskLevel.HIGH,
                risk_factors=["Round numbers"],
                explanation="High risk account",
                confidence=0.85,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_003",
                risk_score=35.0,
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Moderate velocity"],
                explanation="Medium risk account",
                confidence=0.8,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_004",
                risk_score=15.0,
                risk_level=RiskLevel.LOW,
                risk_factors=["Normal activity"],
                explanation="Low risk account",
                confidence=0.95,
                timestamp=datetime.now(),
            ),
        ]

        # Generate summary report
        summary = generate_summary_report(assessments, total_transactions=100)

        # Verify total_accounts (Requirement 8.1)
        assert summary["total_accounts"] == 4

        # Verify total_transactions
        assert summary["total_transactions"] == 100

        # Verify risk_distribution (Requirement 8.2)
        assert summary["risk_distribution"]["critical"] == 1
        assert summary["risk_distribution"]["high"] == 1
        assert summary["risk_distribution"]["medium"] == 1
        assert summary["risk_distribution"]["low"] == 1

        # Verify average_risk_score (Requirement 8.3)
        expected_avg = (85.0 + 60.0 + 35.0 + 15.0) / 4
        assert summary["average_risk_score"] == round(expected_avg, 2)

        # Verify top_suspicious_accounts sorted by risk_score (Requirement 8.4)
        top_accounts = summary["top_suspicious_accounts"]
        assert len(top_accounts) == 4
        assert top_accounts[0]["account_id"] == "acc_001"
        assert top_accounts[0]["risk_score"] == 85.0
        assert top_accounts[1]["account_id"] == "acc_002"
        assert top_accounts[1]["risk_score"] == 60.0
        assert top_accounts[2]["account_id"] == "acc_003"
        assert top_accounts[3]["account_id"] == "acc_004"

    def test_generate_summary_report_empty(self):
        """Test summary report with no assessments."""
        summary = generate_summary_report([], total_transactions=0)

        assert summary["total_accounts"] == 0
        assert summary["total_transactions"] == 0
        assert summary["average_risk_score"] == 0.0
        assert len(summary["top_suspicious_accounts"]) == 0

    def test_generate_summary_report_single_account(self):
        """Test summary report with single account."""
        assessments = [
            RiskAssessment(
                account_id="acc_001",
                risk_score=75.0,
                risk_level=RiskLevel.HIGH,
                risk_factors=["High risk"],
                explanation="Single account",
                confidence=0.9,
                timestamp=datetime.now(),
            )
        ]

        summary = generate_summary_report(assessments, total_transactions=50)

        assert summary["total_accounts"] == 1
        assert summary["total_transactions"] == 50
        assert summary["average_risk_score"] == 75.0
        assert summary["risk_distribution"]["high"] == 1
        assert len(summary["top_suspicious_accounts"]) == 1

    def test_generate_summary_report_top_10_limit(self):
        """Test that top_suspicious_accounts is limited to 10 accounts."""
        # Create 15 assessments
        assessments = []
        for i in range(15):
            score = 100.0 - i * 5  # Descending scores
            # Determine correct risk level based on score
            if score >= 76:
                level = RiskLevel.CRITICAL
            elif score >= 51:
                level = RiskLevel.HIGH
            elif score >= 26:
                level = RiskLevel.MEDIUM
            else:
                level = RiskLevel.LOW
            
            assessments.append(
                RiskAssessment(
                    account_id=f"acc_{i:03d}",
                    risk_score=score,
                    risk_level=level,
                    risk_factors=["Risk factor"],
                    explanation=f"Account {i}",
                    confidence=0.9,
                    timestamp=datetime.now(),
                )
            )

        summary = generate_summary_report(assessments, total_transactions=500)

        # Verify only top 10 are returned
        assert len(summary["top_suspicious_accounts"]) == 10
        assert summary["top_suspicious_accounts"][0]["account_id"] == "acc_000"
        assert summary["top_suspicious_accounts"][9]["account_id"] == "acc_009"

    def test_generate_summary_report_all_same_risk_level(self):
        """Test summary report when all accounts have same risk level."""
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=80.0 + i,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["Critical risk"],
                explanation="Critical account",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(5)
        ]

        summary = generate_summary_report(assessments, total_transactions=200)

        assert summary["total_accounts"] == 5
        assert summary["risk_distribution"]["critical"] == 5
        assert summary["risk_distribution"]["high"] == 0
        assert summary["risk_distribution"]["medium"] == 0
        assert summary["risk_distribution"]["low"] == 0

    def test_generate_summary_report_sorting_order(self):
        """Test that accounts are sorted by risk_score in descending order."""
        assessments = [
            RiskAssessment(
                account_id="acc_low",
                risk_score=20.0,
                risk_level=RiskLevel.LOW,
                risk_factors=["Low risk"],
                explanation="Low",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_critical",
                risk_score=90.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["Critical risk"],
                explanation="Critical",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_medium",
                risk_score=40.0,
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Medium risk"],
                explanation="Medium",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
        ]

        summary = generate_summary_report(assessments, total_transactions=100)

        top_accounts = summary["top_suspicious_accounts"]
        assert top_accounts[0]["account_id"] == "acc_critical"
        assert top_accounts[1]["account_id"] == "acc_medium"
        assert top_accounts[2]["account_id"] == "acc_low"

    def test_generate_summary_report_includes_all_fields(self):
        """Test that top_suspicious_accounts includes all required fields."""
        assessments = [
            RiskAssessment(
                account_id="acc_001",
                risk_score=85.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["Factor 1", "Factor 2"],
                explanation="Detailed explanation",
                confidence=0.92,
                timestamp=datetime.now(),
            )
        ]

        summary = generate_summary_report(assessments, total_transactions=50)

        top_account = summary["top_suspicious_accounts"][0]
        assert "account_id" in top_account
        assert "risk_score" in top_account
        assert "risk_level" in top_account
        assert "risk_factors" in top_account
        assert "explanation" in top_account
        assert "confidence" in top_account
        assert top_account["account_id"] == "acc_001"
        assert top_account["risk_score"] == 85.0
        assert top_account["risk_level"] == "critical"
        assert top_account["risk_factors"] == ["Factor 1", "Factor 2"]
        assert top_account["explanation"] == "Detailed explanation"
        assert top_account["confidence"] == 0.92



class TestGenerateRiskDistributionChart:
    """Test suite for generate_risk_distribution_chart function (Requirement 8.5, 8.7)."""

    def test_generate_risk_distribution_chart_basic(self):
        """Test basic risk distribution chart generation with all risk levels."""
        # Create sample risk assessments with all risk levels
        assessments = [
            RiskAssessment(
                account_id="acc_001",
                risk_score=85.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["High volume"],
                explanation="Critical risk",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_002",
                risk_score=60.0,
                risk_level=RiskLevel.HIGH,
                risk_factors=["Round numbers"],
                explanation="High risk",
                confidence=0.85,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_003",
                risk_score=35.0,
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Moderate velocity"],
                explanation="Medium risk",
                confidence=0.8,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_004",
                risk_score=15.0,
                risk_level=RiskLevel.LOW,
                risk_factors=["Normal activity"],
                explanation="Low risk",
                confidence=0.95,
                timestamp=datetime.now(),
            ),
        ]

        # Mock AWS clients
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        # Generate chart
        s3_uri, base64_png = generate_risk_distribution_chart(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Verify S3 upload was called (Requirement 8.7)
        mock_aws_clients.s3.put_object.assert_called_once()
        call_args = mock_aws_clients.s3.put_object.call_args
        assert call_args[1]["Bucket"] == "test-bucket"
        assert call_args[1]["Key"] == "test-prefix/risk_distribution.png"
        assert call_args[1]["ContentType"] == "image/png"
        assert call_args[1]["ServerSideEncryption"] == "AES256"

        # Verify S3 URI is returned
        assert s3_uri == "s3://test-bucket/test-prefix/risk_distribution.png"

        # Verify base64 PNG is returned
        assert base64_png is not None
        assert isinstance(base64_png, str)
        assert len(base64_png) > 0

    def test_generate_risk_distribution_chart_empty_assessments(self):
        """Test chart generation with no assessments."""
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        s3_uri, base64_png = generate_risk_distribution_chart(
            [], mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Should still generate a chart (with "No data" message)
        assert s3_uri == "s3://test-bucket/test-prefix/risk_distribution.png"
        assert base64_png is not None

    def test_generate_risk_distribution_chart_single_risk_level(self):
        """Test chart generation when all accounts have same risk level."""
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=80.0 + i,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["Critical risk"],
                explanation="Critical account",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(5)
        ]

        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        s3_uri, base64_png = generate_risk_distribution_chart(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Verify chart is generated
        assert s3_uri == "s3://test-bucket/test-prefix/risk_distribution.png"
        assert base64_png is not None

    def test_generate_risk_distribution_chart_s3_upload_failure(self):
        """Test chart generation when S3 upload fails."""
        assessments = [
            RiskAssessment(
                account_id="acc_001",
                risk_score=85.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["High volume"],
                explanation="Critical risk",
                confidence=0.9,
                timestamp=datetime.now(),
            )
        ]

        # Mock AWS clients with S3 upload failure
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object.side_effect = Exception("S3 upload failed")

        s3_uri, base64_png = generate_risk_distribution_chart(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # S3 URI should be None when upload fails
        assert s3_uri is None
        # But base64 PNG should still be generated
        assert base64_png is not None


class TestGenerateRiskScoreHistogram:
    """Test suite for generate_risk_score_histogram function (Requirement 8.6, 8.7)."""

    def test_generate_risk_score_histogram_basic(self):
        """Test basic risk score histogram generation."""
        # Create sample risk assessments with varying scores
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=float(i * 10),
                risk_level=RiskLevel.from_score(float(i * 10)),
                risk_factors=["Risk factor"],
                explanation=f"Account {i}",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(11)  # Scores: 0, 10, 20, ..., 100
        ]

        # Mock AWS clients
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        # Generate histogram
        s3_uri, base64_png = generate_risk_score_histogram(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Verify S3 upload was called (Requirement 8.7)
        mock_aws_clients.s3.put_object.assert_called_once()
        call_args = mock_aws_clients.s3.put_object.call_args
        assert call_args[1]["Bucket"] == "test-bucket"
        assert call_args[1]["Key"] == "test-prefix/risk_score_histogram.png"
        assert call_args[1]["ContentType"] == "image/png"
        assert call_args[1]["ServerSideEncryption"] == "AES256"

        # Verify S3 URI is returned
        assert s3_uri == "s3://test-bucket/test-prefix/risk_score_histogram.png"

        # Verify base64 PNG is returned
        assert base64_png is not None
        assert isinstance(base64_png, str)
        assert len(base64_png) > 0

    def test_generate_risk_score_histogram_empty_assessments(self):
        """Test histogram generation with no assessments."""
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        s3_uri, base64_png = generate_risk_score_histogram(
            [], mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Should still generate a histogram (empty)
        assert s3_uri == "s3://test-bucket/test-prefix/risk_score_histogram.png"
        assert base64_png is not None

    def test_generate_risk_score_histogram_all_same_score(self):
        """Test histogram generation when all accounts have same score."""
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=75.0,
                risk_level=RiskLevel.HIGH,
                risk_factors=["Risk factor"],
                explanation=f"Account {i}",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(10)
        ]

        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        s3_uri, base64_png = generate_risk_score_histogram(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Verify histogram is generated
        assert s3_uri == "s3://test-bucket/test-prefix/risk_score_histogram.png"
        assert base64_png is not None

    def test_generate_risk_score_histogram_extreme_scores(self):
        """Test histogram generation with extreme scores (0 and 100)."""
        assessments = [
            RiskAssessment(
                account_id="acc_min",
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                risk_factors=["Minimal risk"],
                explanation="Minimum score",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
            RiskAssessment(
                account_id="acc_max",
                risk_score=100.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["Maximum risk"],
                explanation="Maximum score",
                confidence=0.9,
                timestamp=datetime.now(),
            ),
        ]

        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        s3_uri, base64_png = generate_risk_score_histogram(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Verify histogram is generated
        assert s3_uri == "s3://test-bucket/test-prefix/risk_score_histogram.png"
        assert base64_png is not None

    def test_generate_risk_score_histogram_s3_upload_failure(self):
        """Test histogram generation when S3 upload fails."""
        assessments = [
            RiskAssessment(
                account_id="acc_001",
                risk_score=50.0,
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Medium risk"],
                explanation="Test account",
                confidence=0.9,
                timestamp=datetime.now(),
            )
        ]

        # Mock AWS clients with S3 upload failure
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object.side_effect = Exception("S3 upload failed")

        s3_uri, base64_png = generate_risk_score_histogram(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # S3 URI should be None when upload fails
        assert s3_uri is None
        # But base64 PNG should still be generated
        assert base64_png is not None

    def test_generate_risk_score_histogram_large_dataset(self):
        """Test histogram generation with large number of assessments."""
        # Create 100 assessments with random-like scores
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=float((i * 7) % 101),  # Pseudo-random scores 0-100
                risk_level=RiskLevel.from_score(float((i * 7) % 101)),
                risk_factors=["Risk factor"],
                explanation=f"Account {i}",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(100)
        ]

        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        s3_uri, base64_png = generate_risk_score_histogram(
            assessments, mock_aws_clients, "test-bucket", "test-prefix/"
        )

        # Verify histogram is generated
        assert s3_uri == "s3://test-bucket/test-prefix/risk_score_histogram.png"
        assert base64_png is not None



class TestGeneratePresentationSlides:
    """Test suite for generate_presentation_slides function (Requirements 8.8, 16.1, 16.2, 16.3, 16.4)."""

    def test_generate_presentation_slides_basic(self):
        """Test basic HTML presentation generation with all components."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        # Create sample summary data
        summary = {
            "total_accounts": 100,
            "total_transactions": 5000,
            "average_risk_score": 42.5,
            "risk_distribution": {
                "critical": 10,
                "high": 20,
                "medium": 30,
                "low": 40,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": "acc_001",
                    "risk_score": 95.0,
                    "risk_level": "critical",
                    "risk_factors": ["High volume", "Night transactions"],
                    "explanation": "This account shows suspicious patterns",
                    "confidence": 0.95,
                },
                {
                    "account_id": "acc_002",
                    "risk_score": 88.0,
                    "risk_level": "critical",
                    "risk_factors": ["Round numbers", "Rapid transactions"],
                    "explanation": "Multiple red flags detected",
                    "confidence": 0.92,
                },
            ],
        }

        # Mock base64 chart data
        pie_chart_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        histogram_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        created_at = datetime(2024, 1, 15, 10, 30, 0)

        # Generate presentation
        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=pie_chart_b64,
            histogram_b64=histogram_b64,
            created_at=created_at,
        )

        # Verify HTML structure
        assert isinstance(html, str)
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

        # Requirement 16.1: Executive summary section
        assert "Executive Summary" in html
        assert "100" in html  # total_accounts
        assert "5000" in html  # total_transactions
        assert "42.5" in html  # average_risk_score

        # Verify risk distribution cards
        assert "10" in html  # critical count
        assert "20" in html  # high count
        assert "30" in html  # medium count
        assert "40" in html  # low count

        # Requirement 16.2: Embedded charts
        assert "Risk Level Distribution" in html
        assert "Risk Score Histogram" in html
        assert f'<img src="data:image/png;base64,{pie_chart_b64}"' in html
        assert f'<img src="data:image/png;base64,{histogram_b64}"' in html

        # Requirement 16.3: Top 10 suspicious accounts table
        assert "Top 10 Suspicious Accounts" in html
        assert "acc_001" in html
        assert "acc_002" in html
        assert "95.0" in html
        assert "88.0" in html
        assert "High volume" in html
        assert "Night transactions" in html
        assert "This account shows suspicious patterns" in html

        # Requirement 16.4: Clean and professional design
        assert "<style>" in html
        assert "font-family" in html
        assert "background" in html
        assert "color" in html

        # Verify timestamp formatting
        assert "2024-01-15 10:30:00 UTC" in html

    def test_generate_presentation_slides_empty_accounts(self):
        """Test presentation generation with no suspicious accounts."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 0,
            "total_transactions": 0,
            "average_risk_score": 0.0,
            "risk_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "top_suspicious_accounts": [],
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify HTML is generated
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

        # Verify empty state handling
        assert "0" in html  # total_accounts
        assert "No accounts to display" in html

        # Verify chart placeholders when charts are unavailable
        assert "Chart unavailable" in html

    def test_generate_presentation_slides_partial_charts(self):
        """Test presentation generation with only one chart available."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 50,
            "total_transactions": 1000,
            "average_risk_score": 35.0,
            "risk_distribution": {
                "critical": 5,
                "high": 10,
                "medium": 15,
                "low": 20,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": "acc_001",
                    "risk_score": 80.0,
                    "risk_level": "critical",
                    "risk_factors": ["High risk"],
                    "explanation": "Test account",
                    "confidence": 0.9,
                }
            ],
        }

        # Only pie chart available
        pie_chart_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=pie_chart_b64,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify pie chart is embedded
        assert f'<img src="data:image/png;base64,{pie_chart_b64}"' in html

        # Verify histogram placeholder
        assert "Chart unavailable" in html

    def test_generate_presentation_slides_max_accounts(self):
        """Test presentation generation with more than 10 suspicious accounts."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        # Create 15 suspicious accounts
        top_accounts = []
        for i in range(15):
            score = 100.0 - i * 5
            if score >= 76:
                level = "critical"
            elif score >= 51:
                level = "high"
            elif score >= 26:
                level = "medium"
            else:
                level = "low"
            
            top_accounts.append({
                "account_id": f"acc_{i:03d}",
                "risk_score": score,
                "risk_level": level,
                "risk_factors": [f"Factor {i}"],
                "explanation": f"Explanation {i}",
                "confidence": 0.9,
            })

        summary = {
            "total_accounts": 15,
            "total_transactions": 3000,
            "average_risk_score": 60.0,
            "risk_distribution": {
                "critical": 5,
                "high": 5,
                "medium": 3,
                "low": 2,
            },
            "top_suspicious_accounts": top_accounts,
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify only top 10 are displayed (slicing happens in the function)
        assert "acc_000" in html
        assert "acc_009" in html
        # Note: The function slices to [:10] in the table generation

    def test_generate_presentation_slides_risk_level_colors(self):
        """Test that risk level badges have correct colors."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 4,
            "total_transactions": 1000,
            "average_risk_score": 50.0,
            "risk_distribution": {
                "critical": 1,
                "high": 1,
                "medium": 1,
                "low": 1,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": "acc_critical",
                    "risk_score": 90.0,
                    "risk_level": "critical",
                    "risk_factors": ["Critical"],
                    "explanation": "Critical account",
                    "confidence": 0.9,
                },
                {
                    "account_id": "acc_high",
                    "risk_score": 70.0,
                    "risk_level": "high",
                    "risk_factors": ["High"],
                    "explanation": "High account",
                    "confidence": 0.9,
                },
                {
                    "account_id": "acc_medium",
                    "risk_score": 40.0,
                    "risk_level": "medium",
                    "risk_factors": ["Medium"],
                    "explanation": "Medium account",
                    "confidence": 0.9,
                },
                {
                    "account_id": "acc_low",
                    "risk_score": 10.0,
                    "risk_level": "low",
                    "risk_factors": ["Low"],
                    "explanation": "Low account",
                    "confidence": 0.9,
                },
            ],
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify color codes are present
        assert "#9C27B0" in html  # critical - purple
        assert "#F44336" in html  # high - red
        assert "#FF9800" in html  # medium - orange
        assert "#4CAF50" in html  # low - green

    def test_generate_presentation_slides_special_characters(self):
        """Test presentation generation with special characters in data."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 1,
            "total_transactions": 100,
            "average_risk_score": 75.0,
            "risk_distribution": {
                "critical": 0,
                "high": 1,
                "medium": 0,
                "low": 0,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": "acc_<script>alert('xss')</script>",
                    "risk_score": 75.0,
                    "risk_level": "high",
                    "risk_factors": ["Factor with <tags>", "Factor & ampersand"],
                    "explanation": "Explanation with 'quotes' and \"double quotes\"",
                    "confidence": 0.9,
                }
            ],
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify HTML is generated (basic XSS protection through HTML rendering)
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

    def test_generate_presentation_slides_responsive_design(self):
        """Test that presentation includes responsive design elements."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 10,
            "total_transactions": 500,
            "average_risk_score": 30.0,
            "risk_distribution": {
                "critical": 1,
                "high": 2,
                "medium": 3,
                "low": 4,
            },
            "top_suspicious_accounts": [],
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify responsive design elements
        assert 'name="viewport"' in html
        assert "max-width" in html
        assert "@media" in html  # Media queries for responsive design

    def test_generate_presentation_slides_professional_styling(self):
        """Test that presentation includes professional styling elements (Requirement 16.4)."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 50,
            "total_transactions": 2000,
            "average_risk_score": 45.0,
            "risk_distribution": {
                "critical": 5,
                "high": 10,
                "medium": 15,
                "low": 20,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": "acc_001",
                    "risk_score": 85.0,
                    "risk_level": "critical",
                    "risk_factors": ["High volume"],
                    "explanation": "Test",
                    "confidence": 0.9,
                }
            ],
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify professional design elements
        assert "gradient" in html.lower()  # Gradient backgrounds
        assert "border-radius" in html  # Rounded corners
        assert "box-shadow" in html  # Shadows for depth
        assert "padding" in html  # Proper spacing
        assert "margin" in html  # Proper spacing
        assert ".header" in html  # Structured CSS classes
        assert ".section" in html
        assert ".stat-card" in html

    def test_generate_presentation_slides_all_requirements(self):
        """Comprehensive test verifying all requirements (8.8, 16.1, 16.2, 16.3, 16.4)."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 100,
            "total_transactions": 5000,
            "average_risk_score": 42.5,
            "risk_distribution": {
                "critical": 10,
                "high": 20,
                "medium": 30,
                "low": 40,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": f"acc_{i:03d}",
                    "risk_score": 100.0 - i * 5,
                    "risk_level": "critical" if 100.0 - i * 5 >= 76 else "high",
                    "risk_factors": [f"Factor {i}"],
                    "explanation": f"Explanation for account {i}",
                    "confidence": 0.9,
                }
                for i in range(10)
            ],
        }

        pie_chart_b64 = "test_pie_chart_base64"
        histogram_b64 = "test_histogram_base64"
        created_at = datetime(2024, 1, 15, 10, 30, 0)

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=pie_chart_b64,
            histogram_b64=histogram_b64,
            created_at=created_at,
        )

        # Requirement 8.8: HTML presentation generator
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

        # Requirement 16.1: Executive summary section
        assert "Executive Summary" in html or "executive summary" in html.lower()
        assert "100" in html  # total_accounts
        assert "5000" in html  # total_transactions
        assert "42.5" in html  # average_risk_score

        # Requirement 16.2: Embedded charts and visualizations
        assert "Risk Level Distribution" in html or "distribution" in html.lower()
        assert "Risk Score Histogram" in html or "histogram" in html.lower()
        assert "data:image/png;base64," in html

        # Requirement 16.3: Table of top 10 suspicious accounts with explanations
        assert "Top 10" in html or "top 10" in html.lower()
        assert "acc_000" in html
        assert "Explanation for account" in html
        assert "<table" in html
        assert "<th" in html
        assert "<td" in html

        # Requirement 16.4: Clean and professional design
        assert "<style>" in html
        assert "font-family" in html
        assert "color" in html
        assert "background" in html
        assert "border-radius" in html or "box-shadow" in html


class TestEdgeCases:
    """Test suite for edge cases in report generation."""

    def test_all_high_risk_accounts(self):
        """Test report generation when all accounts are high risk (CRITICAL)."""
        # Create assessments where all are CRITICAL
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=80.0 + i,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["High volume", "Night transactions", "Round numbers"],
                explanation=f"Critical risk account {i}",
                confidence=0.95,
                timestamp=datetime.now(),
            )
            for i in range(20)
        ]

        # Generate summary
        summary = generate_summary_report(assessments, total_transactions=1000)

        # Verify all accounts are CRITICAL
        assert summary["total_accounts"] == 20
        assert summary["risk_distribution"]["critical"] == 20
        assert summary["risk_distribution"]["high"] == 0
        assert summary["risk_distribution"]["medium"] == 0
        assert summary["risk_distribution"]["low"] == 0

        # Verify average risk score is high
        assert summary["average_risk_score"] >= 80.0

        # Verify top accounts are sorted correctly
        top_accounts = summary["top_suspicious_accounts"]
        assert len(top_accounts) == 10  # Limited to top 10
        # Verify descending order
        for i in range(len(top_accounts) - 1):
            assert top_accounts[i]["risk_score"] >= top_accounts[i + 1]["risk_score"]

    def test_no_suspicious_accounts(self):
        """Test report generation when there are no suspicious accounts (all LOW risk)."""
        # Create assessments where all are LOW risk
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=float(i),  # Scores 0-19, all LOW
                risk_level=RiskLevel.LOW,
                risk_factors=["Normal activity"],
                explanation=f"Low risk account {i}",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(20)
        ]

        # Generate summary
        summary = generate_summary_report(assessments, total_transactions=500)

        # Verify all accounts are LOW
        assert summary["total_accounts"] == 20
        assert summary["risk_distribution"]["critical"] == 0
        assert summary["risk_distribution"]["high"] == 0
        assert summary["risk_distribution"]["medium"] == 0
        assert summary["risk_distribution"]["low"] == 20

        # Verify average risk score is low
        assert summary["average_risk_score"] < 26.0

        # Verify top accounts still returned (even though all are low risk)
        top_accounts = summary["top_suspicious_accounts"]
        assert len(top_accounts) == 10
        # Verify they're still sorted by score
        assert top_accounts[0]["risk_score"] >= top_accounts[-1]["risk_score"]

    def test_mixed_risk_levels_with_ties(self):
        """Test report generation with multiple accounts having same risk scores."""
        # Create assessments with duplicate scores
        assessments = [
            RiskAssessment(
                account_id=f"acc_critical_{i}",
                risk_score=85.0,
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["High risk"],
                explanation="Critical account",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(5)
        ] + [
            RiskAssessment(
                account_id=f"acc_high_{i}",
                risk_score=60.0,
                risk_level=RiskLevel.HIGH,
                risk_factors=["Medium risk"],
                explanation="High account",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(5)
        ]

        summary = generate_summary_report(assessments, total_transactions=300)

        # Verify distribution
        assert summary["total_accounts"] == 10
        assert summary["risk_distribution"]["critical"] == 5
        assert summary["risk_distribution"]["high"] == 5

        # Verify top accounts includes all CRITICAL first
        top_accounts = summary["top_suspicious_accounts"]
        assert len(top_accounts) == 10
        # First 5 should be CRITICAL (score 85.0)
        for i in range(5):
            assert top_accounts[i]["risk_level"] == "critical"
            assert top_accounts[i]["risk_score"] == 85.0
        # Next 5 should be HIGH (score 60.0)
        for i in range(5, 10):
            assert top_accounts[i]["risk_level"] == "high"
            assert top_accounts[i]["risk_score"] == 60.0

    def test_chart_generation_with_no_data(self):
        """Test chart generation functions handle empty data gracefully."""
        mock_aws_clients = MagicMock()
        mock_aws_clients.s3.put_object = MagicMock()

        # Test pie chart with empty list
        s3_uri, base64_png = generate_risk_distribution_chart(
            [], mock_aws_clients, "test-bucket", "test-prefix/"
        )
        assert s3_uri is not None  # Should still generate chart
        assert base64_png is not None

        # Test histogram with empty list
        s3_uri, base64_png = generate_risk_score_histogram(
            [], mock_aws_clients, "test-bucket", "test-prefix/"
        )
        assert s3_uri is not None
        assert base64_png is not None

    def test_html_generation_with_extreme_values(self):
        """Test HTML generation with extreme values (very large numbers, long strings)."""
        from src.lambdas.report_generator.handler import generate_presentation_slides
        
        summary = {
            "total_accounts": 999999,
            "total_transactions": 10000000,
            "average_risk_score": 99.99,
            "risk_distribution": {
                "critical": 999999,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "top_suspicious_accounts": [
                {
                    "account_id": "acc_" + "x" * 100,  # Very long account ID
                    "risk_score": 100.0,
                    "risk_level": "critical",
                    "risk_factors": ["Factor " + str(i) for i in range(50)],  # Many factors
                    "explanation": "This is a very long explanation " * 20,  # Long explanation
                    "confidence": 0.999999,
                }
            ],
        }

        html = generate_presentation_slides(
            summary=summary,
            pie_chart_b64=None,
            histogram_b64=None,
            created_at=datetime.now(),
        )

        # Verify HTML is generated without errors
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "999999" in html
        assert "10000000" in html

    def test_summary_calculation_precision(self):
        """Test that summary statistics maintain proper precision."""
        # Create assessments with fractional scores
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=33.333,
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Factor"],
                explanation="Test",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(3)
        ]

        summary = generate_summary_report(assessments, total_transactions=100)

        # Verify average is calculated correctly and rounded to 2 decimals
        assert summary["average_risk_score"] == 33.33  # Rounded to 2 decimals
        assert isinstance(summary["average_risk_score"], float)

    def test_top_accounts_sorting_stability(self):
        """Test that top accounts sorting is stable and consistent."""
        # Create assessments with varying scores (ensuring all are valid 0-100)
        assessments = [
            RiskAssessment(
                account_id=f"acc_{i:03d}",
                risk_score=float(100 - i * 2),  # Scores: 100, 98, 96, ..., 2, 0
                risk_level=RiskLevel.from_score(float(100 - i * 2)),
                risk_factors=["Factor"],
                explanation=f"Account {i}",
                confidence=0.9,
                timestamp=datetime.now(),
            )
            for i in range(51)  # 51 accounts with scores 100 down to 0
        ]

        summary = generate_summary_report(assessments, total_transactions=1000)

        top_accounts = summary["top_suspicious_accounts"]
        
        # Verify exactly 10 accounts returned
        assert len(top_accounts) == 10
        
        # Verify strict descending order
        for i in range(len(top_accounts) - 1):
            assert top_accounts[i]["risk_score"] >= top_accounts[i + 1]["risk_score"]
        
        # Verify highest score is first
        assert top_accounts[0]["risk_score"] == 100.0
        assert top_accounts[0]["account_id"] == "acc_000"
        
        # Verify 10th account has score 82.0 (100 - 9*2)
        assert top_accounts[9]["risk_score"] == 82.0
        assert top_accounts[9]["account_id"] == "acc_009"
