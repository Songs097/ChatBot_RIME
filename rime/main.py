import click
import os
import random
import threading
import webbrowser
import time
from dotenv import load_dotenv
from rich.console import Console, Group
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rime.client import AIClient
from rime.banners import BANNERS
from rime.utils import load_config

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
    # Welcome Banner - Random Selection
    # 从 banners 列表中随机选择一个并打印
    console.print(random.choice(BANNERS))

    # 加载并验证配置
    client_config = load_config(console)
    if not client_config:
        return

    console.print(f"[bold green]Rime (Model: {client_config['model']})[/bold green] is ready! Type 'exit' or 'quit' to end.")
    console.print("-" * 50)

    # 初始化 API 客户端
    client = AIClient(client_config)

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

            # 获取并渲染 AI 响应
            response_content = ""
            try:
                # 获取响应生成器
                generator = client.chat_completion(messages)
                
                # 1. 在收到第一个块之前显示“思考中...”
                first_chunk = ""
                with console.status("[bold green]Thinking...", spinner="simpleDots"):
                    try:
                        # 获取第一个块，这一步会阻塞直到服务器返回数据
                        first_chunk = next(generator)
                    except StopIteration:
                        # 如果生成器立即结束（空响应）
                        pass

                if first_chunk:
                    # 2. 收到第一个块后，进入打字机渲染模式
                    response_content = first_chunk
                    
                    # 定义初始渲染组
                    render_group = Group(
                        Text("Rime > ", style="bold green", end=""),
                        Markdown(response_content)
                    )

                    with Live(render_group, refresh_per_second=10) as live:
                        # 逐块处理剩余响应
                        for chunk in generator:
                            response_content += chunk
                            # 实时更新显示内容
                            live.update(Group(
                                Text("Rime > ", style="bold green", end=""),
                                Markdown(response_content)
                            ))
            except KeyboardInterrupt:
                # 用户手动打断生成
                console.print("\n[bold yellow]Generating interrupted by user.[/bold yellow]")
                # 依然保存已生成的部分，防止上下文丢失
                messages.append({"role": "assistant", "content": response_content})
                continue
            
            console.print() # Newline after response
            # 将 AI 的完整回复加入历史记录，保持上下文
            messages.append({"role": "assistant", "content": response_content})

        except KeyboardInterrupt:
            # 处理主循环的 Ctrl+C 中断 (退出程序)
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            # 捕获并显示其他错误
            console.print(f"\n[bold red]An error occurred:[/bold red] {e}")

@cli.command()
@click.option('--key', prompt='API Key', help='Your API Key')
@click.option('--url', prompt='API Base URL', help='API Base URL')
@click.option('--model', prompt='Model Name', help='Model Name')
def config(key, url, model):
    """Configure API credentials."""
    # 将用户输入的配置写入 .env 文件
    env_content = f"API_KEY={key}\nAPI_BASE_URL={url}\nMODEL_NAME={model}\n"
    with open('.env', 'w') as f:
        f.write(env_content)
    console.print("[green]Configuration saved to .env file![/green]")

@cli.command()
@click.option('--port', default=5000, help='Port for the web server')
def web(port):
    """Start the Rime web interface."""
    from rime.server import start_server
    
    # Welcome Banner - Random Selection
    console.print(random.choice(BANNERS))
    
    url = f"http://127.0.0.1:{port}"
    console.print(f"[bold green]Starting Rime Web...[/bold green]")
    console.print(f"Opening {url} in your browser...")

    def open_browser():
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(url)

    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask server
    try:
        start_server(port=port)
    except Exception as e:
        console.print(f"[bold red]Failed to start server:[/bold red] {e}")

if __name__ == '__main__':
    cli()
