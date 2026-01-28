import os
from typing import Generator, Tuple, Any, Optional, Dict
from rich.console import Console

def load_config(console: Console) -> Optional[Dict[str, Any]]:
    """
    Loads API configuration from environment variables and validates them.
    
    :param console: The Rich console instance for printing errors.
    :return: A dictionary containing config items if valid, otherwise None.
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

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "stream": True # 默认启用流式输出
    }
