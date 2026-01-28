import os
from typing import Generator, Tuple, Any, Optional
from rich.console import Console

def load_config(console: Console) -> Optional[Tuple[str, str, str]]:
    """
    Loads API configuration from environment variables and validates them.
    
    :param console: The Rich console instance for printing errors.
    :return: A tuple of (api_key, base_url, model) if valid, otherwise None.
    """
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("API_BASE_URL")
    model = os.getenv("MODEL_NAME", "gpt-3.5-turbo") # Default value if not set

    if not api_key:
        console.print("[bold red]Error:[/bold red] API_KEY not found in environment variables.")
        console.print("Please create a .env file with your API credentials.")
        return None

    if not base_url:
        console.print("[bold red]Error:[/bold red] API_BASE_URL not found in environment variables.")
        console.print("Please create a .env file with your API credentials.")
        return None

    return api_key, base_url, model

def stream_with_spinner(generator: Generator[str, None, None], console: Console) -> Tuple[str, Generator[str, None, None]]:
    """
    Handles the initial waiting period with a spinner, then returns the first chunk 
    and the generator for the rest of the stream.
    
    :param generator: The response generator from the API client.
    :param console: The Rich console instance to display the spinner.
    :return: A tuple containing (first_chunk_content, remaining_generator).
    """
    first_chunk = ""
    # 1. Start Spinner waiting for the first character
    # 1. 启动 Spinner 等待第一个字符
    with console.status("[bold green]Thinking...", spinner="simpleDots"):
        try:
            # Try to get the first chunk. This step blocks until the server returns the first byte.
            # 尝试获取第一个 chunk，这一步会阻塞直到服务器返回第一个字
            first_chunk = next(generator)
        except StopIteration:
            # Handle empty response (generator finished immediately)
            # 处理空响应的情况（生成器立即结束）
            first_chunk = ""
            
    return first_chunk, generator
