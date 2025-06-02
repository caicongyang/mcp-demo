import os
import sys
import json
import subprocess
import re

def execute_mysql_query(query):
    """执行MySQL查询并返回结果"""
    # 调用MySQL MCP服务器
    cmd = ["python", "mysql/server.py"]
    
    # 准备MCP JSON-RPC消息
    initialize_msg = '{"jsonrpc": "2.0","method": "initialize","params": {"protocolVersion": "2025-03-26","capabilities": {},"clientInfo": {"name": "test", "version": "0.1.0"}},"id": 1}\n'
    initialized_msg = '{"jsonrpc": "2.0","method": "notifications/initialized"}\n'
    
    # 准备查询消息
    query_upper = query.strip().upper()
    
    # 处理特殊查询
    if query_upper == "SHOW TABLES":
        # 使用list_tables工具
        query_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_tables", 
                "arguments": {}
            }
        }) + "\n"
    elif query_upper.startswith("DESCRIBE ") or query_upper.startswith("DESC "):
        # 提取表名
        match = re.search(r"DESC(?:RIBE)?\s+(\w+)", query, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            # 使用describe_table工具
            query_msg = json.dumps({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "describe_table", 
                    "arguments": {"table_name": table_name}
                }
            }) + "\n"
        else:
            return "无法解析表名"
    elif query_upper.startswith("SELECT"):
        # 使用read_query工具执行SELECT查询
        query_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "read_query", 
                "arguments": {"query": query}
            }
        }) + "\n"
    else:
        # 使用write_query工具执行写入查询
        query_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "write_query", 
                "arguments": {"query": query}
            }
        }) + "\n"
    
    # 启动进程
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # 发送初始化消息
        process.stdin.write(initialize_msg)
        process.stdin.flush()
        
        # 读取响应
        init_response = process.stdout.readline().strip()
        print(f"初始化成功: 连接到MySQL MCP服务器")
        
        # 发送initialized通知
        process.stdin.write(initialized_msg)
        process.stdin.flush()
        
        # 发送查询请求
        process.stdin.write(query_msg)
        process.stdin.flush()
        
        # 读取查询响应
        query_response = process.stdout.readline().strip()
        
        # 解析JSON响应
        response_obj = json.loads(query_response)
        if "result" in response_obj and "content" in response_obj["result"]:
            content = response_obj["result"]["content"]
            if content and len(content) > 0 and "text" in content[0]:
                return content[0]["text"]
            else:
                return f"未能解析查询结果: {content}"
        else:
            return f"响应格式不符合预期: {response_obj}"
            
    except Exception as e:
        return f"执行查询时出错: {e}"
    finally:
        # 关闭进程
        process.terminate()

def main():
    # 如果命令行提供了查询，则使用它
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # 否则，提示用户输入
        query = input("请输入SQL查询: ")
    
    # 执行查询
    result = execute_mysql_query(query)
    print(f"查询结果:\n{result}")

if __name__ == "__main__":
    main() 