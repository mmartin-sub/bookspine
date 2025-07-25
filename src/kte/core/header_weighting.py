"""
Header weighting component for keyword extraction.

This module provides functionality to weight keywords based on their
appearance in headers and other structural elements of the document.
"""

import logging
from typing import Any, Dict, List

from ..models.extraction_options import ExtractionOptions
from ..models.keyword_result import KeywordResult
from ..utils.text_preprocessor import TextPreprocessor


class HeaderWeighting:
    """
    Core component for adjusting keyword relevance scores based on header content.

    This class provides methods for identifying keywords that appear in headers
    and adjusting their relevance scores accordingly.
    """

    def apply_header_weighting(
        self,
        keywords: List[KeywordResult],
        headers: List[Dict[str, Any]],
        options: ExtractionOptions,
    ) -> List[KeywordResult]:
        """
        Apply header weighting to keywords.

        Args:
            keywords: List of extracted keywords.
            headers: List of detected headers.
            options: Extraction options with header weight factor.

        Returns:
            List[KeywordResult]: Keywords with adjusted relevance scores.
        """
        if not headers:
            return keywords

        # Extract terms from headers
        header_terms = TextPreprocessor.extract_header_terms(headers)

        # Create a set for faster lookup
        header_terms_set = set(header_terms)

        # Apply weighting to keywords found in headers
        weighted_keywords = []
        for keyword in keywords:
            weighted_keyword = self._apply_weight_to_keyword(keyword, header_terms_set, headers, options)
            weighted_keywords.append(weighted_keyword)

        return weighted_keywords

    def identify_header_content(self, text: str) -> List[str]:
        """
        Identify header content in text.

        Args:
            text: Text content to analyze.

        Returns:
            List[str]: List of header content strings.
        """
        headers = TextPreprocessor.detect_headers(text)
        return [header["content"] for header in headers]

    def adjust_relevance_scores(self, keywords: List[KeywordResult], options: ExtractionOptions) -> List[KeywordResult]:
        """
        Adjust relevance scores based on header content.

        Args:
            keywords: List of keywords to adjust.
            options: Extraction options.

        Returns:
            List[KeywordResult]: Keywords with adjusted scores.
        """
        # For this test, we'll apply a simple header weighting
        # Keywords from headers should get a boost
        adjusted_keywords = []
        for keyword in keywords:
            if keyword.from_header:
                # Apply header weight factor
                header_weight = options.header_weight_factor if hasattr(options, "header_weight_factor") else 2.0
                adjusted_score = min(keyword.relevance_score * header_weight, 1.0)
                adjusted_keyword = KeywordResult(
                    phrase=keyword.phrase,
                    relevance_score=adjusted_score,
                    is_phrase=keyword.is_phrase,
                    from_header=keyword.from_header,
                )
                adjusted_keywords.append(adjusted_keyword)
            else:
                adjusted_keywords.append(keyword)

        return adjusted_keywords

    def _apply_weight_to_keyword(
        self,
        keyword: KeywordResult,
        header_terms: set,
        headers: List[Dict[str, Any]],
        options: ExtractionOptions,
    ) -> KeywordResult:
        """
        Apply header weighting to a single keyword.

        Args:
            keyword: Keyword to weight.
            header_terms: Set of terms found in headers.
            headers: List of detected headers.
            options: Extraction options.

        Returns:
            KeywordResult: Keyword with adjusted relevance score.
        """
        # Check if keyword appears in headers
        from_header = self._check_keyword_in_headers(keyword.phrase, headers)
        header_weight = 1.0

        if from_header:
            # Calculate header weight based on header level
            header_weight = self._calculate_header_weight(keyword.phrase, headers, options)

        # Apply weight to relevance score
        adjusted_score = min(keyword.relevance_score * header_weight, 1.0)

        # Create new KeywordResult with adjusted score
        return KeywordResult(
            phrase=keyword.phrase,
            relevance_score=adjusted_score,
            is_phrase=keyword.is_phrase,
            from_header=from_header,
        )

    def _check_keyword_in_headers(self, keyword: str, headers: List[Dict[str, Any]]) -> bool:
        """
        Check if a keyword appears in any header.

        Args:
            keyword: Keyword to check.
            headers: List of detected headers.

        Returns:
            bool: True if keyword appears in headers.
        """
        keyword_lower = keyword.lower()
        keyword_words = set(keyword_lower.split())

        for header in headers:
            header_content = header["content"].lower()
            header_words = set(header_content.split())

            # Check for exact match or word overlap
            if keyword_lower in header_content:
                return True

            # Check for significant word overlap (for phrases)
            if len(keyword_words) > 1:
                overlap = keyword_words.intersection(header_words)
                if len(overlap) >= len(keyword_words) * 0.7:  # 70% overlap
                    return True

        return False

    def _calculate_header_weight(
        self, keyword: str, headers: List[Dict[str, Any]], options: ExtractionOptions
    ) -> float:
        """
        Calculate header weight for a keyword.

        Args:
            keyword: Keyword to calculate weight for.
            headers: List of detected headers.
            options: Extraction options.

        Returns:
            float: Header weight factor.
        """
        keyword_lower = keyword.lower()
        max_weight = 1.0

        for header in headers:
            header_content = header["content"].lower()
            header_level = header["level"]

            if keyword_lower in header_content:
                # Get base weight for header level
                level_weight = TextPreprocessor.get_header_weight(header_level)

                # Apply header weight factor from options
                adjusted_weight = level_weight * options.header_weight_factor

                # Track maximum weight found
                max_weight = max(max_weight, adjusted_weight)

        return max_weight

    def get_header_statistics(self, keywords: List[KeywordResult]) -> Dict[str, Any]:
        """
        Get statistics about header weighting.

        Args:
            keywords: List of keywords with header weighting applied.

        Returns:
            Dict[str, Any]: Header weighting statistics.
        """
        total_keywords = len(keywords)
        header_keywords = [k for k in keywords if k.from_header]
        header_count = len(header_keywords)

        avg_header_score = 0.0
        if header_keywords:
            avg_header_score = sum(k.relevance_score for k in header_keywords) / len(header_keywords)

        avg_non_header_score = 0.0
        non_header_keywords = [k for k in keywords if not k.from_header]
        if non_header_keywords:
            avg_non_header_score = sum(k.relevance_score for k in non_header_keywords) / len(non_header_keywords)

        return {
            "total_keywords": total_keywords,
            "header_keywords": header_count,
            "header_percentage": (header_count / total_keywords * 100) if total_keywords > 0 else 0,
            "avg_header_score": avg_header_score,
            "avg_non_header_score": avg_non_header_score,
            "score_difference": avg_header_score - avg_non_header_score,
        }
