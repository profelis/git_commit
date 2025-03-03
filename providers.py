"""
LLM Provider functionality for Git Commit Generator
"""

import logging
import requests
from enum import Enum
from typing import List, Dict, Optional

logger = logging.getLogger('git-commit-generator')

class LLMProvider(Enum):
    OLLAMA = "ollama"
    LM_STUDIO = "lm-studio"

def generate_with_ollama(base_url: str, model: str, prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Generate text using Ollama API.
    
    Args:
        base_url: Base URL for Ollama API
        model: Model name to use
        prompt: The prompt to send to Ollama
        max_tokens: Maximum number of tokens to generate
        temperature: Temperature parameter for generation
        
    Returns:
        Generated text response
    """
    try:
        url = f"{base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error with Ollama API: {e}")
        return f"Error: Could not generate with Ollama: {str(e)}"

def generate_with_lm_studio(base_url: str, model: str, prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Generate text using LM-Studio API.
    
    Args:
        base_url: Base URL for LM-Studio API
        model: Model name to use
        prompt: The prompt to send to LM-Studio
        max_tokens: Maximum number of tokens to generate
        temperature: Temperature parameter for generation
        
    Returns:
        Generated text response
    """
    try:
        url = f"{base_url}/completions"
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
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

def get_available_ollama_models(base_url: str) -> List[str]:
    """
    Get a list of available models from Ollama
    
    Args:
        base_url: Base URL for Ollama API
    
    Returns:
        List of model names or empty list if failed
    """
    try:
        url = f"{base_url}/api/tags"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        models = [model.get("name") for model in data.get("models", [])]
        return models
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Ollama models: {e}")
        return []

def get_available_lm_studio_models(base_url: str) -> List[str]:
    """
    Get a list of available models from LM-Studio
    
    Args:
        base_url: Base URL for LM-Studio API
    
    Returns:
        List of model names or empty list if failed
    """
    try:
        url = f"{base_url}/models"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        models = [model.get("id") for model in data.get("data", [])]
        return models
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching LM-Studio models: {e}")
        return []
