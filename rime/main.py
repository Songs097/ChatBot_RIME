import click
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rime.client import AIClient

# Load environment variables from .env file
# 加载 .env 文件中的环境变量，方便本地开发和配置
load_dotenv()

# 初始化 Rich 控制台，用于美化输出
console = Console()

@click.group()
def cli():
    """Rime - Your Personal Local AI Chatbot"""
    pass

@cli.command()
def chat():
    """Start a chat session with Rime."""
    # Welcome Banner
    console.print(r"""[bold cyan]
      ___                        ___           ___     
     /  /\           ___        /  /\         /  /\    
    /  /::\         /__/\      /  /::|       /  /::\   
   /  /:/\:\        \__\:\    /  /:|:|      /  /:/\:\  
  /  /::\ \:\       /  /::\  /  /:/|:|__   /  /::\ \:\ 
 /__/:/\:\_\:\   __/  /:/\/ /__/:/_|::::\ /__/:/\:\ \:\
 \__\/~|::\/:/  /__/\/:/~~  \__\/  /~~/:/ \  \:\ \:\_\/
    |  |:|::/   \  \::/           /  /:/   \  \:\ \:\  
    |  |:|\/     \  \:\          /  /:/     \  \:\_\/  
    |__|:|~       \__\/         /__/:/       \  \:\    
     \__\|                      \__\/         \__\/    
[/bold cyan]""")
    console.print("[dim]Your Personal Local AI Chatbot[/dim]\n")

    # 从环境变量获取配置信息
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("API_BASE_URL")
    model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    # 检查必要的配置是否存在
    if not api_key:
        console.print("[bold red]Error:[/bold red] API_KEY not found in environment variables.")
        console.print("Please create a .env file with your API credentials.")
        return

    if not base_url:
        console.print("[bold red]Error:[/bold red] API_BASE_URL not found in environment variables.")
        console.print("Please create a .env file with your API credentials.")
        return

    # 初始化 API 客户端
    client = AIClient(api_key, base_url, model)
    
    console.print(f"[bold green]Rime (Model: {model})[/bold green] is ready! Type 'exit' or 'quit' to end.")
    console.print("-" * 50)

    # 保存对话历史
    messages = []
    # Optional: Add system prompt
    # messages.append({"role": "system", "content": "You are Rime, a helpful AI assistant."})

    # 主循环：处理用户输入和 AI 回复
    while True:
        try:
            # 获取用户输入
            user_input = console.input("[bold blue]You > [/bold blue]")
            # 检查退出命令
            if user_input.lower() in ('exit', 'quit'):
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            # 忽略空输入
            if not user_input.strip():
                continue

            # 将用户消息加入历史记录
            messages.append({"role": "user", "content": user_input})

            # Stream response
            response_content = ""
            # 使用 Rich 的 Live 组件显示实时更新的 Markdown
            with Live(Markdown(""), refresh_per_second=10) as live:
                console.print("[bold green]Rime > [/bold green]", end="")
                # 从客户端获取流式响应
                for chunk in client.chat_completion(messages):
                    response_content += chunk
                    # 实时更新显示内容
                    live.update(Markdown(response_content))
            
            console.print() # Newline after response
            # 将 AI 的完整回复加入历史记录，保持上下文
            messages.append({"role": "assistant", "content": response_content})

        except KeyboardInterrupt:
            # 处理 Ctrl+C 中断
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            # 捕获并显示其他错误
            console.print(f"\n[bold red]An error occurred:[/bold red] {e}")

@cli.command()
@click.option('--key', prompt='API Key', help='Your API Key')
@click.option('--url', prompt='API Base URL', help='API Base URL')
@click.option('--model', prompt='Model Name', default='gpt-3.5-turbo', help='Model Name')
def config(key, url, model):
    """Configure API credentials."""
    # 将用户输入的配置写入 .env 文件
    env_content = f"API_KEY={key}\nAPI_BASE_URL={url}\nMODEL_NAME={model}\n"
    with open('.env', 'w') as f:
        f.write(env_content)
    console.print("[green]Configuration saved to .env file![/green]")

if __name__ == '__main__':
    cli()
