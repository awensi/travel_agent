import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from anthropic import Anthropic
from mcp.client.stdio import stdio_client
from mcp.types import ListToolsResult
import sys
import logging
from openai import OpenAI
import httpx
#1 配置mvp server的启动参数

logging.basicConfig(
    filename="D:\\project\\travel_agent\\myagent_server_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

server_params = StdioServerParameters(
    command=sys.executable, #强制使用当前运行agent的Python解释器，用conda的环境
    args=[os.path.abspath("D:\\project\\travel_agent\\mysql_mcp_server.py")],
    env={**os.environ, "PYTHONUNBUFFERED": "1"}
)

async def run_agent():
    #初始化anthropic 客户端
    # anthropic = Anthropic(
    #     api_key="sk-8de1af2c320640409f98ffd65352f8d5",
    #     # base_url="https://dashscope.aliyuncs.com/apps/anthropic"
    #     base_url="https://dashscope-intl.aliyuncs.com/apps/anthropic"
    # )
    client = OpenAI(
        api_key="sk-8de1af2c320640409f98ffd65352f8d5", 
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        # http_client=httpx.Client(proxy={})

    )

    #与MCP server建立连接
    async with stdio_client(server_params) as (read, write):
        try:
            async with ClientSession(read, write) as session:
                await session.initialize()
                logging.info("连接成功！正在获取工具列表...")
                #列出服务器提供的工具，让agent知道能做什么
                response = await session.list_tools()
                tools = response.tools
                # tools = response.tools
                #将MCP工具转换成anthropic格式的工具定义
                openai_tools = [
                    {
                        "type":"function",
                        "function":{
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    }
                    for tool in tools
                ]
                
                # print("------数据库agent已上线")
                user_input = "帮我创建一个新用户，名字叫 '王小明'，邮箱是 'wang@example.com'"
                # user_input = "帮我查询全部的用户信息"
                messages = [
                     {
                            "role":"system",
                            "content":"你是一个数据库管理助手。请根据用户需求调用工具。执行新增或者删除等写的操作时，严禁连续执行相同操作。如果工具返回成功，请直接汇报结果，不要再次尝试。只有工具明确返回错误，且你有办法修复参数时，才允许重试一次"
                        },
                        {
                            "role":"user",
                            "content": user_input
                        }
                ]

                #多轮对话逻辑
                while True:
                    response = client.chat.completions.create(
                        model="qwen-max",
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto"
                    )
                    response_msg = response.choices[0].message
                    messages.append(response_msg)

                    #检查是否有工具调用请求,如果没有工具调用请求，则说明已经完成agent
                    if not response_msg.tool_calls:
                        print(f"最终回复:{response_msg.content}")
                        break

                    #指向性所有被请求的工具(OPENAI支持并行调用)
                    for tool_call in response_msg.tool_calls:
                        function_name = tool_call.function.name
                        import json
                        args = json.loads(tool_call.function.arguments)

                        print(f"正在执行工具：{function_name}, 参数：{args}")

                        #调用MCP server执行数据库操作
                        result = await session.call_tool(function_name, args)

                        #将结果塞回消息历史
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": f"操作结果汇报： {result.content[0].text}",
                            }
                        )
                print("消息处理完毕")
        except Exception as e:
            print(f"the fail reason is {e}")    

if __name__ == "__main__":
    asyncio.run(run_agent())