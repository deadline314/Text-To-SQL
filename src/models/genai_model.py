"""Google GenAI (Gemini) model implementation using new SDK."""

from collections.abc import Generator

import config
from src.interfaces.language_model import ILanguageModel

try:
    from google import genai
    from google.genai import types

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GenAIModel(ILanguageModel):
    """Google GenAI (Gemini) model implementation using new google-genai SDK."""

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ):
        """
        Initialize GenAI model.

        Args:
            model_name: Model name (e.g., "gemini-2.5-flash")
            api_key: Google API key
            temperature: Generation temperature
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
        """
        if not GENAI_AVAILABLE:
            msg = "google-genai is not installed. Install with: pip install google-genai"
            raise ImportError(msg)

        self.model_name = model_name or config.GENAI_MODEL_NAME
        self.api_key = api_key or config.GOOGLE_API_KEY
        self.temperature = temperature or config.MODEL_TEMPERATURE
        self.top_p = top_p or config.MODEL_TOP_P
        self.max_tokens = max_tokens or config.MODEL_MAX_TOKENS

        if not self.api_key:
            msg = "Google API key is required. Set GCP_API_KEY in .env or pass api_key parameter."
            raise ValueError(msg)

        self._initialized = False
        self.client = None

    def initialize(self) -> None:
        """Initialize GenAI client."""
        if self._initialized:
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            self._initialized = True

            print(f"✓ GenAI 模型已初始化: {self.model_name}")

        except Exception as e:
            msg = f"Failed to initialize GenAI model: {e}"
            raise RuntimeError(msg) from e

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        """
        Generate text using GenAI model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            Generated text
        """
        if not self._initialized:
            self.initialize()

        max_tokens = max_tokens or self.max_tokens

        try:
            # 使用新版 SDK 的生成方式
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_output_tokens=max_tokens,
                ),
            )

            return response.text

        except Exception as e:
            msg = f"GenAI generation failed: {e}"
            raise RuntimeError(msg) from e

    def generate_stream(
        self, prompt: str, max_tokens: int | None = None
    ) -> Generator[str, None, None]:
        """
        Generate text using GenAI with streaming.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Yields:
            Generated text tokens
        """
        if not self._initialized:
            self.initialize()

        max_tokens = max_tokens or self.max_tokens

        try:
            # 使用新版 SDK 的串流生成
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_output_tokens=max_tokens,
                ),
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            msg = f"GenAI streaming failed: {e}"
            raise RuntimeError(msg) from e

    def is_initialized(self) -> bool:
        """Check if model is initialized."""
        return self._initialized

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.client = None
        self._initialized = False
