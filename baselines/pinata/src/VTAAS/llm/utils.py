from baselines.pinata.src.VTAAS.llm.llm_client import LLMClient
from baselines.pinata.src.VTAAS.llm.openai_client import OpenAILLMClient


def create_llm_client(
    name: str,
    start_time: float,
    output_folder: str,
    model_name: str,
) -> LLMClient:
    """Instantiates the LLM client."""
    return OpenAILLMClient(name, start_time, output_folder, model=model_name)
