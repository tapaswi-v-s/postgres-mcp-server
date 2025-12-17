# SQL Agent MCP Server

A **Model Context Protocol (MCP)** server powered by **FastMCP** that provides database tools for SQL query execution and database exploration. This server exposes all the necessary tools for the SQL Agent to interact with PostgreSQL databases.

> **Built with FastMCP** - A modern Python framework for building MCP servers with a streamlined API and excellent cloud deployment support.

## 🚀 Features

- **Schema Exploration**: List and explore database schemas
- **Table Management**: List tables and view detailed table structures
- **Query Execution**: Execute SELECT queries (read-only, no confirmation needed)
- **Write Operations**: Execute INSERT, UPDATE, DELETE, DDL operations (with confirmation)
- **Sample Data**: Retrieve sample data from tables for exploration
- **Query Classification**: Automatic classification of SQL query types (DQL, DML, DDL, etc.)

## 📋 Available Tools

### 1. `list_schemas`
List all schemas in the OMNI_STORE database.

**Parameters:** None

**Example Response:**
```
Available schemas in OMNI_STORE:
  - public
  - analytics
  - staging
```

### 2. `list_tables`
List all tables in a specific schema.

**Parameters:**
- `schema_name` (string, optional): Name of the schema (default: "public")

**Example Response:**
```
Tables in schema 'public':
  - users
  - orders
  - products
```

### 3. `describe_table`
Describe the structure of a specific table including columns, types, and constraints.

**Parameters:**
- `table_name` (string, required): Name of the table to describe
- `schema_name` (string, optional): Name of the schema (default: "public")

**Example Response:**
```
Table: public.users

Columns:
  - id: INTEGER NOT NULL
  - username: VARCHAR(100) NOT NULL
  - email: VARCHAR(255) NOT NULL
  - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Primary Key: id

Foreign Keys:
  - None
```

### 4. `execute_select_query`
Execute a SELECT query on the database (read-only, no confirmation needed).

**Parameters:**
- `sql_query` (string, required): The SELECT SQL query to execute

**Example Response:**
```
Query returned 10 row(s):

id | username | email
----------------------------
1 | john_doe | john@example.com
2 | jane_doe | jane@example.com
...
```

### 5. `execute_write_query`
Execute write operations (INSERT, UPDATE, DELETE, DDL) with user confirmation.

**Parameters:**
- `sql_query` (string, required): The SQL query to execute
- `confirmed` (boolean, optional): Whether the user has confirmed execution (default: false)

**Example Response (without confirmation):**
```
CONFIRMATION_REQUIRED
Query Type: DML
SQL Query:
DELETE FROM users WHERE id = 123

This query will modify the database. It requires user confirmation before execution.
Please ask the user: "Do you want to proceed with this DML operation? (yes/no)"
```

### 6. `get_sample_data`
Get sample data from a table to understand its content.

**Parameters:**
- `table_name` (string, required): Name of the table
- `schema_name` (string, optional): Name of the schema (default: "public")
- `limit` (integer, optional): Number of rows to return (default: 5)

**Example Response:**
```
Query returned 5 row(s):

id | name | price
-------------------
1 | Product A | 19.99
2 | Product B | 29.99
...
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- FastMCP installed (`pip install fastmcp`)
- Access to FastMCP Cloud (for deployment) - https://fastmcp.com

### Local Development Setup

1. **Clone or navigate to the mcp-server directory:**
   ```bash
   cd mcp-server
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Create a `.env` file in the mcp-server directory with your database credentials:
   ```env
   DB_HOST=your-database-host.com
   DB_PORT=5432
   DB_NAME=OMNI_STORE
   DB_USER=your-db-username
   DB_PASSWORD=your-db-password
   ```

5. **Run the server locally:**
   ```bash
   # Using FastMCP dev server (recommended)
   fastmcp dev server.py
   
   # Or run directly with Python
   python -m fastmcp run server.py
   ```

## ☁️ Deployment to FastMCP Cloud

### Configuration

All deployment configurations are defined in `config.yaml`. Key settings include:

- **Server Information**: Name, version, description
- **Database Connection**: Connection parameters and pooling settings
- **Tools Configuration**: Enabled tools and their specific settings
- **Security**: Query filtering, rate limiting, IP whitelisting
- **Monitoring**: Health checks, metrics, auto-scaling

### Deployment Steps

1. **Install FastMCP CLI:**
   ```bash
   pip install fastmcp
   ```

2. **Authenticate with FastMCP Cloud:**
   ```bash
   fastmcp login
   ```

3. **Deploy your server:**
   ```bash
   cd mcp-server
   fastmcp deploy --name sql-agent-mcp-server --entry server.py
   ```

