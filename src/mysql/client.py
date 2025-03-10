"""
Example client for the MySQL Query MCP Server.
"""

import asyncio
import json
import logging
import ast
from typing import Dict, Any, List, Optional

from mcp.client import Client

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def query_mysql(
    server_url: str, 
    query: str, 
    is_read: bool = True
) -> List[Dict[str, Any]]:
    """Query the MySQL database through the MCP server.
    
    Args:
        server_url: URL of the MCP server
        query: SQL query to execute
        is_read: Whether this is a read (SELECT) query or a write query
        
    Returns:
        Query results as a list of dictionaries
    """
    # 创建客户端
    client = Client(server_url)
    
    try:
        # 连接到服务器
        await client.connect()
        
        # 获取可用工具
        tools = await client.list_tools()
        logger.info(f"Available tools: {[t.name for t in tools]}")
        
        # 选择适当的工具
        tool_name = "read_query" if is_read else "write_query"
        
        # 查找工具
        tool = None
        for t in tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            raise ValueError(f"{tool_name} tool not found. Available tools: {[t.name for t in tools]}")
        
        # 准备查询参数
        call_params = {"query": query}
        
        # 调用工具执行查询
        logger.info(f"Executing query using tool: {tool.name}")
        result = await client.call_tool(tool.name, call_params)
        
        # 处理结果
        if not result or not result[0].text:
            return []
        
        # 结果是一个字符串表示的 Python 列表，需要解析
        try:
            # 使用 ast.literal_eval 安全地解析字符串表示的 Python 对象
            parsed_result = ast.literal_eval(result[0].text)
            return parsed_result
        except (SyntaxError, ValueError) as e:
            logger.error(f"Failed to parse result: {e}")
            return []
        
    finally:
        # 关闭连接
        await client.close()

async def list_tables(server_url: str) -> List[Dict[str, Any]]:
    """List all tables in the MySQL database.
    
    Args:
        server_url: URL of the MCP server
        
    Returns:
        List of tables
    """
    # 创建客户端
    client = Client(server_url)
    
    try:
        # 连接到服务器
        await client.connect()
        
        # 获取可用工具
        tools = await client.list_tools()
        
        # 查找 list_tables 工具
        tool = None
        for t in tools:
            if t.name == "list_tables":
                tool = t
                break
        
        if not tool:
            raise ValueError(f"list_tables tool not found. Available tools: {[t.name for t in tools]}")
        
        # 调用工具
        logger.info(f"Listing tables using tool: {tool.name}")
        result = await client.call_tool(tool.name, {})
        
        # 处理结果
        if not result or not result[0].text:
            return []
        
        # 解析结果
        try:
            parsed_result = ast.literal_eval(result[0].text)
            return parsed_result
        except (SyntaxError, ValueError) as e:
            logger.error(f"Failed to parse result: {e}")
            return []
        
    finally:
        # 关闭连接
        await client.close()

async def describe_table(server_url: str, table_name: str) -> List[Dict[str, Any]]:
    """Describe a table in the MySQL database.
    
    Args:
        server_url: URL of the MCP server
        table_name: Name of the table to describe
        
    Returns:
        Table schema information
    """
    # 创建客户端
    client = Client(server_url)
    
    try:
        # 连接到服务器
        await client.connect()
        
        # 获取可用工具
        tools = await client.list_tools()
        
        # 查找 describe_table 工具
        tool = None
        for t in tools:
            if t.name == "describe_table":
                tool = t
                break
        
        if not tool:
            raise ValueError(f"describe_table tool not found. Available tools: {[t.name for t in tools]}")
        
        # 调用工具
        logger.info(f"Describing table {table_name} using tool: {tool.name}")
        result = await client.call_tool(tool.name, {"table_name": table_name})
        
        # 处理结果
        if not result or not result[0].text:
            return []
        
        # 解析结果
        try:
            parsed_result = ast.literal_eval(result[0].text)
            return parsed_result
        except (SyntaxError, ValueError) as e:
            logger.error(f"Failed to parse result: {e}")
            return []
        
    finally:
        # 关闭连接
        await client.close()

async def main():
    """Run example queries against the MySQL MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MySQL Query MCP Client Example")
    parser.add_argument(
        "--server-url", 
        type=str, 
        default="http://localhost:3000", 
        help="URL of the MCP server"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Custom SQL query to execute"
    )
    parser.add_argument(
        "--list-tables",
        action="store_true",
        help="List all tables in the database"
    )
    parser.add_argument(
        "--describe-table",
        type=str,
        help="Describe a specific table"
    )
    
    args = parser.parse_args()
    
    try:
        if args.list_tables:
            # 列出所有表
            tables = await list_tables(args.server_url)
            print("\n=== Tables in Database ===")
            print(json.dumps(tables, indent=2))
            return
            
        if args.describe_table:
            # 描述表结构
            schema = await describe_table(args.server_url, args.describe_table)
            print(f"\n=== Schema for Table '{args.describe_table}' ===")
            print(json.dumps(schema, indent=2))
            return
            
        if args.query:
            # 执行自定义查询
            is_read = args.query.strip().upper().startswith("SELECT")
            result = await query_mysql(args.server_url, args.query, is_read)
            print("\n=== Custom Query Results ===")
            print(f"Query: {args.query}")
            print(json.dumps(result, indent=2))
            return
        
        # 如果没有指定任何操作，运行一些示例查询
        
        # 示例 1: 列出所有表
        try:
            tables = await list_tables(args.server_url)
            print("\n=== Example 1: Tables in Database ===")
            print(json.dumps(tables, indent=2))
            
            # 如果有表，描述第一个表
            if tables and len(tables) > 0:
                first_table = tables[0].get("Tables_in_" + tables[0].keys().__iter__().__next__().split("_")[-1], None)
                if first_table:
                    schema = await describe_table(args.server_url, first_table)
                    print(f"\n=== Example 2: Schema for Table '{first_table}' ===")
                    print(json.dumps(schema, indent=2))
        except Exception as e:
            logger.error(f"Example failed: {e}")
        
        # 示例 3: 执行 SELECT 查询
        try:
            result = await query_mysql(
                args.server_url,
                "SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = DATABASE() ORDER BY table_rows DESC LIMIT 10",
                True
            )
            print("\n=== Example 3: Database information ===")
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Example 3 failed: {e}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 