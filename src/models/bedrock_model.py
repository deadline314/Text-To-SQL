"""AWS Bedrock Claude model implementation."""

from collections.abc import Generator

import config
from src.interfaces.language_model import ILanguageModel

try:
    import boto3
    from botocore.config import Config as BotoConfig

    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False


class BedrockModel(ILanguageModel):
    """AWS Bedrock Claude model implementation."""

    def __init__(
        self,
        model_id: str | None = None,
        region: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ):
        """
        Initialize Bedrock model.

        Args:
            model_id: Bedrock model ID (e.g., "anthropic.claude-sonnet-4-v1")
            region: AWS region
            temperature: Generation temperature
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
        """
        if not BEDROCK_AVAILABLE:
            msg = "boto3 is not installed. Install with: pip install boto3 botocore"
            raise ImportError(msg)

        self.model_id = model_id or config.BEDROCK_MODEL_ID
        self.region = region or config.BEDROCK_REGION
        self.temperature = temperature or config.MODEL_TEMPERATURE
        self.top_p = top_p or config.MODEL_TOP_P
        self.max_tokens = max_tokens or config.MODEL_MAX_TOKENS
        self.aws_access_key_id = aws_access_key_id or config.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = aws_secret_access_key or config.AWS_SECRET_ACCESS_KEY

        self._initialized = False
        self.client = None

    def initialize(self) -> None:
        """Initialize Bedrock client."""
        if self._initialized:
            return

        try:
            session_kwargs = {}
            if self.aws_access_key_id and self.aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = self.aws_access_key_id
                session_kwargs["aws_secret_access_key"] = self.aws_secret_access_key

            session = boto3.Session(**session_kwargs)

            boto_config = BotoConfig(
                region_name=self.region,
                read_timeout=config.REQUEST_TIMEOUT,
                connect_timeout=config.REQUEST_TIMEOUT,
            )

            self.client = session.client("bedrock-runtime", config=boto_config)
            self._initialized = True

            print(f"✓ Bedrock 模型已初始化: {self.model_id}")
            print(f"  區域: {self.region}")

        except Exception as e:
            msg = f"Failed to initialize Bedrock client: {e}"
            raise RuntimeError(msg) from e

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        """
        Generate text using Bedrock Claude model.

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
            import json

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "messages": [{"role": "user", "content": prompt}],
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
            )

            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"]

        except Exception as e:
            msg = f"Bedrock generation failed: {e}"
            raise RuntimeError(msg) from e

    def generate_stream(
        self, prompt: str, max_tokens: int | None = None
    ) -> Generator[str, None, None]:
        """
        Generate text using Bedrock with streaming.

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
            import json

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "messages": [{"role": "user", "content": prompt}],
            }

            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body),
            )

            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])

                if chunk["type"] == "content_block_delta":
                    if chunk["delta"]["type"] == "text_delta":
                        yield chunk["delta"]["text"]

        except Exception as e:
            msg = f"Bedrock streaming failed: {e}"
            raise RuntimeError(msg) from e

    def is_initialized(self) -> bool:
        """Check if model is initialized."""
        return self._initialized

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.client = None
        self._initialized = False
