from typing import Any, Dict, List, Literal, Optional

import numpy as np
import requests
from keybert.backend import BaseEmbedder

EngineType = Literal["huggingface", "stapi", "infinity"]


class UniversalEmbedder(BaseEmbedder):
    """
    A single, universal backend that can connect to multiple inference engines.
    """

    def __init__(
        self, engine: EngineType, api_url: str, auth_token: Optional[str] = None, model_name: Optional[str] = "default"
    ):
        super().__init__()
        self.engine = engine
        self.api_url = api_url
        self.auth_token = auth_token
        self.model_name = model_name

    def embed(self, documents: List[str], verbose: bool = False) -> np.ndarray:
        headers: Dict[str, str] = {}
        payload: Dict[str, Any] = {}

        # 1. Configure request based on the engine
        if self.engine == "huggingface":
            if not self.auth_token:
                raise ValueError("`auth_token` is required for Hugging Face engine.")
            headers["Authorization"] = f"Bearer {self.auth_token}"
            payload = {"inputs": documents, "options": {"wait_for_model": True}}

        elif self.engine == "stapi":
            # OpenAI-compatible format
            payload = {"input": documents, "model": self.model_name}

        elif self.engine == "infinity":
            payload = {"input": documents}

        else:
            raise ValueError(f"Unknown engine type: {self.engine}")

        # 2. Make the request
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_data = response.json()

        # 3. Parse the response based on the engine
        if self.engine == "huggingface":
            # Direct list of embeddings
            embeddings = response_data

        elif self.engine in ["stapi", "infinity"]:
            # Nested embedding data
            embeddings = [item["embedding"] for item in response_data["data"]]

        return np.array(embeddings)
