"""HuggingFace model implementation for Text-to-SQL."""

from collections.abc import Generator

from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, pipeline

import config
from src.interfaces.language_model import ILanguageModel

# 從 config.py 讀取預設值
DEFAULT_MODEL_NAME = config.MODEL_NAME
DEFAULT_MAX_TOKENS = config.MODEL_MAX_TOKENS
DEFAULT_TEMPERATURE = config.MODEL_TEMPERATURE
DEFAULT_TOP_P = config.MODEL_TOP_P
DEFAULT_DEVICE = config.MODEL_DEVICE


class HuggingFaceModel(ILanguageModel):
    """HuggingFace model implementation using transformers library."""

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ):
        """
        Initialize HuggingFace model.

        Args:
            model_name: Name of the model to use (default: from config.py)
            device: Device to run the model on (default: from config.py)
            temperature: Sampling temperature for generation (default: from config.py)
            top_p: Top-p sampling parameter (default: from config.py)
        """
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.device = device or DEFAULT_DEVICE
        self.temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
        self.top_p = top_p if top_p is not None else DEFAULT_TOP_P
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the model and tokenizer."""
        if self._initialized:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, torch_dtype="auto", device_map="auto"
        )

        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )

        self._initialized = True

    def is_initialized(self) -> bool:
        """Check if model is initialized."""
        return self._initialized

    def generate(self, prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """
        Generate text using the model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if not self._initialized:
            self.initialize()

        messages = [{"role": "user", "content": prompt}]

        # Use safe temperature (>0) to avoid numerical issues
        safe_temperature = max(self.temperature, 0.1)

        outputs = self.pipeline(
            messages,
            max_new_tokens=max_tokens,
            temperature=safe_temperature,
            top_p=self.top_p,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated_text = outputs[0]["generated_text"][-1]["content"]
        return generated_text.strip()

    def generate_stream(
        self, prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS
    ) -> Generator[str, None, None]:
        """
        Generate text using the model with streaming output.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Yields:
            Generated text tokens
        """
        if not self._initialized:
            self.initialize()

        messages = [{"role": "user", "content": prompt}]
        prompt_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt_text, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        from threading import Thread

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

        # Use safe temperature (>0) to avoid numerical issues
        safe_temperature = max(self.temperature, 0.1)

        generation_kwargs = {
            **inputs,
            "max_new_tokens": max_tokens,
            "temperature": safe_temperature,
            "top_p": self.top_p,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer,
        }

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        yield from streamer

        thread.join()
