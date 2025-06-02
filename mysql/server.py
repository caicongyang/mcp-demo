"""
MCP Server for MySQL queries.
This server implements the Model Context Protocol to query a MySQL database.

该服务器实现了 Model Context Protocol (MCP)，用于执行 MySQL 数据库查询。
它允许客户端通过 MCP 协议发送 SQL 查询，并以结构化的方式返回查询结果。
"""

import os
import sys
import logging
from typing import Any, Dict, List, Optional
import json
import asyncio
import argparse
from pathlib import Path

import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio

# 配置日志记录 - 设置日志级别为 INFO，以便记录服务器的重要事件
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp_mysql_server')
logger.info("Starting MCP MySQL Server")

# 如果在 Windows 上运行，确保使用 UTF-8 编码
# Windows 默认可能不使用 UTF-8，这可能导致中文等非 ASCII 字符显示问题
if sys.platform == "win32" and os.environ.get('PYTHONIOENCODING') is None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def load_env_file(env_file: Optional[str] = None) -> bool:
    """
    加载环境变量文件。
    
    参数:
        env_file: 环境变量文件路径，如果为 None，则尝试在当前目录查找 .env 文件
        
    返回:
        是否成功加载环境变量文件
    """
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
        return True
    
    # 尝试在当前目录查找 .env 文件
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path.absolute()}")
        return True
    
    logger.warning("No .env file found")
    return False

def get_db_url(cmd_db_url: Optional[str] = None, env_file: Optional[str] = None) -> str:
    """
    获取数据库连接 URL。
    
    参数:
        cmd_db_url: 命令行参数提供的数据库 URL
        env_file: 环境变量文件路径
        
    返回:
        数据库连接 URL
    """
    # 如果命令行参数提供了数据库 URL，优先使用
    if cmd_db_url:
        return cmd_db_url
    
    # 尝试加载环境变量
    load_env_file(env_file)
    
    # 从环境变量获取数据库 URL
    db_url = os.environ.get("DB_URL")
    if not db_url:
        raise ValueError("Database URL not provided. Use --db-url or set DB_URL environment variable.")
    
    return db_url

