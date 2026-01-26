from typing import Generator, Tuple, Any
from rich.console import Console

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
