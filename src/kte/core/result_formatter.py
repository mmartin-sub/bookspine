"""
Result formatter for keyword extraction.

This module provides functionality to format and rank keyword
extraction results based on various criteria.
"""

import logging
from typing import Any, Dict, List, Optional

from ..models.extraction_options import ExtractionOptions
from ..models.keyword_result import KeywordResult


class ResultFormatter:
    """
    Core component for formatting and ranking keyword extraction results.

    This class provides methods for ranking keywords, applying filtering,
    and preparing results for output.
    """

    def format_results(self, keywords: List[KeywordResult], options: ExtractionOptions) -> List[KeywordResult]:
        """
        Format and rank keyword results.

        Args:
            keywords: List of extracted keywords.
            options: Extraction options for formatting.

        Returns:
            List[KeywordResult]: Formatted and ranked keywords.
        """
        if not keywords:
            return []

        # Apply phrase prioritization if enabled
        if options.prefer_phrases:
            keywords = self._prioritize_phrases(keywords)

        # Sort by relevance score
        keywords = self._sort_by_relevance(keywords)

        # Apply minimum relevance filter
        keywords = self._filter_by_relevance(keywords, options.min_relevance)

        # Limit to maximum keywords
        keywords = keywords[: options.max_keywords]

        return keywords

    def rank_keywords_by_relevance(self, keywords: List[KeywordResult]) -> List[KeywordResult]:
        """
        Rank keywords by relevance score.

        Args:
            keywords: List of keywords to rank.

        Returns:
            List[KeywordResult]: Ranked keywords.
        """
        return self._sort_by_relevance(keywords)

    def prioritize_phrases(self, keywords: List[KeywordResult], options: ExtractionOptions) -> List[KeywordResult]:
        """
        Prioritize multi-word phrases over single words.

        Args:
            keywords: List of keywords to prioritize.
            options: Extraction options.

        Returns:
            List[KeywordResult]: Keywords with phrases prioritized.
        """
        return self._prioritize_phrases(keywords)

    def filter_and_limit_results(
        self, keywords: List[KeywordResult], options: ExtractionOptions
    ) -> List[KeywordResult]:
        """
        Filter and limit keyword results.

        Args:
            keywords: List of keywords to filter.
            options: Extraction options for filtering.

        Returns:
            List[KeywordResult]: Filtered and limited keywords.
        """
        # Filter by relevance
        filtered = self._filter_by_relevance(keywords, options.min_relevance)

        # Limit to maximum keywords
        return filtered[: options.max_keywords]

    def generate_metadata(self, keywords: List[KeywordResult], source: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate metadata for keyword results.

        Args:
            keywords: List of keyword results.
            source: Source of the keywords.

        Returns:
            Dict[str, Any]: Metadata about the results.
        """
        if not keywords:
            return {
                "total_keywords": 0,
                "phrases_count": 0,
                "single_words_count": 0,
                "header_keywords_count": 0,
                "average_relevance": 0.0,
            }

        phrases = [k for k in keywords if k.is_phrase]
        header_keywords = [k for k in keywords if k.from_header]

        metadata: Dict[str, Any] = {
            "total_keywords": len(keywords),
            "phrases_count": len(phrases),
            "single_words_count": len(keywords) - len(phrases),
            "header_keywords_count": len(header_keywords),
            "average_relevance": float(sum(k.relevance_score for k in keywords) / len(keywords)),
            "max_relevance": float(max(k.relevance_score for k in keywords)),
            "min_relevance": float(min(k.relevance_score for k in keywords)),
        }

        if source is not None:
            metadata["source"] = source

        return metadata

    def _prioritize_phrases(self, keywords: List[KeywordResult]) -> List[KeywordResult]:
        """
        Prioritize multi-word phrases over single words.

        Args:
            keywords: List of keywords to prioritize.

        Returns:
            List[KeywordResult]: Keywords with phrases prioritized.
        """
        phrases = [k for k in keywords if k.is_phrase]
        single_words = [k for k in keywords if not k.is_phrase]

        # Sort phrases and single words separately by relevance
        phrases.sort(key=lambda x: x.relevance_score, reverse=True)
        single_words.sort(key=lambda x: x.relevance_score, reverse=True)

        # Prioritize phrases by putting them first, then single words
        result: List[KeywordResult] = []
        result.extend(phrases)
        result.extend(single_words)

        return result

    def _sort_by_relevance(self, keywords: List[KeywordResult]) -> List[KeywordResult]:
        """
        Sort keywords by relevance score.

        Args:
            keywords: List of keywords to sort.

        Returns:
            List[KeywordResult]: Sorted keywords.
        """
        return sorted(keywords, key=lambda x: x.relevance_score, reverse=True)

    def _filter_by_relevance(self, keywords: List[KeywordResult], min_relevance: float) -> List[KeywordResult]:
        """
        Filter keywords by minimum relevance score.

        Args:
            keywords: List of keywords to filter.
            min_relevance: Minimum relevance score threshold.

        Returns:
            List[KeywordResult]: Filtered keywords.
        """
        return [k for k in keywords if k.relevance_score >= min_relevance]

    def get_result_statistics(self, keywords: List[KeywordResult]) -> Dict[str, Any]:
        """
        Get statistics about the formatted results.

        Args:
            keywords: List of formatted keywords.

        Returns:
            Dict[str, Any]: Result statistics.
        """
        if not keywords:
            return {
                "total_keywords": 0,
                "phrases": 0,
                "single_words": 0,
                "header_keywords": 0,
                "avg_relevance_score": 0.0,
                "min_relevance_score": 0.0,
                "max_relevance_score": 0.0,
            }

        phrases = [k for k in keywords if k.is_phrase]
        single_words = [k for k in keywords if not k.is_phrase]
        header_keywords = [k for k in keywords if k.from_header]

        relevance_scores: List[float] = [k.relevance_score for k in keywords]

        return {
            "total_keywords": len(keywords),
            "phrases": len(phrases),
            "single_words": len(single_words),
            "header_keywords": len(header_keywords),
            "avg_relevance_score": float(sum(relevance_scores) / len(relevance_scores)),
            "min_relevance_score": min(relevance_scores),
            "max_relevance_score": max(relevance_scores),
        }
