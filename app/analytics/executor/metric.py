from typing import Dict, Any, List
from app.schemas.profile import DatasetProfile
from app.schemas.semantic import SemanticModel
from app.core.logging import logger


class MetricCalculator:
    """
    Consumes the dataset profile and semantic validation models to evaluate
    cleanliness rates, outlier densities, duplicate percentages, and consistency scores.
    """

    @staticmethod
    def calculate_quality_metrics(profile: DatasetProfile, model: SemanticModel) -> Dict[str, float]:
        """
        Calculates quality indicators from cached metadata profile.
        """
        total_cells = profile.rows * profile.columns_count
        missing_pct = 0.0
        completeness = 100.0

        if total_cells > 0:
            missing_pct = (profile.total_missing_values / total_cells) * 100.0
            completeness = 100.0 - missing_pct

        duplicate_pct = 0.0
        if profile.rows > 0:
            duplicate_pct = (profile.duplicate_rows / profile.rows) * 100.0

        # Calculate outlier percentage across outlier quality issues
        outlier_pcts = [
            issue.affected_percentage
            for issue in profile.quality_issues
            if issue.issue_type == "outliers"
        ]
        outlier_pct = sum(outlier_pcts) / len(outlier_pcts) if outlier_pcts else 0.0

        # Consistency score: based on type inconsistencies flagged in profile issues
        type_inconsistent_cells = 0
        for issue in profile.quality_issues:
            # Check if issue relates to mixed datatypes
            if issue.issue_type == "mixed_datatypes":
                type_inconsistent_cells += 1 # general penalty

        consistency = 100.0 - (type_inconsistent_cells * 10.0)
        consistency = max(0.0, min(100.0, consistency))

        # Validity score: based on validation errors/issues flagged in semantic model
        validity = 100.0 - (len(profile.quality_issues) * 5.0)
        validity = max(0.0, min(100.0, validity))

        # Overall quality score
        overall_score = float(profile.dataset_quality_score)

        return {
            "completeness": round(completeness, 2),
            "missing_percentage": round(missing_pct, 2),
            "duplicate_percentage": round(duplicate_pct, 2),
            "outlier_percentage": round(outlier_pct, 2),
            "consistency_score": round(consistency, 2),
            "validity_score": round(validity, 2),
            "overall_quality_score": round(overall_score, 2)
        }
