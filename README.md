# BookSpine & KTE

A comprehensive Python toolkit for calculating book spine dimensions and extracting keywords from book content.

This project provides two main tools:

-   **BookSpine**: A library and command-line tool for calculating book spine dimensions for various printing services.
-   **KTE (Keyword Theme Extraction)**: A library and command-line tool for extracting keywords and themes from book content using AI.

## Features

-   **Flexible Keyword Extraction**: The KTE module supports multiple keyword extraction backends:
    -   **Local**: Uses a local `sentence-transformers` model for keyword extraction.
    -   **Hugging Face API**: Offloads the extraction to the Hugging Face Inference API.
    -   **STAPI (Docker)**: Connects to a local Docker container running a sentence-transformer API.
-   **Configurable**: The extraction method can be easily configured using environment variables.

## Documentation

For detailed information on installation, usage, and development, please see our documentation in the `docs` directory.

-   **[Installation Instructions](docs/INSTALL.md)**
-   **[Developer Documentation](docs/developer/)**
-   **[TODO List](docs/TODO.md)**

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/developer/CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
