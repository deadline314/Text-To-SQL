"""Tests for language model implementations."""

from unittest.mock import MagicMock, patch

from src.models.huggingface_model import HuggingFaceModel


def test_model_initialization():
    model = HuggingFaceModel(model_name="test-model", device="cpu")

    assert model.model_name == "test-model"
    assert model.device == "cpu"
    assert model.is_initialized() is False


@patch("src.models.huggingface_model.AutoTokenizer")
@patch("src.models.huggingface_model.AutoModelForCausalLM")
@patch("src.models.huggingface_model.pipeline")
def test_initialize_loads_model(mock_pipeline, mock_model_cls, mock_tokenizer_cls):
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_pipe = MagicMock()

    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
    mock_model_cls.from_pretrained.return_value = mock_model
    mock_pipeline.return_value = mock_pipe

    model = HuggingFaceModel(model_name="test-model")
    model.initialize()

    assert model.is_initialized() is True
    mock_tokenizer_cls.from_pretrained.assert_called_once_with("test-model")
    mock_model_cls.from_pretrained.assert_called_once()


@patch("src.models.huggingface_model.AutoTokenizer")
@patch("src.models.huggingface_model.AutoModelForCausalLM")
@patch("src.models.huggingface_model.pipeline")
def test_generate_text(mock_pipeline, mock_model_cls, mock_tokenizer_cls):
    mock_pipe = MagicMock()
    mock_pipe.return_value = [
        {
            "generated_text": [
                {"role": "user"},
                {"role": "assistant", "content": "SELECT * FROM users;"},
            ]
        }
    ]

    mock_pipeline.return_value = mock_pipe
    mock_tokenizer_cls.from_pretrained.return_value = MagicMock()
    mock_model_cls.from_pretrained.return_value = MagicMock()

    model = HuggingFaceModel()
    result = model.generate("test prompt")

    assert result == "SELECT * FROM users;"
    assert mock_pipe.called
