"""Abstract interface for language models."""

from abc import ABC, abstractmethod


class ILanguageModel(ABC):
    """Abstract interface for language model implementations."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Generate text based on the given prompt.

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response
        """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the model and load necessary resources."""

    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if the model is initialized and ready to use."""
