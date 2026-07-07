import re
import pandas as pd
from typing import Union, List, Any
from app.core.logging import logger

# Compiled Regex patterns for deterministic checks
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$")
ZIP_REGEX = re.compile(r"^\d{5}(-\d{4})?$")
TIME_REGEX = re.compile(r"^\d{2}:\d{2}(:\d{2})?$")


class DataTypeDetector:
    """
    Utility executing deterministic heuristics on pandas/cuDF Series
    to classify the logical data type and semantic role of columns.
    """

    @staticmethod
    def detect_type(series: pd.Series) -> str:
        """
        Detects the logical datatype of a Series.
        Returns one of: INTEGER, FLOAT, BOOLEAN, STRING, TEXT, CATEGORY, DATE, DATETIME, TIME, EMAIL, PHONE, ZIPCODE, UNKNOWN.
        """
        # Drop null values for analysis
        non_nulls = series.dropna()
        if len(non_nulls) == 0:
            return "UNKNOWN"

        # Obtain underlying numpy/python type name
        dtype_str = str(series.dtype).lower()

        # 1. Check native Boolean dtype or boolean-like patterns
        if "bool" in dtype_str:
            return "BOOLEAN"

        unique_vals = non_nulls.unique()
        if len(unique_vals) <= 2:
            # Check boolean representations
            str_vals = {str(x).strip().lower() for x in unique_vals}
            bool_markers = {"true", "false", "t", "f", "1", "0", "yes", "no", "y", "n"}
            if str_vals.issubset(bool_markers):
                return "BOOLEAN"

        # 2. Check native numeric dtypes
        is_numeric = pd.api.types.is_numeric_dtype(series)

        # 3. Check for Date / Datetime representation
        # Take a subset of values for checking to keep performance high
        sample_size = min(len(non_nulls), 200)
        sample = non_nulls.sample(n=sample_size, random_state=42) if len(non_nulls) > sample_size else non_nulls
        sample_str = sample.astype(str).str.strip()

        # Check if the series represents isolated times (HH:MM:SS)
        if not is_numeric and all(TIME_REGEX.match(val) for val in sample_str):
            return "TIME"

        if "datetime" in dtype_str:
            # Differentiate DATE vs DATETIME
            if all(hasattr(val, "hour") and val.hour == 0 and val.minute == 0 and val.second == 0 for val in sample):
                return "DATE"
            return "DATETIME"

        # Attempt date parsing on string samples
        if not is_numeric:
            parsed_dates_count = 0
            for val in sample_str:
                if len(val) >= 4 and not val.isdigit(): # avoid reading numbers like '2020' as dates
                    try:
                        pd.to_datetime(val, errors="raise")
                        parsed_dates_count += 1
                    except Exception:
                        pass
            
            # If >85% of sample values are parseable datetimes
            if parsed_dates_count / sample_size > 0.85:
                # Differentiate DATE vs DATETIME
                try:
                    parsed_series = pd.to_datetime(sample_str, errors="coerce")
                    if all(parsed_series.dt.hour == 0) and all(parsed_series.dt.minute == 0):
                        return "DATE"
                    return "DATETIME"
                except Exception:
                    return "DATETIME"

        # 4. Check specific text structures (Email, Phone, Zipcode)
        if not is_numeric:
            email_matches = 0
            phone_matches = 0
            zip_matches = 0
            
            for val in sample_str:
                if EMAIL_REGEX.match(val):
                    email_matches += 1
                elif PHONE_REGEX.match(val):
                    phone_matches += 1
                elif ZIP_REGEX.match(val):
                    zip_matches += 1
                    
            if email_matches / sample_size > 0.85:
                return "EMAIL"
            if phone_matches / sample_size > 0.85:
                return "PHONE"
            if zip_matches / sample_size > 0.85:
                return "ZIPCODE"

        # If zip code is stored as integer type but fits 5-digit zip patterns
        if is_numeric and "int" in dtype_str:
            # If column name matches zip and all values are in US zip range
            col_name = str(series.name).lower() if series.name else ""
            if "zip" in col_name or "postal" in col_name:
                if all(0 <= val <= 99999 for val in sample):
                    return "ZIPCODE"

        # 5. Resolve standard numeric categories
        if is_numeric:
            if "int" in dtype_str:
                return "INTEGER"
            return "FLOAT"

        # 6. Differentiate TEXT, CATEGORY and STRING
        # Check average character lengths and words count first to find free text
        avg_len = sample_str.str.len().mean()
        word_counts = sample_str.str.split().str.len()
        avg_word_count = word_counts.mean()

        if avg_len > 50 or avg_word_count > 5:
            return "TEXT"

        # Low cardinality check for category classification
        unique_ratio = len(unique_vals) / len(series)
        if len(unique_vals) < 25 or (unique_ratio < 0.08 and len(unique_vals) < 200):
            return "CATEGORY"

        return "STRING"

    @staticmethod
    def infer_roles(
        col_name: str,
        detected_type: str,
        unique_vals: List[Any],
        total_rows: int,
        series: pd.Series
    ) -> List[str]:
        """
        Determines semantic/analytical roles that this column represents.
        Returns a list of roles, including:
        Identifier, Measurement, Timestamp, Target Variable, Free Text, Location, Binary Value, Ordinal Category, Nominal Category, Confidence Score
        """
        roles: List[str] = []
        name_lower = col_name.lower()
        unique_count = len(unique_vals)
        non_null_count = series.dropna().count()

        # 1. Identifier
        id_keywords = {"id", "uuid", "guid", "code", "patient_id", "mrn", "ssn", "key", "pk", "pid"}
        # If column name contains key identifier terms OR is highly unique string/int
        is_id_name = any(k in name_lower.split("_") or name_lower == k for k in id_keywords)
        if is_id_name or (unique_count == total_rows and detected_type in {"INTEGER", "STRING"}):
            roles.append("Identifier")

        # 2. Binary Value
        if unique_count == 2:
            roles.append("Binary Value")

        # 3. Timestamp
        if detected_type in {"DATE", "DATETIME", "TIME"}:
            roles.append("Timestamp")

        # 4. Location
        loc_keywords = {"city", "state", "zip", "country", "address", "latitude", "longitude", "lat", "lon", "region", "county"}
        if any(k in name_lower for k in loc_keywords) or detected_type == "ZIPCODE":
            roles.append("Location")

        # 5. Free Text
        if detected_type == "TEXT":
            roles.append("Free Text")

        # 6. Target Variable
        target_keywords = {"label", "target", "outcome", "class", "diagnosis", "status", "death", "readmitted", "survived", "y", "admitted"}
        if any(k == name_lower or name_lower.startswith(k + "_") or name_lower.endswith("_" + k) for k in target_keywords):
            # Target variables are usually categorical or binary labels
            if detected_type in {"CATEGORY", "BOOLEAN", "INTEGER", "STRING"} and unique_count < 100:
                roles.append("Target Variable")

        # 7. Confidence Score
        score_keywords = {"score", "probability", "confidence", "prob", "p_value"}
        if detected_type == "FLOAT":
            if any(k in name_lower for k in score_keywords):
                # Ensure values fall primarily in [0.0, 1.0] or [0.0, 100.0]
                non_null_series = series.dropna()
                if len(non_null_series) > 0:
                    if non_null_series.min() >= 0.0 and non_null_series.max() <= 100.0:
                        roles.append("Confidence Score")

        # 8. Measurement
        # Numeric values that are NOT identifiers or confidence scores
        if detected_type in {"INTEGER", "FLOAT"} and "Identifier" not in roles:
            # Measurement metrics (e.g. blood pressure, cholesterol, pulse, heart rate)
            measurement_indicators = {
                "rate", "value", "temp", "blood", "bp", "systolic", "diastolic", "level", "age",
                "weight", "height", "count", "amount", "ratio", "concentration", "pulse", "glucose", "bmi"
            }
            if any(k in name_lower for k in measurement_indicators) or detected_type == "FLOAT":
                roles.append("Measurement")

        # 9. Ordinal Category / Nominal Category
        if detected_type == "CATEGORY" and "Identifier" not in roles:
            # Check if it has ordering clues (e.g. stage, grade, level, severity, rating)
            ordinal_keywords = {"stage", "grade", "level", "severity", "rating", "class", "group"}
            if any(k in name_lower for k in ordinal_keywords):
                roles.append("Ordinal Category")
            else:
                roles.append("Nominal Category")

        return roles
