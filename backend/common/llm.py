from functools import lru_cache
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from .config import settings
from .logger import get_logger


logger = get_logger(__name__)


@lru_cache()
def get_chat_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> BaseLLM:
    """
    获取 DeepSeek 聊天 LLM 实例（使用 LangChain OpenAI 兼容接口）
    
    Args:
        model: 模型名称，默认为 settings.DEEPSEEK_CHAT_MODEL
        temperature: 温度参数，默认为 0.7
        max_tokens: 最大生成长度，默认为 None
    
    Returns:
        BaseLLM: LangChain 的 LLM 实例
    """
    model_name = model or settings.MODEL_NAME
    
    llm = ChatOpenAI(
        model=model_name,
        api_key=settings.MODEL_API_KEY,
        base_url=f"{settings.MODEL_BASE_URL}/v1",
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    logger.info(f"Initialized chat LLM (DeepSeek): {model_name}")
    return llm


@lru_cache()
def get_vision_llm(
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
) -> BaseLLM:
    """
    获取 Ollama 视觉 LLM 实例
    
    Args:
        model: 模型名称，默认为 settings.OLLAMA_VISION_MODEL
        temperature: 温度参数，默认为 0.2
        max_tokens: 最大生成长度，默认为 None
    
    Returns:
        BaseLLM: LangChain 的 LLM 实例
    """
    model_name = model or settings.OLLAMA_VISION_MODEL
    
    llm = OllamaLLM(
        base_url=settings.OLLAMA_HOST,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    logger.info(f"Initialized vision LLM (Ollama): {model_name}")
    return llm


@lru_cache()
def get_ollama_embeddings(
    model: str = "nomic-embed-text",
) -> Embeddings:
    """
    获取 Ollama Embeddings 实例
    
    Args:
        model: 模型名称，默认为 "nomic-embed-text"
    
    Returns:
        Embeddings: LangChain 的 Embeddings 实例
    """
    embeddings = OllamaEmbeddings(
        base_url=settings.OLLAMA_HOST,
        model=model,
    )
    
    logger.info(f"Initialized Ollama embeddings: {model}")
    return embeddings


# 快捷获取默认实例
chat_llm = get_chat_llm()
vision_llm = get_vision_llm()

