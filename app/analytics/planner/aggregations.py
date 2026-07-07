from typing import List, Dict
from app.schemas.semantic import SemanticModel
from app.schemas.plan import AggregationPlan


class AggregationPlanner:
    """
    Scans the columns of the SemanticModel to plan required math aggregations
    (mean, distinct count, sum) for downstream query executors.
    """

    @staticmethod
    def plan_aggregations(model: SemanticModel) -> List[AggregationPlan]:
        """
        Plans aggregation operations per column.
        """
        plans: List[AggregationPlan] = []

        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            
            # 1. Base aggregations on semantic type definition in Model
            ops = set(col.allowed_aggregations)

            # If semantic type is UNKNOWN, fall back to heuristics based on expected visualizations/categories
            if sem_type == "UNKNOWN" or not ops:
                cat = col.medical_category.upper()
                grp = col.entity_group.upper()
                
                # Check properties or data types from semantic category fallbacks
                if grp == "UNMAPPED":
                    # Fallback based on column metrics or default options
                    ops = {"count"}
                else:
                    ops = {"count", "mode"}
            
            # Map standard aggregation nomenclature to planner supported operations
            mapped_ops = []
            for op in ops:
                op_lower = op.lower()
                if op_lower in {"mean", "average"}:
                    mapped_ops.append("Average")
                elif op_lower == "median":
                    mapped_ops.append("Median")
                elif op_lower == "min":
                    mapped_ops.append("Minimum")
                elif op_lower == "max":
                    mapped_ops.append("Maximum")
                elif op_lower in {"count", "row_count"}:
                    mapped_ops.append("Count")
                elif op_lower in {"distinct_count", "unique_count"}:
                    mapped_ops.append("Distinct Count")
                elif op_lower == "mode":
                    mapped_ops.append("Distinct Count")  # Distinct counts for categories
                elif op_lower == "sum":
                    mapped_ops.append("Sum")

            # Clean duplicates
            clean_ops = list(set(mapped_ops))
            if not clean_ops:
                clean_ops = ["Count"]

            # Additional aggregations for specific variables
            if sem_type == "ADMISSION_DATE":
                clean_ops.extend(["Moving Average", "Growth Rate", "Running Total"])
            elif sem_type == "OUTCOME":
                clean_ops.append("Percentage")

            plans.append(AggregationPlan(
                column=norm_name,
                operations=clean_ops
            ))

        return plans
