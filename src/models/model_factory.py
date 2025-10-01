"""Model factory for creating language model instances."""

import config
from src.interfaces.language_model import ILanguageModel


def create_model(
    provider: str | None = None,
    model_id: str | None = None,
    **kwargs,
) -> ILanguageModel:
    """
    Create a language model instance based on provider.

    Args:
        provider: Provider name ("local", "bedrock", "genai")
        model_id: Model ID (provider-specific)
        **kwargs: Additional model parameters

    Returns:
        ILanguageModel instance

    Raises:
        ValueError: If provider is invalid or dependencies are missing
    """
    provider = provider or config.MODEL_PROVIDER

    if provider == "local":
        from src.models.huggingface_model import HuggingFaceModel

        model_name = model_id or config.MODEL_NAME
        return HuggingFaceModel(model_name=model_name, **kwargs)

    elif provider == "bedrock":
        try:
            from src.models.bedrock_model import BedrockModel

            return BedrockModel(model_id=model_id, **kwargs)
        except ImportError as e:
            msg = "AWS Bedrock dependencies not installed. Install with: pip install boto3 botocore"
            raise ValueError(msg) from e

    elif provider == "genai":
        try:
            from src.models.genai_model import GenAIModel

            return GenAIModel(model_name=model_id, **kwargs)
        except ImportError as e:
            msg = (
                "Google GenAI dependencies not installed. "
                "Install with: pip install google-generativeai"
            )
            raise ValueError(msg) from e

    else:
        msg = f"Unknown provider: {provider}. Valid options: local, bedrock, genai"
        raise ValueError(msg)


def parse_provider_from_arg(arg: str) -> tuple[str, str | None]:
    """
    Parse provider and model from command line argument.

    Args:
        arg: Command line argument (e.g., "-bedrock", "-genai model-name")

    Returns:
        Tuple of (provider, model_id)

    Examples:
        "-local" -> ("local", None)
        "-bedrock" -> ("bedrock", None)
        "-bedrock us.anthropic.claude-sonnet-4-v1:0" -> ("bedrock", "us.anthropic...")
        "-genai gemini-2.5-pro" -> ("genai", "gemini-2.5-pro")
    """
    arg = arg.strip()

    if arg.startswith("-"):
        arg = arg[1:]

    parts = arg.split(None, 1)
    provider = parts[0].lower()

    if provider not in ["local", "bedrock", "genai"]:
        msg = f"Invalid provider: {provider}. Valid options: local, bedrock, genai"
        raise ValueError(msg)

    model_id = parts[1] if len(parts) > 1 else None

    return provider, model_id
