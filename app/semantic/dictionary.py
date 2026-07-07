import os
import json
from typing import Dict, List, Tuple
from app.core.logging import logger


class SemanticDictionary:
    """
    Loads and query-matches the dictionary configuration mapping raw column names
    and unit variations to standard healthcare concepts.
    """
    def __init__(self, dict_path: str = None, synonyms_path: str = None) -> None:
        # Resolve paths dynamically relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_dict = os.path.abspath(
            os.path.join(current_dir, "..", "config", "semantic", "semantic_dictionary.json")
        )
        default_synonyms = os.path.abspath(
            os.path.join(current_dir, "..", "config", "semantic", "medical_synonyms.json")
        )

        self.dict_path = dict_path or default_dict
        self.synonyms_path = synonyms_path or default_synonyms
        
        self.concepts_map: Dict[str, List[str]] = {}
        self.suffixes_map: Dict[str, List[str]] = {}
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Reads synonyms and mappings from dynamic JSON files."""
        try:
            if os.path.exists(self.dict_path):
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    self.concepts_map = json.load(f)
                logger.debug(f"SemanticDictionary: Loaded mapping from {self.dict_path}")
            else:
                logger.warning(f"SemanticDictionary file missing at: {self.dict_path}")
        except Exception as e:
            logger.error(f"Failed to load semantic dictionary mapping file: {e}")

        try:
            if os.path.exists(self.synonyms_path):
                with open(self.synonyms_path, "r", encoding="utf-8") as f:
                    syn_data = json.load(f)
                    self.suffixes_map = syn_data.get("suffixes", {})
                logger.debug(f"SemanticDictionary: Loaded suffixes from {self.synonyms_path}")
            else:
                logger.warning(f"SemanticDictionary synonyms file missing at: {self.synonyms_path}")
        except Exception as e:
            logger.error(f"Failed to load medical synonyms configuration file: {e}")

    def lookup_column(self, col_name: str) -> Tuple[str, float]:
        """
        Attempts to align a raw column header to standard concepts.
        Returns a tuple of (Semantic Concept Name, Confidence Score).
        """
        # Normalize for matching: lowercased, spaces replaced by underscores, multiple underscores stripped
        clean_name = col_name.strip().lower().replace(" ", "_")
        clean_name = re_underscore = re_replace_underscores(clean_name)
        
        # 1. Direct exact match in synonyms lists
        for concept, synonyms in self.concepts_map.items():
            for syn in synonyms:
                syn_clean = syn.strip().lower().replace(" ", "_")
                if clean_name == syn_clean:
                    return concept, 1.0

        # 2. Suffix / Substring matches using synonyms
        for concept, synonyms in self.concepts_map.items():
            for syn in synonyms:
                syn_clean = syn.strip().lower().replace(" ", "_")
                # Avoid matching very short terms (like 'wt' or 'bp') as substrings to prevent false matches
                if len(syn_clean) > 2:
                    if clean_name.startswith(f"{syn_clean}_") or clean_name.endswith(f"_{syn_clean}"):
                        return concept, 0.85

        # 3. Dedicated suffix-matches from synonyms configuration
        for concept, suffixes in self.suffixes_map.items():
            for suffix in suffixes:
                suff_clean = suffix.strip().lower()
                if clean_name.endswith(suff_clean) or clean_name.startswith(suff_clean):
                    return concept, 0.80

        # 4. Partial substring containment check
        for concept, synonyms in self.concepts_map.items():
            for syn in synonyms:
                syn_clean = syn.strip().lower().replace(" ", "_")
                if len(syn_clean) > 3 and syn_clean in clean_name:
                    return concept, 0.70

        return "UNKNOWN", 0.0


def re_replace_underscores(name: str) -> str:
    """Helper to clean multiple consecutive underscores."""
    import re
    return re.sub(r"_+", "_", name).strip("_")
