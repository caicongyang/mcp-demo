import requests
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载.env文件中的环境变量
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# 初始化MCP服务器
mcp = FastMCP("SimpleWeatherServer")

@mcp.tool()
def get_weather(location: str):
    """
    获取指定城市的当前天气
    :param location: 城市名称
    :return: 天气信息
    """
    # 优先从环境变量获取API密钥（包括.env文件中的设置）
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    if not api_key:
        return {"错误": "请在.env文件或环境变量中设置OPENWEATHER_API_KEY"}
        
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        weather_info = {
            "城市": location,
            "天气状况": data['weather'][0]['description'],
            "温度": f"{data['main']['temp']}°C",
            "体感温度": f"{data['main']['feels_like']}°C",
            "湿度": f"{data['main']['humidity']}%",
            "风速": f"{data['wind']['speed']} m/s",
            "风向": f"{data['wind']['deg']}°",
            "云量": f"{data['clouds']['all']}%"
        }
        return weather_info
    else:
        return {"错误": f"无法获取天气信息: {data.get('message', '未知错误')}"}

# 启动服务器
if __name__ == "__main__":
    print("简易天气MCP服务器运行中...")
    print("使用方法:")
    print("1. 本地调试: python weather_mcp_server.py")
    print("2. 连接MCP Inspector: http://localhost:8000/sse")
    print("3. 调用get_weather工具，输入城市名称")
    
    if os.environ.get("OPENWEATHER_API_KEY"):
        print("\nAPI密钥已设置，服务准备就绪！")
    else:
        print("\n警告: 未找到OPENWEATHER_API_KEY")
        print("请在.env文件中添加以下内容，或设置环境变量:")
        print("OPENWEATHER_API_KEY=你的密钥")
    
    mcp.run()  # 默认使用SSE模式 