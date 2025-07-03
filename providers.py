"""
LLM Provider functionality for Git Commit Generator
"""

import logging
import requests
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any

logger = logging.getLogger("git-commit-generator")


class ProviderType(Enum):
    OLLAMA = "ollama"
    LM_STUDIO = "lm-studio"


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using the LLM provider"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get available models from the provider"""
        pass


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            return data.get("response", "")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error with Ollama API: {e}")
            return f"Error: Could not generate with Ollama: {str(e)}"

    def get_available_models(self) -> List[str]:
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return [model.get("name") for model in data.get("models", [])]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Ollama models: {e}")
            return []


class LMStudioProvider(BaseLLMProvider):
    def __init__(
        self, base_url: str = "http://localhost:1234/v1", model: str = "default"
    ):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            url = f"{self.base_url}/completions"
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            choices = data.get("choices", [])
            if choices and len(choices) > 0:
                return choices[0].get("text", "")
            return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"Error with LM-Studio API: {e}")
            return f"Error: Could not generate with LM-Studio: {str(e)}"

    def get_available_models(self) -> List[str]:
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return [model.get("id") for model in data.get("data", [])]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LM-Studio models: {e}")
            return []


def create_provider(
    provider_type: ProviderType, base_url: str, model: str
) -> BaseLLMProvider:
    """Factory function to create the appropriate provider instance"""
    if provider_type == ProviderType.OLLAMA:
        return OllamaProvider(base_url, model)
    elif provider_type == ProviderType.LM_STUDIO:
        return LMStudioProvider(base_url, model)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