class MySQLDatabase:
    """
    MySQL 数据库连接和查询执行类。
    
    该类负责：
    1. 建立与 MySQL 数据库的连接
    2. 执行 SQL 查询并处理结果
    3. 处理查询错误和异常
    4. 转换查询结果为适合 JSON 序列化的格式
    """
    
    def __init__(self, db_url: str):
        """
        初始化 MySQL 数据库连接。
        
        参数:
            db_url: SQLAlchemy 连接 URL，格式如：mysql+pymysql://用户名:密码@主机:端口/数据库名
                   例如: mysql+pymysql://root:password@localhost:3306/mydb
        
        初始化过程:
        1. 保存数据库连接 URL
        2. 创建 SQLAlchemy 引擎对象
        3. 测试数据库连接是否成功
        """
        self.db_url = db_url
        # 创建 SQLAlchemy 引擎 - 这是与数据库交互的核心对象
        self.engine = create_engine(db_url)
        
        # 测试数据库连接 - 执行一个简单的查询确保连接正常
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Successfully connected to database: {db_url}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行 SQL 查询并返回结果。
        
        参数:
            query: 要执行的 SQL 查询字符串
            params: 查询参数字典（可选），用于参数化查询
            
        返回:
            查询结果的字典列表，每个字典代表一行数据，键为列名
            
        处理流程:
        1. 记录查询（不包含敏感数据）
        2. 连接数据库并执行查询
        3. 判断查询类型（读/写操作）
        4. 处理查询结果，转换为适合 JSON 序列化的格式
        5. 处理可能的异常
        """
        if params is None:
            params = {}
            
        try:
            # 记录查询（注意敏感数据处理）
            logger.info(f"Executing query: {query}")
            
            # 执行查询
            with self.engine.connect() as conn:
                # 使用 SQLAlchemy 的 text 函数创建 SQL 表达式，并传入参数
                # text() 函数将普通 SQL 字符串转换为 SQLAlchemy 可以处理的 SQL 表达式
                result = conn.execute(text(query), params)
                
                # 检查是否是写入操作（非 SELECT 查询）
                # 通过检查查询字符串是否以 SELECT 开头来判断
                is_write_query = not query.strip().upper().startswith("SELECT")
                
                if is_write_query:
                    # 对于非 SELECT 查询（INSERT, UPDATE, DELETE 等）
                    # 返回受影响的行数
                    affected = result.rowcount
                    logger.debug(f"Write query affected {affected} rows")
                    return [{"affected_rows": affected}]
                
                # 将结果转换为字典列表
                results = []
                for row in result:
                    # 将行转换为字典，并处理不可序列化的类型
                    row_dict = {}
                    for i, column in enumerate(result.keys()):
                        value = row[i]
                        # 处理不可 JSON 序列化的类型
                        # 例如日期、时间等需要转换为字符串
                        if isinstance(value, (sqlalchemy.Date, sqlalchemy.DateTime)):
                            value = value.isoformat()
                        elif hasattr(value, "__str__"):
                            value = str(value)
                        row_dict[column] = value
                    results.append(row_dict)
                
                logger.debug(f"Read query returned {len(results)} rows")
                return results
                
        except Exception as e:
            # 记录错误并返回错误响应
            logger.error(f"Database error executing query: {e}")
            raise

# 创建 MCP 服务器实例
server = Server("mysql-manager")

# 获取全局数据库实例
db_instance = None

def get_database():
    """获取数据库实例"""
    global db_instance
    if db_instance is None:
        db_url = get_db_url()
        db_instance = MySQLDatabase(db_url)
    return db_instance

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="read_query",
            description="Execute a SELECT query to read data from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SELECT SQL query to execute"
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="write_query",
            description="Execute an INSERT, UPDATE, or DELETE query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL modification query to execute"
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="create_table",
            description="Create a new table in the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "CREATE TABLE SQL statement"
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="describe_table",
            description="Get the structure of a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    try:
        db = get_database()
        
        if name == "read_query":
            query = arguments.get("query")
            if not query.strip().upper().startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed for read_query")
            
            results = db.execute_query(query)
            return [types.TextContent(type="text", text=str(results))]
        
        elif name == "write_query":
            query = arguments.get("query")
            if query.strip().upper().startswith("SELECT"):
                raise ValueError("SELECT queries are not allowed for write_query")
            
            results = db.execute_query(query)
            return [types.TextContent(type="text", text=str(results))]
        
        elif name == "create_table":
            query = arguments.get("query")
            if not query.strip().upper().startswith("CREATE TABLE"):
                raise ValueError("Only CREATE TABLE statements are allowed")
            
            db.execute_query(query)
            return [types.TextContent(type="text", text="Table created successfully")]
        
        elif name == "list_tables":
            results = db.execute_query("SHOW TABLES")
            return [types.TextContent(type="text", text=str(results))]
        
        elif name == "describe_table":
            table_name = arguments.get("table_name")
            results = db.execute_query(f"DESCRIBE {table_name}")
            return [types.TextContent(type="text", text=str(results))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

# 主函数
def run_server():
    """从命令行运行 MySQL Query MCP 服务器的入口函数。"""
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Run a MySQL Query MCP Server")
    parser.add_argument(
        "--db-url", 
        type=str, 
        help="Database URL (e.g., mysql+pymysql://user:password@localhost/dbname)"
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["http", "stdio"],
        default="stdio",
        help="Transport protocol to use (http or stdio)"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to .env file for configuration"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 加载环境变量
        load_env_file(args.env_file)
        
        # 获取数据库 URL
        db_url = get_db_url(args.db_url)
        
        # 隐藏密码部分用于日志记录
        db_url_safe = db_url
        if ":" in db_url and "@" in db_url:
            parts = db_url.split("@")
            credentials = parts[0].split(":")
            if len(credentials) > 2:
                db_url_safe = f"{credentials[0]}:****@{parts[1]}"
        
        logger.info(f"Database URL: {db_url_safe}")
        
        # 根据传输类型选择运行方式
        if args.transport == "stdio":
            logger.info("Starting MCP server with stdio transport")
            # 运行stdio服务器
            async def main():
                async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                    await server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name="mysql-manager",
                            server_version="0.1.0",
                            capabilities=server.get_capabilities(
                                notification_options=NotificationOptions(),
                                experimental_capabilities={},
                            ),
                        ),
                    )
            
            # 运行服务器
            asyncio.run(main())
        else:
            logger.info("Starting MCP server with HTTP transport - not implemented")
            sys.exit(1)
            
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 当脚本直接运行时，执行 run_server 函数
    run_server() 