# Keyword Extraction Configuration

The Keyword Theme Extraction (KTE) module is designed to be flexible, allowing you to choose from several backends for sentence embedding. This document explains how to configure the extraction method to suit your needs.

## Extraction Engines

You can choose from four different extraction engines:

-   `local`: Uses a local `sentence-transformers` model. This requires installing the `local-models` extra.
-   `huggingface`: Uses the Hugging Face Inference API for remote inference.
-   `stapi`: Connects to a local Docker container running the `stapi` server.
-   `infinity`: Connects to a local Docker container running the `infinity` server.

## Configuration

The extraction engine is configured using environment variables.

### `KTE_ENGINE`

This environment variable determines which extraction engine to use.

-   **`local` (default):**
    ```bash
    export KTE_ENGINE=local
    ```
    You must have the `local-models` extra installed: `pip install "bookspine[local-models]"`

-   **`huggingface`:**
    ```bash
    export KTE_ENGINE=huggingface
    export KTE_API_URL="https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    export KTE_AUTH_TOKEN="YOUR_HUGGING_FACE_API_TOKEN"
    ```

-   **`stapi`:**
    ```bash
    export KTE_ENGINE=stapi
    export KTE_API_URL="http://localhost:8000/v1/embeddings"
    ```

-   **`infinity`:**
    ```bash
    export KTE_ENGINE=infinity
    export KTE_API_URL="http://localhost:7997/embeddings"
    ```

### `KTE_MODEL_NAME`

This environment variable specifies the name of the sentence-transformer model to use. The default is `sentence-transformers/all-MiniLM-L6-v2`.

```bash
export KTE_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
```

## Running Local Inference Servers

If you want to use the `stapi` or `infinity` engines, you need to run their Docker containers locally.

### STAPI

Run the `stapi` Docker container with the following command:

```bash
docker run -d -p 8000:8000 \
  -e MODEL="sentence-transformers/all-MiniLM-L6-v2" \
  ghcr.io/substratusai/stapi
```

### Infinity

Run the `infinity` Docker container with the following command:

```bash
docker run -d -p 7997:7997 \
  -e MODEL_NAME_OR_PATH="sentence-transformers/all-MiniLM-L6-v2" \
  michaelfeil/infinity
```
