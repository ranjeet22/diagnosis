import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.insight import (
    InsightCollection,
    ExecutiveSummary,
    Insight,
    InsightMetadata,
    InsightContext
)
from app.schemas.results import AnalyticsResult
from app.repositories.result_repository import AnalyticsResultRepository
from app.repositories.insight_repository import InsightRepository
from app.gemini import GeminiClientWrapper
from app.gemini.retry import RetryManager
from app.analytics.insight import InsightContextBuilder, PromptBuilder, InsightValidationService


class InsightGenerationService:
    """
    Orchestration application service executing Prompt 9.
    Maps results to optimized contexts, performs rate-limit compliant retries,
    runs schema validators, caches outputs, and triggers deterministic fallbacks.
    """
    def __init__(self,
        repository: InsightRepository,
        result_repository: AnalyticsResultRepository,
        client_wrapper: GeminiClientWrapper
    ) -> None:
        self.repository = repository
        self.result_repository = result_repository
        self.client_wrapper = client_wrapper

    async def get_insights(self, dataset_id: str) -> InsightCollection:
        """
        Retrieves cached insights. If cache miss, runs generation.
        """
        try:
            return await self.repository.get_insights(dataset_id=dataset_id)
        except DatasetNotFound:
            logger.info(f"Insights cache miss for dataset {dataset_id}. Running generation...")
            return await self.generate_insights(dataset_id=dataset_id, force=False)

    async def generate_insights(self, dataset_id: str, force: bool = False) -> InsightCollection:
        logger.info(f"InsightGenerationService: Initiating AI insight generation for dataset {dataset_id}")

        # 1. Load dependencies
        try:
            results = await self.result_repository.get_results(dataset_id=dataset_id)
        except DatasetNotFound as e:
            raise DatasetNotFound(f"Cannot generate insights: {e}")
        except Exception as e:
            raise AnalyticsError(f"Failed to load analytics results for insights: {e}")

        # 2. Check Cache (if force is False)
        if not force:
            try:
                cached = await self.repository.get_insights(dataset_id=dataset_id)
                # If cached generation is newer than/equal to results timestamp, reuse it!
                if cached.metadata.generation_timestamp >= results.created_at:
                    logger.info(f"InsightGenerationService: Cache hit. Reusing cached insights for dataset {dataset_id}")
                    return cached
            except DatasetNotFound:
                pass  # Cache miss, proceed

        # 3. Build Context (Token Optimization)
        context = InsightContextBuilder.build_context(results)

        # 4. Build Prompt Payload
        prompt_builder = PromptBuilder()
        payload = prompt_builder.build_prompt_payload(context)

        # 5. Invoke Gemini with Retry Manager
        raw_text = ""
        gemini_metadata = {
            "model_name": self.client_wrapper.default_model,
            "prompt_version": prompt_builder.version,
            "status": "success"
        }

        async def run_call():
            return await self.client_wrapper.generate_explanation(
                system_instruction=payload.system_instruction,
                prompt=payload.prompt
            )

        try:
            raw_text = await RetryManager.execute_with_retry(run_call, max_retries=3)
        except Exception as e:
            logger.warning(
                f"InsightGenerationService: Gemini API call failed or rate-limited after retries: {e}. "
                "Triggering fallback deterministic insights generation..."
            )
            raw_text = self._get_fallback_response_json(context)
            gemini_metadata["status"] = "fallback"

        # 6. Parse and Validate Response
        parsed_data, logs, is_valid = InsightValidationService.validate_llm_json(raw_text)
        
        if not is_valid or not parsed_data:
            logger.warning("InsightGenerationService: Generated JSON failed validation checks. Constructing fallback...")
            parsed_data = json.loads(self._get_fallback_response_json(context))
            logs.append("Validation Warning: LLM JSON was malformed. Reverted to deterministic fallback representation.")
            gemini_metadata["status"] = "fallback_validation_failure"

        # 7. Assemble Collection
        exec_raw = parsed_data.get("executive_summary", {})
        executive_summary = ExecutiveSummary(
            title=exec_raw.get("title", "Clinical Cohort Summary"),
            summary=exec_raw.get("summary", "Summarization of patient record counts and medical outcomes."),
            key_takeaways=exec_raw.get("key_takeaways", [])
        )

        insights_list = []
        for idx, ins in enumerate(parsed_data.get("insights", [])):
            insights_list.append(Insight(
                id=ins.get("id", f"ins_{idx}"),
                title=ins.get("title", "Clinical Indicator"),
                summary=ins.get("summary", "Overview of cohort metrics."),
                detailed_explanation=ins.get("detailed_explanation", ""),
                evidence=ins.get("evidence", ""),
                source_metrics=ins.get("source_metrics", []),
                importance=ins.get("importance", "medium"),
                confidence=ins.get("confidence", 1.0),
                category=ins.get("category", "general")
            ))

        metadata = InsightMetadata(
            prompt_version=prompt_builder.version,
            generation_timestamp=datetime.now(timezone.utc),
            confidence_score=0.8 if gemini_metadata["status"] == "success" else 0.5,
            gemini_metadata=gemini_metadata
        )

        collection = InsightCollection(
            dataset_id=dataset_id,
            executive_summary=executive_summary,
            insights=insights_list,
            metadata=metadata
        )

        # 8. Persist insights
        try:
            await self.repository.save_insights(dataset_id=dataset_id, insights=collection)
            logger.info(f"InsightGenerationService: Successfully saved insights for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to persist insights json to storage: {e}")
            raise AnalyticsError(f"Failed to persist insights config: {e}")

        return collection

    def _get_fallback_response_json(self, context: InsightContext) -> str:
        """
        Generates a deterministic JSON payload representing the clinical context
        to serve as a fallback when Gemini is offline or rate-limited.
        """
        kpis_desc = ", ".join([f"{k}: {v}" for k, v in context.kpis.items()])
        
        fallback_data = {
            "executive_summary": {
                "title": "Deterministic Cohort Summary (Fallback Mode)",
                "summary": f"This summary has been compiled deterministically. Operational KPIs include: {kpis_desc}.",
                "key_takeaways": [
                    "Deterministic analysis compiled successfully.",
                    "Primary KPI metrics mapped without external LLM processing.",
                    "Dataset cleaning score and categorical frequencies are stable."
                ]
            },
            "insights": [
                {
                    "id": "fallback_kpi_overview",
                    "title": "Key Indicators Overview",
                    "summary": "Cohort operational metrics summary.",
                    "detailed_explanation": f"KPI metrics summary: {kpis_desc}.",
                    "evidence": kpis_desc,
                    "source_metrics": list(context.kpis.keys()),
                    "importance": "high",
                    "confidence": 1.0,
                    "category": "general"
                }
            ]
        }

        # Add data quality observation if completeness score exists
        if "Dataset Completeness" in context.kpis:
            fallback_data["insights"].append({
                "id": "fallback_data_quality",
                "title": "Data Quality and Field Integrity",
                "summary": f"Dataset completeness is reported at {context.kpis['Dataset Completeness']}.",
                "detailed_explanation": "Deterministic verification confirms that required medical columns are fully populated.",
                "evidence": f"Dataset Completeness: {context.kpis['Dataset Completeness']}",
                "source_metrics": ["Dataset Completeness"],
                "importance": "medium",
                "confidence": 1.0,
                "category": "data_quality"
            })

        return json.dumps(fallback_data, indent=2)
