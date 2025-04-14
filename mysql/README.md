# 简易MySQL MCP服务

一个最小化的MySQL查询MCP服务示例，基于HTTP SSE或stdio模式。

本文档主要介绍 MySQL MCP 服务的安装和使用。

## 安装

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置数据库连接:
```bash
# 方法1: 创建.env文件
cp .env.example .env
# 然后编辑.env文件，填入你的MySQL连接信息

# 方法2: 直接设置环境变量
export MYSQL_CONNECTION_STRING=mysql://user:password@localhost:3306/database
```

## 使用方法

### 启动服务

```bash
# 默认使用stdio模式启动
python server.py

# 或明确指定transport模式
python server.py --transport stdio  # 使用stdio模式
```


### 使用MCP Inspector测试

1. 安装并运行MCP Inspector:
```bash
npx -y @modelcontextprotocol/inspector
```

2. 在浏览器中打开MCP Inspector (通常是 http://localhost:5173)

3. 选择适当的Transport Type:
   - 如果使用stdio模式，选择"subprocess"并指定`python server.py`作为命令

4. 点击Connect，然后选择"Tools"标签

5. 调用相应工具，如`read_query`，输入SQL查询如"SELECT * FROM users LIMIT 10"

### 在Cursor中配置MCP服务器

要在Cursor中使用我们的MySQL MCP服务，需要进行以下步骤：

1. **确保你已安装了所有依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **编辑Cursor的MCP配置文件**
   - Cursor的MCP配置文件通常位于 `~/.cursor/mcp.json`
   - 如果该文件不存在，请创建它
   - 使用以下格式添加MySQL MCP服务配置:

   ```json
   {
     "mcpServers": {
       "mysql-mcp": {
         "command": "python",
         "args": ["/完整路径/server.py"]
       }
       // ... 其他现有MCP服务配置 ...
     }
   }
   ```

   - 请将`/完整路径/`替换为`server.py`文件的实际路径
   - 您可以根据需要修改服务名称`mysql-mcp`

3. **重启Cursor**
   - 保存配置文件后，重启Cursor以加载新的MCP配置

4. **在Cursor中使用MySQL工具**
   - 在Cursor编辑器中新建或打开一个文件
   - 在聊天框中输入请求：`请使用mysql-mcp的read_query执行"SELECT VERSION()"`
   - Cursor应该会调用MCP服务，并返回MySQL版本信息

5. **故障排除**
   - 如果连接失败，请检查配置文件格式是否正确
   - 确保`server.py`的路径是绝对路径且正确
   - 确保所有依赖都已安装
   - 确保你的数据库连接信息已设置并且有效 