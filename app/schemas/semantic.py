from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NullableRecommendation(BaseModel):
    """Null value handling recommendation for a mapped concept."""
    allowed: bool = Field(..., description="Is null/missing value allowed in downstream operations.")
    imputation_strategy: str = Field(..., description="Imputation strategy (mean, median, mode, drop, none).")


class SemanticColumn(BaseModel):
    """
    Semantic definition and metadata for a column inside the dataset.
    """
    original_name: str = Field(..., description="Raw column name from the CSV headers.")
    normalized_name: str = Field(..., description="Normalized snake_case column identifier.")
    semantic_type: str = Field(..., description="Canonical mapped type (e.g. DISEASE, AGE, GENDER).")
    confidence_score: float = Field(..., description="Classification confidence (0.0 to 1.0).")
    entity_group: str = Field(..., description="Entity logical group (Patient, Encounter, Vitals, etc.).")
    medical_category: str = Field(..., description="Medical clinical category (Demographic, Vitals, Diagnostic).")
    expected_analysis: List[str] = Field(default_factory=list, description="Downstream analyses relevant to this concept.")
    suggested_visualizations: List[str] = Field(default_factory=list, description="Suitable chart groups for this concept.")
    allowed_aggregations: List[str] = Field(default_factory=list, description="Aggregations valid for this concept.")
    expected_units: Optional[str] = Field(None, description="Expected unit of measurement.")
    nullable_recommendation: NullableRecommendation = Field(..., description="Missing value imputation guidance.")


class SemanticRelationship(BaseModel):
    """
    Clinical or analytical relationship detected between two columns.
    """
    name: str = Field(..., description="Identifier name of the relationship.")
    relationship_type: str = Field(..., description="Relationship grouping (e.g. temporal, correlation).")
    source_column: str = Field(..., description="Normalized name of the primary/source column.")
    target_column: str = Field(..., description="Normalized name of the secondary/target column.")
    description: str = Field(..., description="Human-readable summary of the relationship significance.")
    recommended_analysis: str = Field(..., description="The mathematical analytical procedure suggested.")


class SemanticEntity(BaseModel):
    """
    Group of columns mapping to a cohesive domain entity (e.g. Patient Demographic details).
    """
    name: str = Field(..., description="Entity name.")
    columns: List[str] = Field(..., description="Normalized column names belonging to this entity.")
    description: str = Field(..., description="Descriptive context of this entity.")


class SemanticMetadata(BaseModel):
    """
    Summary metrics representing the quality and richness of the semantic mapping.
    """
    mapped_columns_count: int = Field(..., description="Count of columns successfully mapped to standard concepts.")
    unmapped_columns_count: int = Field(..., description="Count of columns left as UNKNOWN.")
    mean_confidence_score: float = Field(..., description="Average confidence score across all columns.")
    completeness_score: float = Field(..., description="Percentage of key clinical concepts mapped (0.0 to 100.0).")


class SemanticModel(BaseModel):
    """
    Unified Healthcare Semantic Model wrapping all columns, entities, and relationships.
    """
    dataset_id: str = Field(..., description="The profiled dataset UUID.")
    columns: Dict[str, SemanticColumn] = Field(..., description="Mapping of normalized column names to their semantic schemas.")
    relationships: List[SemanticRelationship] = Field(default_factory=list, description="Detected clinical relationships.")
    entities: Dict[str, SemanticEntity] = Field(default_factory=dict, description="Reconstructed logical entities.")
    metadata: SemanticMetadata = Field(..., description="Semantic mapping health metadata.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Semantic model creation timestamp.")


class SemanticModelResponse(BaseModel):
    """
    API Response model returned by semantic endpoints.
    """
    dataset_id: str = Field(..., description="The analyzed dataset UUID.")
    semantic_model: SemanticModel = Field(..., description="The complete generated semantic model.")
    recalculated: bool = Field(False, description="Flag indicating if the model was rebuilt or fetched from cache.")
