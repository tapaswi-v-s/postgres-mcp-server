# Quick Start Guide - SQL Agent MCP Server

Get your SQL Agent MCP Server (powered by FastMCP) up and running in 5 minutes!

## 🚀 Quick Setup (Local Development)

### Step 1: Install Dependencies

```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Or use the automated setup script:

```bash
cd mcp-server
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure Environment

Create a `.env` file with your database credentials:

```env
DB_HOST=your-database-host.com
DB_PORT=5432
DB_NAME=OMNI_STORE
DB_USER=your_username
DB_PASSWORD=your_password
```

### Step 3: Run the Server

```bash
# Using FastMCP dev server (recommended)
fastmcp dev server.py

# Or run directly
python -m fastmcp run server.py
```

You should see:
```
FastMCP server started successfully
Server: sql-agent-mcp-server
Tools: 6 registered
Listening for connections...
```

## ☁️ Quick Deploy (FastMCP Cloud)

### Option 1: CLI (Recommended - Fastest)

```bash
# Install FastMCP
pip install fastmcp

# Login to FastMCP Cloud
fastmcp login

# Deploy your server
cd mcp-server
fastmcp deploy --name sql-agent-mcp-server --entry server.py

# Set environment variables
fastmcp env set DB_HOST your-db-host.com
fastmcp env set DB_PORT 5432
fastmcp env set DB_NAME OMNI_STORE
fastmcp env set DB_USER your_user
fastmcp env set DB_PASSWORD your_password --secret

# Verify deployment
fastmcp status sql-agent-mcp-server
```

### Option 2: Web Dashboard (Visual)

1. **Go to** https://fastmcp.com
2. **Create New Server:**
   - Name: `sql-agent-mcp-server`
   - Framework: FastMCP
   - Upload: `server.py`, `requirements.txt`
   - Entry Point: `server.py`

3. **Add Environment Variables:**
   ```
   DB_HOST=your-db-host.com
   DB_PORT=5432
   DB_NAME=OMNI_STORE
   DB_USER=your_user
   DB_PASSWORD=your_password  (mark as secret)
   ```

4. **Click Deploy** ✅

## 🧪 Quick Test

After deployment, test your server:

```bash
# Check server status
fastmcp status sql-agent-mcp-server

# List available tools
fastmcp tools sql-agent-mcp-server

# Test a tool
fastmcp invoke sql-agent-mcp-server list_schemas

# Test with parameters
fastmcp invoke sql-agent-mcp-server list_tables \
  --args '{"schema_name": "public"}'

# View logs
fastmcp logs sql-agent-mcp-server --tail 50
```

## 📚 Available Tools

Once deployed, you can use these tools:

| Tool | Purpose | Example |
|------|---------|---------|
| `list_schemas` | List all database schemas | Lists: public, analytics, etc. |
| `list_tables` | List tables in a schema | Shows all tables in 'public' |
| `describe_table` | Show table structure | Columns, types, constraints |
| `execute_select_query` | Run SELECT queries | Query and get results |
| `execute_write_query` | Run INSERT/UPDATE/DELETE | Modify data (with confirmation) |
| `get_sample_data` | Get sample rows | Preview table data |

## 🎯 Common Use Cases

### Explore Database

```python
# List all schemas
list_schemas()

# List tables in public schema
list_tables(schema_name="public")

# See structure of users table
describe_table(table_name="users", schema_name="public")
```

### Query Data

```python
# Get sample data
get_sample_data(table_name="users", limit=10)

# Run custom query
execute_select_query(sql_query="SELECT * FROM users WHERE age > 25")
```

### Modify Data (with confirmation)

```python
# Insert data (requires confirmation)
execute_write_query(
    sql_query="INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
    confirmed=True
)
```

## ⚙️ Configuration

All settings are in `config.yaml`. Key settings:

```yaml
# Adjust query limits
tools:
  settings:
    execute_select_query:
      max_rows: 100  # Maximum rows returned

# Enable/disable security features
security:
  query_filtering:
    enabled: true
  rate_limiting:
    max_queries_per_minute: 60
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change default passwords
- [ ] Enable query filtering in `config.yaml`
- [ ] Enable rate limiting
- [ ] Use read-only database user for SELECT queries
- [ ] Never commit `.env` file
- [ ] Set `detailed_errors: false` in production

## 🐛 Troubleshooting

### Can't connect to database?

1. Check `.env` file has correct credentials
2. Verify database host is accessible
3. Test with: `psql -h DB_HOST -U DB_USER -d DB_NAME`

### Server won't start?

1. Check Python version: `python3 --version` (need 3.10+)
2. Verify all dependencies installed: `pip list`
3. Check for errors in `.env` file

### Tools return errors?

1. Verify database user has correct permissions
2. Check table/schema names are correct
3. Review logs for specific error messages

## 📖 Next Steps

- **Full Documentation:** See `README.md`
- **Deployment Guide:** See `DEPLOYMENT.md`
- **Configuration Reference:** See `config.yaml`

## 💡 Tips

1. **Start Simple:** Test locally before deploying
2. **Use Sample Data:** Use `get_sample_data()` to understand tables
3. **Check Logs:** Always review logs after deployment
4. **Monitor Performance:** Keep an eye on query execution times
5. **Regular Updates:** Keep dependencies up to date

## 🆘 Getting Help

- Check logs: `fastmcp logs sql-agent-mcp-server --tail 100 --follow`
- Test locally: `fastmcp dev server.py`
- Check status: `fastmcp status sql-agent-mcp-server`
- List tools: `fastmcp tools sql-agent-mcp-server`
- See full docs: `README.md` and `DEPLOYMENT.md`
- FastMCP Docs: https://docs.fastmcp.com

---

**Ready to go?** Start with Step 1 above! 🚀

For detailed information, see the complete [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md).

