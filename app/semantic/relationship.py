from typing import List, Dict
from app.schemas.semantic import SemanticColumn, SemanticRelationship


class RelationshipDetector:
    """
    Scans mapped semantic columns within a dataset profile
    to identify relevant clinical, temporal, and demographic relationships.
    """

    @staticmethod
    def detect_relationships(columns: Dict[str, SemanticColumn]) -> List[SemanticRelationship]:
        """
        Traverses columns to identify clinical links.
        Returns a list of SemanticRelationship models.
        """
        relationships: List[SemanticRelationship] = []

        # Find columns by their semantic type
        concept_cols: Dict[str, List[str]] = {}
        for norm_name, col in columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_cols:
                    concept_cols[sem_type] = []
                concept_cols[sem_type].append(norm_name)

        # 1. Temporal: ADMISSION_DATE and DISCHARGE_DATE
        if "ADMISSION_DATE" in concept_cols and "DISCHARGE_DATE" in concept_cols:
            admission_col = concept_cols["ADMISSION_DATE"][0]
            discharge_col = concept_cols["DISCHARGE_DATE"][0]
            relationships.append(SemanticRelationship(
                name="admission_to_discharge_duration",
                relationship_type="temporal",
                source_column=admission_col,
                target_column=discharge_col,
                description="Links patient admission timestamp to discharge timestamp to evaluate stay duration.",
                recommended_analysis="Compute difference in days between discharge_date and admission_date to calculate stay duration."
            ))

        # 2. Demographic Correlation: AGE and DISEASE
        if "AGE" in concept_cols and "DISEASE" in concept_cols:
            age_col = concept_cols["AGE"][0]
            disease_col = concept_cols["DISEASE"][0]
            relationships.append(SemanticRelationship(
                name="age_vs_disease_prevalence",
                relationship_type="demographic_correlation",
                source_column=age_col,
                target_column=disease_col,
                description="Correlates patient age demographics with diagnosis patterns.",
                recommended_analysis="Group patient age values into bins (cohorts) and calculate disease incidence percentages."
            ))

        # 3. Demographic Correlation: GENDER and DISEASE
        if "GENDER" in concept_cols and "DISEASE" in concept_cols:
            gender_col = concept_cols["GENDER"][0]
            disease_col = concept_cols["DISEASE"][0]
            relationships.append(SemanticRelationship(
                name="gender_vs_disease_prevalence",
                relationship_type="demographic_correlation",
                source_column=gender_col,
                target_column=disease_col,
                description="Compares disease distribution metrics between genders.",
                recommended_analysis="Perform cross-tabulation count analysis of gender distributions per diagnosis label."
            ))

        # 4. Clinical Outcome: DISEASE and OUTCOME
        if "DISEASE" in concept_cols and "OUTCOME" in concept_cols:
            disease_col = concept_cols["DISEASE"][0]
            outcome_col = concept_cols["OUTCOME"][0]
            relationships.append(SemanticRelationship(
                name="disease_vs_outcome_association",
                relationship_type="clinical_outcome",
                source_column=disease_col,
                target_column=outcome_col,
                description="Analyzes recovery, readmission, or mortality ratios grouped by medical diagnosis.",
                recommended_analysis="Examine recovery and readmission rate distributions grouped by disease category."
            ))

        # 5. Comparative: HOSPITAL and DISEASE
        if "HOSPITAL" in concept_cols and "DISEASE" in concept_cols:
            hospital_col = concept_cols["HOSPITAL"][0]
            disease_col = concept_cols["DISEASE"][0]
            relationships.append(SemanticRelationship(
                name="hospital_vs_disease_incidence",
                relationship_type="comparative",
                source_column=hospital_col,
                target_column=disease_col,
                description="Compares disease caseload profiles across healthcare facilities.",
                recommended_analysis="Compute disease frequency counts grouped by hospital identifier."
            ))

        # 6. Geographical: LOCATION and DISEASE
        if "LOCATION" in concept_cols and "DISEASE" in concept_cols:
            loc_col = concept_cols["LOCATION"][0]
            disease_col = concept_cols["DISEASE"][0]
            relationships.append(SemanticRelationship(
                name="location_vs_disease_distribution",
                relationship_type="geographical",
                source_column=loc_col,
                target_column=disease_col,
                description="Maps regional disease incidence rates.",
                recommended_analysis="Examine disease counts and frequencies grouped by location/zipcode."
            ))

        return relationships
