# MySQL MCP Server

[English](README.md) | [中文](README_CN.md)

## Overview

A Model Context Protocol (MCP) server implementation that provides database interaction capabilities through MySQL. This server enables running SQL queries, creating tables, and exploring database schema information.

## Components

### Tools

The server offers five core tools:

#### Query Tools

* `read_query`  
   * Execute SELECT queries to read data from the database  
   * Input:  
         * `query` (string): The SELECT SQL query to execute  
   * Returns: Query results as array of objects
* `write_query`  
   * Execute INSERT, UPDATE, or DELETE queries  
   * Input:  
         * `query` (string): The SQL modification query  
   * Returns: `{ affected_rows: number }`
* `create_table`  
   * Create new tables in the database  
   * Input:  
         * `query` (string): CREATE TABLE SQL statement  
   * Returns: Confirmation of table creation

#### Schema Tools

* `list_tables`  
   * Get a list of all tables in the database  
   * No input required  
   * Returns: Array of table names
* `describe_table`  
   * View schema information for a specific table  
   * Input:  
         * `table_name` (string): Name of table to describe  
   * Returns: Array of column definitions with names and types

## Installation

### Prerequisites

- Python 3.10+
- MySQL database
- Required Python packages:
  - `mcp` (Model Context Protocol)
  - `sqlalchemy`
  - `pymysql` (or another MySQL driver)
  - `python-dotenv`
  - `uvicorn` (for HTTP transport)

### Setup with Conda

First, create and activate a conda environment:

```bash
# Create environment
conda create --name mcp-demo python=3.12
# Activate environment
conda activate mcp-demo
```

Then, install the required dependencies:

```bash
# Method 1: Using pip
pip install "mcp[cli]>=0.1.0" "pymysql>=1.1.0" "sqlalchemy>=2.0.0" "python-dotenv>=1.0.0" "uvicorn>=0.27.0"

# Method 2: Using uv
uv pip install "mcp[cli]>=0.1.0" "pymysql>=1.1.0" "sqlalchemy>=2.0.0" "python-dotenv>=1.0.0" "uvicorn>=0.27.0"
```

## Configuration

You can configure the server using:

### Environment Variables File (.env)

1. Copy the `.env.template` file and rename it to `.env`:

```bash
cp .env.template .env
```

2. Edit the `.env` file with your configuration:

```
# Database configuration
DB_URL=mysql+pymysql://username:password@localhost:3306/dbname
```

### Command Line Arguments

You can also override configuration with command line arguments:

```bash
python src/mysql/server.py --db-url mysql+pymysql://username:password@localhost:3306/dbname
```

## Usage

### Starting the Server

```bash
# Using .env file configuration
python src/mysql/server.py

# Using command line arguments
python src/mysql/server.py --db-url mysql+pymysql://username:password@localhost:3306/dbname --transport http
```

### Testing with MCP Inspector

You can test the server using the MCP Inspector tool:

```bash
npx @modelcontextprotocol/inspector uv run /Users/caicongyang/IdeaProjects/tom/mcp-demo/src/mysql/server.py
```

This will start the server and allow you to interactively test the available tools.

### Example Workflow

1. Start the server with your MySQL database connection
2. Connect an AI model to the server using the MCP client
3. Use the `list_tables` tool to see available tables
4. Create tables with `create_table` if needed
5. Insert data with `write_query`
6. Query data with `read_query`

## Usage with Claude Desktop

### uv

Add the server to your `claude_desktop_config.json`:

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

Add the server to your `claude_desktop_config.json`:

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

## Package Installation

You can also install the package using pip:

```bash
# Install in development mode
pip install -e .

# Run using the installed package
mcp-mysql --db-url mysql+pymysql://username:password@localhost/dbname
```

## In Cursor IDE

[Cursor](https://cursor.sh/) is an AI-assisted IDE. You can integrate this MCP server with Cursor to query MySQL databases directly during coding.

### Setup in Cursor

1. **Start the MCP server**

   ```bash
   python src/mysql/server.py
   ```

2. **Configure MCP in Cursor settings**

   Add your MCP server URL:
   
   ```
   http://localhost:8000
   ```

3. **Use Cursor commands to access MCP**

   In the Cursor editor, use:

   ```
   /mcp mysql-query {"query": "SELECT * FROM users LIMIT 5"}
   ```

   For parameterized queries:

   ```
   /mcp mysql-query {"query": "SELECT * FROM users WHERE age > :min_age", "params": {"min_age": 30}}
   ```

## API Reference

### Input Format

```json
{
  "query": "SELECT * FROM users WHERE age > :min_age",
  "params": {
    "min_age": 30
  }
}
```

### Output Format

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

## Security Considerations

- This server should be run in a trusted environment as it allows arbitrary SQL queries
- In production, implement proper access control and input validation
- Consider limiting the types of SQL commands that can be executed
- **Important**: Do not commit `.env` files containing sensitive information to version control

## Development

### Project Structure

- `src/mysql/server.py`: Main server implementation
- `pyproject.toml`: Package configuration
- `README.md`: This documentation

### Adding New Features

To extend the server with new capabilities:
1. Add new tools using the `@mcp.tool()` decorator
2. Implement the tool logic using the `MySQLDatabase` class
3. Update the documentation to reflect the new capabilities

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
