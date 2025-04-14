# 简易天气MCP服务

一个最小化的天气查询MCP服务示例，基于HTTP SSE模式。

## 安装

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置API密钥:
```bash
# 方法1: 创建.env文件
cp .env.example .env
# 然后编辑.env文件，填入你的OpenWeather API密钥

# 方法2: 直接设置环境变量
export OPENWEATHER_API_KEY=你的OpenWeather密钥
```

## 使用方法

### 启动服务

```bash
python weather_mcp_server.py
```

服务将在 http://localhost:8000/sse 上运行。

### 使用MCP Inspector测试

1. 安装并运行MCP Inspector:
```bash
npx -y @modelcontextprotocol/inspector
```

2. 在浏览器中打开MCP Inspector (通常是 http://localhost:5173)

3. 选择"SSE" Transport Type，输入URL: http://localhost:8000/sse

4. 点击Connect，然后选择"Tools"标签

5. 调用`get_weather`工具，输入城市名称如"北京"或"London"

### 在Cursor中配置MCP服务器

要在Cursor中使用我们的天气MCP服务，需要进行以下步骤：

1. **确保MCP服务器正在运行**
   ```bash
   python weather_mcp_server.py
   ```

2. **打开Cursor设置**
   - 点击Cursor界面右下角的设置图标，或使用快捷键 `Cmd+,` (Mac) / `Ctrl+,` (Windows/Linux)
   - 在左侧菜单中找到并点击 "MCP"

3. **添加新的MCP配置**
   - 点击 "Add MCP" 按钮
   - 选择 "From File" 或 "From JSON"

4. **如果选择 "From File"**
   - 浏览并选择本项目中的 `cursor_config.json` 文件

5. **如果选择 "From JSON"**
   - 复制以下JSON内容并粘贴到文本框中:
   ```json
   {
     "mcp_service": {
       "name": "SimpleWeatherServer",
       "description": "提供基本天气查询服务",
       "version": "1.0.0",
       "transport": "http",
       "url": "http://localhost:8000"
     },
     "tools": [
       {
         "name": "get_weather",
         "description": "获取指定城市的当前天气",
         "parameters": {
           "type": "object",
           "properties": {
             "location": {
               "type": "string",
               "description": "城市名称，如'北京'、'上海'、'London'"
             }
           },
           "required": ["location"]
         }
       }
     ]
   }
   ```

6. **保存配置**
   - 点击 "Save" 或 "Add" 按钮保存MCP配置
   - 如果配置成功，你应该能在MCP列表中看到 "SimpleWeatherServer"

7. **测试MCP连接**
   - 在Cursor的配置页面，找到你刚添加的 "SimpleWeatherServer"
   - 点击 "Test Connection" 按钮测试连接
   - 如果连接成功，会显示绿色的成功标志

8. **在Cursor中使用天气工具**
   - 在Cursor编辑器中新建或打开一个文件
   - 在聊天框中输入请求：`请使用get_weather查询北京的天气`
   - Cursor应该会调用MCP服务，并返回北京的天气信息

9. **直接使用函数调用**
   - 在聊天框中，你也可以直接使用函数调用语法：
   ```
   get_weather(location="上海")
   ```

10. **故障排除**
    - 如果连接失败，请确保MCP服务器正在运行
    - 检查URL是否正确 (http://localhost:8000)
    - 确保你的API密钥已设置并且有效 