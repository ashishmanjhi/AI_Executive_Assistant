"""
LLM Configuration and Provider Management

Supports multiple LLM providers:
- Ollama (local)
- OpenAI (GPT-3.5, GPT-4)
- Anthropic Claude (Claude-3)
- Hugging Face (various models)

Features:
- Easy provider switching via .env
- Cost tracking per request
- Automatic fallback
- Token usage monitoring
"""

import os
from typing import Any, Optional
from enum import Enum
import logging

from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv

# Import providers conditionally
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ChatOllama = None

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

try:
    from langchain_huggingface import HuggingFaceEndpoint
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    HuggingFaceEndpoint = None

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"


class LLMConfig:
    """
    LLM Configuration Manager
    
    Handles provider selection, model configuration, and cost tracking.
    """
    
    # Pricing per 1M tokens (input/output) - Update as needed
    PRICING = {
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "ollama": {"input": 0.00, "output": 0.00},  # Local, free
        "huggingface": {"input": 0.00, "output": 0.00},  # Varies by model
    }
    
    def __init__(self):
        self.provider = self._get_provider()
        self.model_name = self._get_model_name()
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def _get_provider(self) -> LLMProvider:
        """Get LLM provider from environment"""
        provider_str = os.getenv("LLM_PROVIDER", "ollama").lower()
        try:
            return LLMProvider(provider_str)
        except ValueError:
            logger.warning(f"Invalid LLM_PROVIDER '{provider_str}', defaulting to ollama")
            return LLMProvider.OLLAMA
    
    def _get_model_name(self) -> str:
        """Get model name based on provider"""
        if self.provider == LLMProvider.OLLAMA:
            return os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        elif self.provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == LLMProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        elif self.provider == LLMProvider.HUGGINGFACE:
            return os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        return "llama3.2:latest"
    
    def create_llm(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
        **kwargs
    ) -> BaseChatModel:
        """
        Create LLM instance based on configured provider.
        
        Args:
            temperature: Override default temperature
            max_tokens: Override default max tokens
            streaming: Enable streaming responses
            **kwargs: Additional provider-specific arguments
        
        Returns:
            Configured LLM instance
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            if self.provider == LLMProvider.OLLAMA:
                return self._create_ollama_llm(temp, max_tok, streaming, **kwargs)
            elif self.provider == LLMProvider.OPENAI:
                return self._create_openai_llm(temp, max_tok, streaming, **kwargs)
            elif self.provider == LLMProvider.ANTHROPIC:
                return self._create_anthropic_llm(temp, max_tok, streaming, **kwargs)
            elif self.provider == LLMProvider.HUGGINGFACE:
                # HuggingFaceEndpoint is not a BaseChatModel, cast for type compatibility
                return self._create_huggingface_llm(temp, max_tok, streaming, **kwargs)  # type: ignore
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error creating LLM for provider {self.provider}: {e}")
            # Fallback to Ollama if available
            if self.provider != LLMProvider.OLLAMA:
                logger.info("Falling back to Ollama")
                return self._create_ollama_llm(temp, max_tok, streaming)
            raise
    
    def _create_ollama_llm(
        self,
        temperature: float,
        max_tokens: int,
        streaming: bool,
        **kwargs
    ):
        """Create Ollama LLM instance"""
        if not OLLAMA_AVAILABLE or ChatOllama is None:
            raise ImportError("langchain-ollama not installed. Install with: pip install langchain-ollama")
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Note: ChatOllama doesn't support streaming parameter in constructor
        # Streaming is controlled at invocation time via .stream() method
        return ChatOllama(
            model=self.model_name,
            base_url=base_url,
            temperature=temperature,
            num_predict=max_tokens,
            **kwargs
        )
    
    def _create_openai_llm(
        self,
        temperature: float,
        max_tokens: int,
        streaming: bool,
        **kwargs
    ):
        """Create OpenAI LLM instance"""
        if not OPENAI_AVAILABLE or ChatOpenAI is None:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai tiktoken")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        # Note: Streaming is controlled at invocation time, not in constructor
        # API key will be picked up from OPENAI_API_KEY environment variable
        return ChatOpenAI(
            model=self.model_name,
            temperature=temperature,
            **kwargs
        )
    
    def _create_anthropic_llm(
        self,
        temperature: float,
        max_tokens: int,
        streaming: bool,
        **kwargs
    ):
        """Create Anthropic Claude LLM instance"""
        if not ANTHROPIC_AVAILABLE or ChatAnthropic is None:
            raise ImportError("langchain-anthropic not installed. Install with: pip install langchain-anthropic")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        # Note: Streaming is controlled at invocation time, not in constructor
        # API key will be picked up from ANTHROPIC_API_KEY environment variable
        return ChatAnthropic(
            model_name=self.model_name,
            temperature=temperature,
            max_tokens_to_sample=max_tokens,
            **kwargs
        )
    
    def _create_huggingface_llm(
        self,
        temperature: float,
        max_tokens: int,
        streaming: bool,
        **kwargs
    ):
        """Create Hugging Face LLM instance"""
        if not HUGGINGFACE_AVAILABLE or HuggingFaceEndpoint is None:
            raise ImportError("langchain-huggingface not installed. Install with: pip install langchain-huggingface")
        
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found in environment")
        
        # Note: HuggingFaceEndpoint doesn't support streaming parameter in constructor
        # Streaming is controlled at invocation time
        return HuggingFaceEndpoint(
            repo_id=self.model_name,
            huggingfacehub_api_token=api_key,
            temperature=temperature,
            max_new_tokens=max_tokens,
            **kwargs
        )
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_name: Optional[str] = None
    ) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_name: Model name (uses configured model if not provided)
        
        Returns:
            Cost in USD
        """
        model = model_name or self.model_name
        
        # Get pricing for model
        pricing = None
        for key in self.PRICING:
            if key in model.lower():
                pricing = self.PRICING[key]
                break
        
        if not pricing:
            # Default to free for unknown models
            pricing = {"input": 0.00, "output": 0.00}
        
        # Calculate cost (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Update totals
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total_cost
        
        return total_cost
    
    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics"""
        return {
            "provider": self.provider.value,
            "model": self.model_name,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "average_cost_per_request": round(
                self.total_cost / max(1, self.total_input_tokens + self.total_output_tokens) * 1000,
                6
            )
        }
    
    def reset_stats(self):
        """Reset usage statistics"""
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def get_info(self) -> dict[str, Any]:
        """Get configuration information"""
        return {
            "provider": self.provider.value,
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "cost_tracking": True,
            "pricing_available": self.model_name in self.PRICING or any(
                key in self.model_name.lower() for key in self.PRICING
            )
        }


# Global LLM configuration instance
_llm_config: Optional[LLMConfig] = None


def get_llm_config() -> LLMConfig:
    """Get global LLM configuration instance"""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config


def create_llm(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
    **kwargs
) -> BaseChatModel:
    """
    Convenience function to create LLM with global config.
    
    Args:
        temperature: Override default temperature
        max_tokens: Override default max tokens
        streaming: Enable streaming responses
        **kwargs: Additional provider-specific arguments
    
    Returns:
        Configured LLM instance
    """
    config = get_llm_config()
    return config.create_llm(temperature, max_tokens, streaming, **kwargs)


def track_usage(response: Any) -> float:
    """
    Track token usage and cost from LLM response.
    
    Args:
        response: LLM response object
    
    Returns:
        Cost in USD
    """
    config = get_llm_config()
    
    # Extract token usage from response
    input_tokens = 0
    output_tokens = 0
    
    if hasattr(response, "usage_metadata"):
        usage = response.usage_metadata
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
    elif hasattr(response, "response_metadata"):
        metadata = response.response_metadata
        if "token_usage" in metadata:
            usage = metadata["token_usage"]
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
    
    if input_tokens > 0 or output_tokens > 0:
        cost = config.calculate_cost(input_tokens, output_tokens)
        logger.info(
            f"Token usage - Input: {input_tokens}, Output: {output_tokens}, Cost: ${cost:.6f}"
        )
        return cost
    
    return 0.0


def get_usage_stats() -> dict[str, Any]:
    """Get usage statistics from global config"""
    config = get_llm_config()
    return config.get_usage_stats()


def reset_usage_stats():
    """Reset usage statistics in global config"""
    config = get_llm_config()
    config.reset_stats()


def get_llm_info() -> dict[str, Any]:
    """Get LLM configuration information"""
    config = get_llm_config()
    return config.get_info()


# Made with Bob