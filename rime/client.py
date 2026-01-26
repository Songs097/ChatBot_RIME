import requests
import os
import json
from typing import List, Dict, Generator

class AIClient:
    """
    一个通用的 AI API 客户端，用于与支持 OpenAI 格式的 API 进行交互。
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化客户端。
        :param api_key: API 密钥
        :param base_url: API 基础地址
        :param model: 使用的模型名称
        """
        self.api_key = api_key
        # 确保 base_url 不以 / 结尾，避免拼接 URL 时出现双斜杠
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        向 API 发送消息并以生成器形式返回响应块（流式传输）。
        假设 API 兼容 OpenAI 的接口格式。
        
        :param messages: 包含对话历史的消息列表，格式为 [{"role": "user", "content": "..."}]
        :return: 生成器，逐个 yield 响应的文本片段
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True  # 启用流式输出，实现打字机效果
        }

        try:
            # 发起 POST 请求，开启 stream=True 以便逐行读取响应
            # 设置 timeout=30，给大模型更多思考时间
            response = requests.post(url, headers=self.headers, json=payload, stream=True, timeout=30)
            response.raise_for_status() # 如果状态码不是 200，抛出异常

            # 逐行读取响应内容（Server-Sent Events 格式）
            # chunk_size=None 表示让服务器决定块大小，通常能避免客户端缓冲
            for line in response.iter_lines(chunk_size=None):
                if line:
                    decoded_line = line.decode('utf-8')
                    # SSE 格式的数据行通常以 "data: " 开头
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:]
                        # "[DONE]" 是 OpenAI 格式 API 传输结束的标志
                        if data_str == '[DONE]':
                            break
                        try:
                            # 解析 JSON 数据
                            data = json.loads(data_str)
                            # 提取 delta 中的 content 内容
                            delta = data.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            # 忽略解析错误的行
                            continue
        except requests.exceptions.RequestException as e:
            yield f"Error: {str(e)}"
