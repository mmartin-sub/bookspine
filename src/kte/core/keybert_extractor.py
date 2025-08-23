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
from .universal_embedder import UniversalEmbedder


class KeyBERTExtractor:
    """
    Core component for keyword extraction using KeyBERT.

    This class provides methods for extracting keywords and phrases from text
    using the KeyBERT algorithm, with support for various configuration options.
    """

    def __init__(
        self, engine: str, api_url: str, auth_token: Optional[str] = None, model_name: Optional[str] = "default"
    ):
        """
        Initialize the KeyBERT extractor.

        Args:
            engine: The inference engine to use ('huggingface', 'stapi', 'infinity', or 'local').
            api_url: The URL of the inference API.
            auth_token: The authentication token for the API.
            model_name: The name of the model to use.
        """
        self._model: Optional[Any] = None
        self._initialized = False
        self.engine = engine
        self.api_url = api_url
        self.auth_token = auth_token
        self.model_name = model_name

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

            if self.engine == "local":
                from sentence_transformers import SentenceTransformer

                embedder = SentenceTransformer(self.model_name)
            else:
                embedder = UniversalEmbedder(
                    engine=self.engine,
                    api_url=self.api_url,
                    auth_token=self.auth_token,
                    model_name=self.model_name,
                )

            self._model = KeyBERT(model=embedder)
            self._initialized = True

        except ImportError:
            if self.engine == "local":
                raise ImportError(
                    "KeyBERT and sentence-transformers are required for the 'local' extraction method. "
                    "Install with: pip install '.[local-models]'"
                )
            else:
                raise ImportError("KeyBERT is required for keyword extraction. Install with: pip install keybert")
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
