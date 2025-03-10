# MySQL MCP Server

[English](README.md) | [中文](README_CN.md)

## 概述

这是一个基于模型上下文协议（Model Context Protocol，MCP）的服务器实现，提供通过 MySQL 进行数据库交互的能力。该服务器支持运行 SQL 查询、创建表格以及探索数据库架构信息。

## 组件

### 工具

服务器提供五个核心工具：

#### 查询工具

* `read_query`  
   * 执行 SELECT 查询以从数据库读取数据  
   * 输入：  
         * `query` (字符串)：要执行的 SELECT SQL 查询语句  
   * 返回：查询结果的对象数组
* `write_query`  
   * 执行 INSERT、UPDATE 或 DELETE 查询  
   * 输入：  
         * `query` (字符串)：SQL 修改查询语句  
   * 返回：`{ affected_rows: number }`（受影响的行数）
* `create_table`  
   * 在数据库中创建新表  
   * 输入：  
         * `query` (字符串)：CREATE TABLE SQL 语句  
   * 返回：表创建成功的确认信息

#### 架构工具

* `list_tables`  
   * 获取数据库中所有表的列表  
   * 无需输入  
   * 返回：表名数组
* `describe_table`  
   * 查看特定表的结构信息  
   * 输入：  
         * `table_name` (字符串)：要描述的表名  
   * 返回：包含列名和类型的列定义数组

## 安装

### 前提条件

- Python 3.10+
- MySQL 数据库
- 所需 Python 包：
  - `mcp` (Model Context Protocol)
  - `sqlalchemy`
  - `pymysql` (或其他 MySQL 驱动)
  - `python-dotenv`
  - `uvicorn` (用于 HTTP 传输)

### 使用 Conda 设置

首先，创建并激活 conda 环境：

```bash
# 创建环境
conda create --name mcp-demo python=3.12
# 激活环境
conda activate mcp-demo
```

然后，安装所需依赖：

```bash
# 方法 1：使用 pip
pip install "mcp[cli]>=0.1.0" "pymysql>=1.1.0" "sqlalchemy>=2.0.0" "python-dotenv>=1.0.0" "uvicorn>=0.27.0"

# 方法 2：使用 uv
uv pip install "mcp[cli]>=0.1.0" "pymysql>=1.1.0" "sqlalchemy>=2.0.0" "python-dotenv>=1.0.0" "uvicorn>=0.27.0"
```

## 配置

您可以使用以下方式配置服务器：

### 环境变量文件 (.env)

1. 复制 `.env.template` 文件并重命名为 `.env`：

```bash
cp .env.template .env
```

2. 编辑 `.env` 文件进行配置：

```
# 数据库配置
DB_URL=mysql+pymysql://username:password@localhost:3306/dbname
```

### 命令行参数

您也可以使用命令行参数覆盖配置：

```bash
python src/mysql/server.py --db-url mysql+pymysql://username:password@localhost:3306/dbname
```

## 使用方法

### 启动服务器

```bash
# 使用 .env 文件配置
python src/mysql/server.py

# 使用命令行参数
python src/mysql/server.py --db-url mysql+pymysql://username:password@localhost:3306/dbname --transport http
```

### 使用 MCP Inspector 测试

您可以使用 MCP Inspector 工具测试服务器：

```bash
npx @modelcontextprotocol/inspector uv run /Users/caicongyang/IdeaProjects/tom/mcp-demo/src/mysql/server.py
```

这将启动服务器并允许您交互式地测试可用工具。

### 示例工作流程

1. 使用 MySQL 数据库连接启动服务器
2. 使用 MCP 客户端将 AI 模型连接到服务器
3. 使用 `list_tables` 工具查看可用表
4. 如需要，使用 `create_table` 创建表
5. 使用 `write_query` 插入数据
6. 使用 `read_query` 查询数据

## 在 Claude Desktop 中使用

### uv

将服务器添加到您的 `claude_desktop_config.json`：

```json
"mcpServers": {
  "mysql": {
    "command": "uv",
    "args": [
      "--directory",
      "path_to_mcp_demo",
      "run",
      "python",
      "src/mysql/server.py",
      "--db-url",
      "mysql+pymysql://username:password@localhost/dbname"
    ]
  }
}
```

### Docker

将服务器添加到您的 `claude_desktop_config.json`：

```json
"mcpServers": {
  "mysql": {
    "command": "docker",
    "args": [
      "run",
      "--rm",
      "-i",
      "-v",
      "mcp-mysql:/mcp",
      "mcp/mysql",
      "--db-url",
      "mysql+pymysql://username:password@localhost/dbname"
    ]
  }
}
```

## 包安装

您也可以使用 pip 安装该包：

```bash
# 以开发模式安装
pip install -e .

# 使用已安装的包运行
mcp-mysql --db-url mysql+pymysql://username:password@localhost/dbname
```

## 在 Cursor IDE 中使用

[Cursor](https://cursor.sh/) 是一个 AI 辅助的 IDE。您可以将此 MCP 服务器与 Cursor 集成，以便在编码过程中直接查询 MySQL 数据库。

### 在 Cursor 中设置

1. **启动 MCP 服务器**

   ```bash
   python src/mysql/server.py
   ```

2. **在 Cursor 设置中配置 MCP**

   添加您的 MCP 服务器 URL：
   
   ```
   http://localhost:8000
   ```

3. **使用 Cursor 命令访问 MCP**

   在 Cursor 编辑器中，使用：

   ```
   /mcp mysql-query {"query": "SELECT * FROM users LIMIT 5"}
   ```

   对于参数化查询：

   ```
   /mcp mysql-query {"query": "SELECT * FROM users WHERE age > :min_age", "params": {"min_age": 30}}
   ```

## API 参考

### 输入格式

```json
{
  "query": "SELECT * FROM users WHERE age > :min_age",
  "params": {
    "min_age": 30
  }
}
```

### 输出格式

```json
{
  "results": [
    {"id": 1, "name": "John", "age": 35},
    {"id": 2, "name": "Jane", "age": 42}
  ],
  "columns": ["id", "name", "age"],
  "rowcount": 2
}
```

## 安全考虑

- 此服务器应在受信任的环境中运行，因为它允许执行任意 SQL 查询
- 在生产环境中，实施适当的访问控制和输入验证
- 考虑限制可以执行的 SQL 命令类型
- **重要**：不要将包含敏感信息的 `.env` 文件提交到版本控制系统

## 开发

### 项目结构

- `src/mysql/server.py`：主服务器实现
- `pyproject.toml`：包配置
- `README.md`：本文档

### 添加新功能

要扩展服务器的功能：
1. 使用 `@mcp.tool()` 装饰器添加新工具
2. 使用 `MySQLDatabase` 类实现工具逻辑
3. 更新文档以反映新功能

## 许可证

此 MCP 服务器采用 MIT 许可证。这意味着您可以自由使用、修改和分发该软件，但须遵守 MIT 许可证的条款和条件。
