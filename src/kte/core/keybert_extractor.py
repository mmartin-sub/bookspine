"""
KeyBERT-based keyword extractor.

This module provides keyword extraction functionality using KeyBERT,
with support for various extraction strategies and configurations.
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple

from ..models.extraction_options import ExtractionOptions
from ..models.keyword_result import KeywordResult


class KeyBERTExtractor:
    """
    Core component for keyword extraction using KeyBERT.

    This class provides methods for extracting keywords and phrases from text
    using the KeyBERT algorithm, with support for various configuration options.
    """

    def __init__(self):
        """
        Initialize the KeyBERT extractor.
        """
        self._model: Optional[Any] = None
        self._initialized = False
        self._configure_huggingface()

    def _configure_huggingface(self):
        """
        Configure Hugging Face Hub settings to reduce rate limiting.
        """
        # Disable telemetry to reduce API calls
        os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

        # Disable implicit token to avoid unnecessary auth requests
        os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")

        # Set cache directory to local path
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        os.environ.setdefault("HF_HOME", cache_dir)

        # Check for Hugging Face API token for better rate limits
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token
        else:
            # Log warning about potential rate limiting
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "No HF_TOKEN found. For better rate limits, set HF_TOKEN environment variable. "
                "Get a free token at: https://huggingface.co/settings/tokens"
            )

        # Enable offline mode if models are cached
        if os.path.exists(cache_dir):
            os.environ.setdefault("HF_HUB_OFFLINE", "1")

    def extract_keywords(self, text: str, options: ExtractionOptions) -> List[KeywordResult]:
        """
        Extract keywords from text using KeyBERT.

        Args:
            text: Text content to extract keywords from.
            options: Extraction options and configuration.

        Returns:
            List[KeywordResult]: List of extracted keywords with metadata.

        Raises:
            ValueError: If text is empty or invalid.
            Exception: If KeyBERT extraction fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if len(text.strip()) < 10:
            raise ValueError("Text is too short for meaningful extraction")

        try:
            # Initialize model if needed
            if not self._initialized:
                self._initialize_model()

            # Extract keywords using KeyBERT
            raw_keywords = self._extract_with_keybert(text, options)

            # Convert to KeywordResult objects
            keyword_results = self._convert_to_keyword_results(raw_keywords, options)

            return keyword_results

        except Exception as e:
            raise Exception(f"KeyBERT extraction failed: {str(e)}")

    def _initialize_model(self):
        """
        Initialize the KeyBERT model.

        Raises:
            ImportError: If KeyBERT is not available.
        """
        try:
            from keybert import KeyBERT
            from sentence_transformers import SentenceTransformer

            # Use a lightweight model for faster processing
            model_name = "all-MiniLM-L6-v2"

            # Check if model is already loaded
            if self._model is not None:
                return

            # Initialize with caching and reduced verbosity
            sentence_model = SentenceTransformer(
                model_name,
                cache_folder=os.path.join(os.path.expanduser("~"), ".cache", "huggingface"),
                device="cpu",  # Use CPU for consistency
            )

            self._model = KeyBERT(model=sentence_model)
            self._initialized = True

        except ImportError:
            raise ImportError(
                "KeyBERT and sentence-transformers are required for keyword extraction. "
                "Install with: pip install keybert sentence-transformers"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize KeyBERT model: {str(e)}")

    def _extract_with_keybert(self, text: str, options: ExtractionOptions) -> List[Tuple[str, float]]:
        """
        Extract keywords using KeyBERT.

        Args:
            text: Text content to extract from.
            options: Extraction options.

        Returns:
            List[Tuple[str, float]]: List of (keyword, score) tuples.
        """
        # Configure extraction parameters
        top_k = min(options.max_keywords * 2, 50)  # Extract more than needed for filtering
        keyphrase_ngram_range = (1, 3)  # Extract 1-3 word phrases
        stop_words = "english"

        # Extract keywords
        if self._model is None:
            raise RuntimeError("KeyBERT model not initialized")

        keywords: List[Tuple[str, float]] = self._model.extract_keywords(
            text,
            keyphrase_ngram_range=keyphrase_ngram_range,
            stop_words=stop_words,
            top_n=top_k,
            diversity=0.7,  # Encourage diversity in results
        )

        return keywords

    def _convert_to_keyword_results(
        self, raw_keywords: List[Tuple[str, float]], options: ExtractionOptions
    ) -> List[KeywordResult]:
        """
        Convert raw keyword tuples to KeywordResult objects.

        Args:
            raw_keywords: List of (keyword, score) tuples.
            options: Extraction options.

        Returns:
            List[KeywordResult]: List of KeywordResult objects.
        """
        keyword_results = []

        for phrase, score in raw_keywords:
            # Clean the phrase
            cleaned_phrase = self._clean_phrase(phrase)

            # Skip empty phrases
            if not cleaned_phrase:
                continue

            # Determine if it's a phrase (multiple words)
            is_phrase = len(cleaned_phrase.split()) > 1

            # Create KeywordResult
            keyword_result = KeywordResult(
                phrase=cleaned_phrase,
                relevance_score=score,
                is_phrase=is_phrase,
                from_header=False,  # Will be set by HeaderWeighting if needed
            )

            keyword_results.append(keyword_result)

        return keyword_results

    def _filter_keywords(
        self, keywords: List[Tuple[str, float]], options: ExtractionOptions
    ) -> List[Tuple[str, float]]:
        """
        Filter keywords based on extraction options.

        Args:
            keywords: List of (keyword, score) tuples to filter.
            options: Extraction options for filtering.

        Returns:
            List[Tuple[str, float]]: Filtered keywords.
        """
        # Filter by minimum relevance score
        filtered = [(kw, score) for kw, score in keywords if score >= options.min_relevance]

        # Limit to maximum keywords
        return filtered[: options.max_keywords]

    def _clean_phrase(self, phrase: str) -> str:
        """
        Clean and normalize a phrase.

        Args:
            phrase: Raw phrase from KeyBERT.

        Returns:
            str: Cleaned phrase.
        """
        # Remove extra whitespace
        phrase = re.sub(r"\s+", " ", phrase.strip())

        # Remove special characters that might interfere
        phrase = re.sub(r"[^\w\s\-]", "", phrase)

        return phrase.strip()

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dict[str, Any]: Model information.
        """
        if not self._initialized:
            return {"initialized": False}

        return {
            "initialized": True,
            "model_type": "KeyBERT",
            "sentence_model": "all-MiniLM-L6-v2",
        }