4. **Set environment variables:**
   ```bash
   fastmcp env set DB_HOST your-db-host.com
   fastmcp env set DB_PORT 5432
   fastmcp env set DB_NAME OMNI_STORE
   fastmcp env set DB_USER your_user
   fastmcp env set DB_PASSWORD your_password --secret
   ```

5. **Verify deployment:**
   ```bash
   # Check status
   fastmcp status sql-agent-mcp-server
   
   # List available tools
   fastmcp tools sql-agent-mcp-server
   
   # Test a tool
   fastmcp invoke sql-agent-mcp-server list_schemas
   ```

### Environment Variables (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database host address | `db.example.com` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `OMNI_STORE` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `your-secure-password` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `MCP_CLOUD_API_KEY` | MCP Cloud API key | - |
| `MCP_CLOUD_PROJECT_ID` | Project ID | - |

## 📊 Configuration Reference

### Server Settings (`config.yaml`)

```yaml
server:
  name: "sql-agent-mcp-server"
  version: "1.0.0"
  settings:
    protocol_version: "1.0"
    logging:
      level: "INFO"
```

### Database Configuration

```yaml
database:
  host: "${DB_HOST}"
  port: "${DB_PORT:5432}"
  pool:
    size: 5
    max_overflow: 10
```

### Security Settings

```yaml
security:
  query_filtering:
    enabled: true
    blocked_keywords:
      - "DROP DATABASE"
      - "DROP SCHEMA"
  rate_limiting:
    enabled: true
    max_queries_per_minute: 60
```

## 🔒 Security Best Practices

1. **Never commit `.env` files** - Use environment variables for sensitive data
2. **Enable query filtering** - Prevent dangerous operations
3. **Use rate limiting** - Protect against abuse
4. **Require confirmation** - Always confirm write operations
5. **IP whitelisting** - Restrict access to known IPs (if applicable)
6. **Regular updates** - Keep dependencies up to date

## 🧪 Testing

### Test Connection

```bash
# Test database connection
python -c "from server import DatabaseConnection; db = DatabaseConnection(); print('Connection successful!')"
```

### Test Individual Tools

You can test tools using FastMCP CLI or by importing them directly:

```bash
# Using FastMCP CLI
fastmcp dev server.py

# In another terminal, test tools
fastmcp invoke sql-agent-mcp-server list_schemas
fastmcp invoke sql-agent-mcp-server list_tables --args '{"schema_name": "public"}'
```

Or test by importing directly:

```python
import asyncio
from server import list_schemas, list_tables

# Test list_schemas
result = asyncio.run(list_schemas())
print(result)

# Test list_tables
result = asyncio.run(list_tables("public"))
print(result)
```

## 📝 Development

### Project Structure

```
mcp-server/
├── server.py           # Main MCP server implementation
├── config.yaml         # Server configuration
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

### Adding New Tools

With FastMCP, adding new tools is simple using decorators:

1. Create a new async function with the `@mcp.tool()` decorator:
   ```python
   @mcp.tool()
   async def my_new_tool(param1: str, param2: int = 10) -> str:
       """
       Description of what this tool does.
       
       Args:
           param1: Description of param1
           param2: Description of param2 (default: 10)
       """
       # Your implementation here
       return "Result"
   ```

2. FastMCP automatically:
   - Registers the tool
   - Generates the JSON schema from type hints
   - Uses the docstring for tool description
   - No manual registration needed!

3. Update this README with documentation

## 🐛 Troubleshooting

### Connection Issues

**Problem:** Cannot connect to database

**Solution:**
- Verify database credentials in `.env`
- Check database host is accessible
- Ensure firewall rules allow connection
- Verify PostgreSQL is running

### Tool Execution Errors

**Problem:** Tool returns error messages

**Solution:**
- Check SQL query syntax
- Verify table/schema names exist
- Ensure sufficient permissions
- Check database connection status

### Deployment Issues

**Problem:** Server fails to start on FastMCP Cloud

**Solution:**
- Verify all environment variables are set using `fastmcp env list`
- Check server logs using `fastmcp logs sql-agent-mcp-server`
- Ensure Python version is 3.10+
- Verify FastMCP is installed: `pip show fastmcp`

## 📚 Resources

- [FastMCP Documentation](https://docs.fastmcp.com/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Cloud Documentation](https://docs.fastmcp.com/cloud/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🤝 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review configuration settings
3. Check server logs
4. Contact your team administrator

## 📄 License

This MCP server is part of the SQL Agent project.

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Framework:** FastMCP  
**Platform:** FastMCP Cloud

