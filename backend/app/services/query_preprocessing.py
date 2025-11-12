"""
Query Preprocessing Service
Handles query cleaning, expansion, and optimization for Polish language queries
"""

import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)

# Polish abbreviations commonly used in legal/official contexts
POLISH_ABBREVIATIONS: Dict[str, str] = {
    "np.": "na przykład",
    "tj.": "to jest",
    "tzn.": "to znaczy",
    "itp.": "i tak podobnie",
    "itd.": "i tak dalej",
    "m.in.": "między innymi",
    "zł": "złotych",
    "PLN": "złotych polskich",
    "tys.": "tysięcy",
    "mln": "milionów",
    "mld": "miliardów",
    "dr": "doktor",
    "prof.": "profesor",
    "mgr": "magister",
    "inż.": "inżynier",
    "ul.": "ulica",
    "al.": "aleja",
    "pl.": "plac",
    "godz.": "godzina",
    "min.": "minut",
    "sek.": "sekund",
    "r.": "roku",
    "nr": "numer",
    "art.": "artykuł",
    "ust.": "ustęp",
    "pkt": "punkt",
    "lit.": "litera",
    "par.": "paragraf",
    "str.": "strona",
    "ww.": "wyżej wymieniony",
    "wg": "według",
    "dot.": "dotyczący",
    "zob.": "zobacz",
    "por.": "porównaj",
    "tzw.": "tak zwany",
    "ok.": "około",
    "max": "maksymalnie",
    "min": "minimalnie",
    "śr.": "średnio",
    "temp.": "temperatura",
    "proc.": "procent",
    "%": "procent",
}


class QueryPreprocessor:
    """Preprocesses queries for better retrieval performance"""

    def __init__(self):
        """Initialize query preprocessor"""
        logger.info("Query Preprocessor initialized")

    def preprocess(self, query: str) -> str:
        """
        Preprocess a query to improve retrieval.

        Steps:
        1. Normalize whitespace
        2. Expand Polish abbreviations
        3. Remove excessive punctuation
        4. Normalize case (while preserving important capitals)

        Args:
            query: Raw user query

        Returns:
            Preprocessed query
        """
        if not query:
            return query

        original_query = query
        logger.debug(f"Preprocessing query: {query[:100]}...")

        # Step 1: Normalize whitespace
        query = self._normalize_whitespace(query)

        # Step 2: Expand abbreviations
        query = self._expand_abbreviations(query)

        # Step 3: Clean punctuation
        query = self._clean_punctuation(query)

        # Step 4: Normalize whitespace again after expansions
        query = self._normalize_whitespace(query)

        if query != original_query:
            logger.debug(f"Preprocessed: {original_query} -> {query}")

        return query

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Trim leading/trailing whitespace
        return text.strip()

    def _expand_abbreviations(self, text: str) -> str:
        """
        Expand Polish abbreviations to full forms.

        Args:
            text: Input text

        Returns:
            Text with expanded abbreviations
        """
        for abbr, full_form in POLISH_ABBREVIATIONS.items():
            # Use word boundaries to avoid partial matches
            # Case-insensitive for better matching
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, full_form, text, flags=re.IGNORECASE)

        return text

    def _clean_punctuation(self, text: str) -> str:
        """
        Clean excessive or problematic punctuation.

        Args:
            text: Input text

        Returns:
            Text with cleaned punctuation
        """
        # Remove multiple question marks or exclamation points
        text = re.sub(r'[?!]{2,}', '?', text)

        # Remove trailing punctuation that doesn't add meaning
        text = re.sub(r'\s+[.,;:]+\s*$', '', text)

        return text

    def expand_query_variations(self, query: str) -> list[str]:
        """
        Generate query variations for multi-query retrieval.

        This can be used for advanced retrieval strategies.

        Args:
            query: Original query

        Returns:
            List of query variations
        """
        variations = [query]

        # Add preprocessed version if different
        preprocessed = self.preprocess(query)
        if preprocessed != query:
            variations.append(preprocessed)

        # Could add more variations here:
        # - Synonyms
        # - Related terms
        # - Different phrasings

        return list(set(variations))  # Deduplicate


# Singleton instance
_preprocessor: QueryPreprocessor | None = None


def get_query_preprocessor() -> QueryPreprocessor:
    """
    Get or create the query preprocessor singleton.

    Returns:
        QueryPreprocessor instance
    """
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = QueryPreprocessor()
    return _preprocessor
