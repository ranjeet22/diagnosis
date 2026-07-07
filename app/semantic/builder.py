from datetime import datetime, timezone
from typing import Dict, List, Any
from app.core.logging import logger
from app.schemas.profile import DatasetProfile
from app.schemas.semantic import (
    SemanticModel,
    SemanticColumn,
    SemanticRelationship,
    SemanticEntity,
    SemanticMetadata,
    NullableRecommendation
)
from app.semantic.dictionary import SemanticDictionary
from app.semantic.knowledge_base import MedicalKnowledgeBase
from app.semantic.relationship import RelationshipDetector


class SemanticModelBuilder:
    """
    Coordinates matching dictionary and knowledge base mappings over
    a dataset profile to build a cohesive Healthcare Semantic Model.
    """
    def __init__(
        self,
        dictionary: SemanticDictionary,
        knowledge_base: MedicalKnowledgeBase
    ) -> None:
        self.dictionary = dictionary
        self.knowledge_base = knowledge_base

    def build_model(self, profile: DatasetProfile) -> SemanticModel:
        """
        Translates a DatasetProfile into a SemanticModel.
        """
        logger.info(f"Building semantic model for dataset {profile.dataset_id}")
        
        mapped_columns: Dict[str, SemanticColumn] = {}
        unmapped_count = 0
        mapped_count = 0
        total_confidence = 0.0

        # Track mapped standard concepts for completeness calculation
        key_concepts = {"DISEASE", "AGE", "GENDER", "ADMISSION_DATE", "OUTCOME"}
        found_key_concepts = set()

        # 1. Map Columns
        for norm_name, col_prof in profile.columns.items():
            # Lookup standard concept in dictionary
            concept, conf = self.dictionary.lookup_column(col_prof.original_name)
            
            # If dictionary lookup failed, verify if column has data role mappings
            if concept == "UNKNOWN":
                # Fallback heuristics based on logical data types
                if col_prof.detected_data_type == "EMAIL":
                    concept, conf = "EMAIL", 0.70
                elif col_prof.detected_data_type == "PHONE":
                    concept, conf = "PHONE", 0.70
                elif col_prof.detected_data_type == "ZIPCODE":
                    concept, conf = "LOCATION", 0.70
            
            if concept == "UNKNOWN":
                unmapped_count += 1
                entity_group = "Unmapped"
                medical_category = "General"
                expected_units = None
                null_rec = {"allowed": True, "imputation_strategy": "none"}
                
                # Fetch fallback rules based on logical type
                analysis_meta = self.knowledge_base.get_analysis_metadata(concept, col_prof.detected_data_type)
            else:
                mapped_count += 1
                total_confidence += conf
                if concept in key_concepts:
                    found_key_concepts.add(concept)
                    
                # Fetch details from Medical Knowledge Base
                entity_meta = self.knowledge_base.get_entity_metadata(concept)
                entity_group = entity_meta["entity_group"]
                medical_category = entity_meta["medical_category"]
                expected_units = entity_meta["expected_units"]
                null_rec = entity_meta["nullable_recommendation"]
                
                analysis_meta = self.knowledge_base.get_analysis_metadata(concept, col_prof.detected_data_type)

            sem_col = SemanticColumn(
                original_name=col_prof.original_name,
                normalized_name=norm_name,
                semantic_type=concept,
                confidence_score=conf,
                entity_group=entity_group,
                medical_category=medical_category,
                expected_analysis=analysis_meta.get("expected_analysis", []),
                suggested_visualizations=analysis_meta.get("suggested_visualizations", []),
                allowed_aggregations=analysis_meta.get("allowed_aggregations", []),
                expected_units=expected_units,
                nullable_recommendation=NullableRecommendation(
                    allowed=null_rec["allowed"],
                    imputation_strategy=null_rec["imputation_strategy"]
                )
            )
            mapped_columns[norm_name] = sem_col

        # 2. Assemble Entities (Group columns by entity_group)
        entities: Dict[str, SemanticEntity] = {}
        for norm_name, col in mapped_columns.items():
            grp = col.entity_group
            if grp not in entities:
                entities[grp] = SemanticEntity(
                    name=grp,
                    columns=[],
                    description=f"Logical grouping of columns related to {grp} attributes."
                )
            entities[grp].columns.append(norm_name)

        # 3. Detect Relationships
        relationships = RelationshipDetector.detect_relationships(mapped_columns)

        # 4. Calculate Metadata summaries
        mean_conf = total_confidence / mapped_count if mapped_count > 0 else 0.0
        completeness = (len(found_key_concepts) / len(key_concepts)) * 100.0

        metadata = SemanticMetadata(
            mapped_columns_count=mapped_count,
            unmapped_columns_count=unmapped_count,
            mean_confidence_score=round(mean_conf, 2),
            completeness_score=round(completeness, 2)
        )

        # 5. Build Model
        return SemanticModel(
            dataset_id=profile.dataset_id,
            columns=mapped_columns,
            relationships=relationships,
            entities=entities,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )
