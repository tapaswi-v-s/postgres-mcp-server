# Deployment Guide for SQL Agent MCP Server

This guide provides detailed instructions for deploying the SQL Agent MCP Server to FastMCP Cloud.

> **Note:** This server uses FastMCP, a modern Python framework for building MCP servers with a streamlined API and excellent cloud deployment support.

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] PostgreSQL database set up and accessible
- [ ] Database credentials (host, port, name, user, password)
- [ ] FastMCP Cloud account created (https://fastmcp.com)
- [ ] Python 3.10+ installed locally for testing
- [ ] FastMCP CLI installed (`pip install fastmcp`)
- [ ] All dependencies tested locally

## 🔧 Configuration Steps

### 1. Database Setup

Ensure your PostgreSQL database is properly configured:

```sql
-- Verify database exists
SELECT datname FROM pg_database WHERE datname = 'OMNI_STORE';

-- Create user if needed (optional)
CREATE USER your_user WITH PASSWORD 'your_password';

-- Grant permissions
GRANT CONNECT ON DATABASE OMNI_STORE TO your_user;
GRANT USAGE ON SCHEMA public TO your_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
```

### 2. Environment Variables Configuration

Create a secure list of environment variables for mcp-cloud.ai:

```env
# Required Variables
DB_HOST=your-production-db-host.com
DB_PORT=5432
DB_NAME=OMNI_STORE
DB_USER=your_db_user
DB_PASSWORD=your_secure_password

# Optional Variables
LOG_LEVEL=INFO
```

### 3. Review config.yaml

Update the following sections in `config.yaml` for production:

```yaml
deployment:
  environment: "production"  # Change from development

security:
  query_filtering:
    enabled: true  # Ensure enabled
  rate_limiting:
    enabled: true
    max_queries_per_minute: 60  # Adjust based on needs

error_handling:
  detailed_errors: false  # Disable detailed errors in production
```

## 🚀 Deployment Methods

### Method 1: Using FastMCP CLI (Recommended)

1. **Install FastMCP CLI:**
   ```bash
   pip install fastmcp
   ```

2. **Test locally first:**
   ```bash
   cd mcp-server
   
   # Set environment variables for local testing
   export DB_HOST=your-db-host.com
   export DB_PORT=5432
   export DB_NAME=OMNI_STORE
   export DB_USER=your_user
   export DB_PASSWORD=your_password
   
   # Run the server locally
   fastmcp run server.py
   ```

3. **Authenticate with FastMCP Cloud:**
   ```bash
   fastmcp login
   ```

4. **Deploy to FastMCP Cloud:**
   ```bash
   fastmcp deploy \
     --name sql-agent-mcp-server \
     --entry server.py
   ```

5. **Set environment variables in cloud:**
   ```bash
   fastmcp env set DB_HOST your-db-host.com
   fastmcp env set DB_PORT 5432
   fastmcp env set DB_NAME OMNI_STORE
   fastmcp env set DB_USER your_user
   fastmcp env set DB_PASSWORD your_password --secret
   ```

6. **Verify deployment:**
   ```bash
   fastmcp status sql-agent-mcp-server
   fastmcp logs sql-agent-mcp-server --tail 50
   ```

### Method 2: Using FastMCP Cloud Dashboard

1. **Navigate to FastMCP Cloud:**
   - Go to https://fastmcp.com
   - Log in to your account

2. **Create New Project:**
   - Click "New Server" or "Deploy"
   - Name: `sql-agent-mcp-server`
   - Description: "PostgreSQL database operations MCP server"
   - Framework: FastMCP

3. **Upload Files:**
   Upload the following files:
   - `server.py`
   - `requirements.txt`
   
   **Optional:**
   - `config.yaml`
   - `README.md`
   
   **Do NOT upload:**
   - `.env` (use environment variables instead)
   - `.gitignore`
   - `__pycache__/`

4. **Configure Settings:**
   - Entry Point: `server.py`
   - Runtime: Python 3.10+
   - Memory: 512MB (minimum)
   - CPU: 0.5 vCPU
   - Timeout: 60 seconds

5. **Set Environment Variables:**
   In the project settings, add:
   - `DB_HOST` = your-db-host.com
   - `DB_PORT` = 5432
   - `DB_NAME` = OMNI_STORE
   - `DB_USER` = your_user
   - `DB_PASSWORD` = your_password (mark as secret/sensitive)

6. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note the server endpoint URL
   - FastMCP will automatically discover all tools via decorators

### Method 3: Using Git Integration

FastMCP Cloud supports Git-based deployments:

1. **Create a Git repository:**
   ```bash
   cd mcp-server
   git init
   git add .
   git commit -m "Initial FastMCP server setup"
   ```

2. **Connect to remote repository:**
   ```bash
   git remote add origin https://github.com/your-org/sql-agent-mcp.git
   git push -u origin main
   ```

3. **Connect FastMCP Cloud to repository:**
   - In FastMCP dashboard, select "Connect Repository"
   - Authorize GitHub/GitLab access
   - Select your repository
   - Set build configuration:
     - Root directory: `/`
     - Entry point: `server.py`
     - Install command: `pip install -r requirements.txt`
     - Framework: FastMCP (auto-detected)

4. **Configure environment variables** (same as Method 2)

5. **Enable auto-deployment:**
   - Enable automatic deployments on push to main branch
   - Set up preview deployments for pull requests (optional)
   - Configure deployment branch rules if needed

## ✅ Post-Deployment Verification

### 1. Health Check

Test the server using FastMCP CLI:

```bash
# Check server status
fastmcp status sql-agent-mcp-server

# List available tools
fastmcp tools sql-agent-mcp-server

# Test a specific tool
fastmcp invoke sql-agent-mcp-server list_schemas
```

Or use the MCP Inspector:
```bash
fastmcp inspect sql-agent-mcp-server
```

### 2. Test Basic Tools

Use FastMCP CLI to test tools:

```bash
# Test list_schemas
fastmcp invoke sql-agent-mcp-server list_schemas

# Test list_tables
fastmcp invoke sql-agent-mcp-server list_tables \
  --args '{"schema_name": "public"}'

# Test describe_table
fastmcp invoke sql-agent-mcp-server describe_table \
  --args '{"table_name": "users", "schema_name": "public"}'
```

### 3. Monitor Logs

Check server logs for any errors:

```bash
fastmcp logs sql-agent-mcp-server --tail 100 --follow
```

### 4. Performance Testing

Run load tests to ensure server handles expected traffic:

```bash
# Example using Apache Bench
ab -n 100 -c 10 https://your-server.mcp-cloud.ai/health
```

## 🔄 Updates and Rollbacks

### Deploying Updates

1. **Test changes locally first:**
   ```bash
   cd mcp-server
   
   # Run with FastMCP dev server
   fastmcp dev server.py
   
   # Or run directly
   python -m fastmcp run server.py
   ```

2. **Deploy update:**
   ```bash
   fastmcp deploy sql-agent-mcp-server
   ```

3. **Verify deployment:**
   - Check health endpoint
   - Test critical tools
   - Monitor logs for errors

### Rolling Back

If issues occur after deployment:

```bash
# List previous deployments
fastmcp deployments sql-agent-mcp-server

# Rollback to previous version
fastmcp rollback sql-agent-mcp-server --version v1.0.0

# Or rollback to last successful deployment
fastmcp rollback sql-agent-mcp-server --last-stable
```

## 📊 Monitoring and Maintenance

### Set Up Monitoring

1. **Enable monitoring in config.yaml:**
   ```yaml
   deployment:
     monitoring:
       enabled: true
       metrics_endpoint: "/metrics"
   ```

2. **Configure alerts:**
   - Error rate > 5%
   - Response time > 5 seconds
   - Database connection failures
   - Rate limit exceeded

### Regular Maintenance

- **Weekly:**
  - Review error logs
  - Check performance metrics
  - Verify database connection health

- **Monthly:**
  - Update dependencies
  - Review and rotate credentials
  - Optimize queries if needed

- **Quarterly:**
  - Security audit
  - Load testing
  - Capacity planning

## 🛡️ Security Considerations

### Database Security

1. **Use read-only user for SELECT queries:**
   ```sql
   CREATE USER readonly_user WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE OMNI_STORE TO readonly_user;
   GRANT USAGE ON SCHEMA public TO readonly_user;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
   ```

2. **Enable SSL/TLS:**
   ```yaml
   database:
     ssl_mode: "require"
   ```

### Network Security

1. **Enable IP whitelisting:**
   ```yaml
   security:
     ip_whitelist:
       - "1.2.3.4"
       - "5.6.7.8"
   ```

2. **Use VPN or private network** when connecting to database

### Application Security

1. **Rotate credentials regularly**
2. **Use strong passwords**
3. **Enable query filtering**
4. **Monitor for suspicious activity**
5. **Keep dependencies updated**

## 🐛 Troubleshooting Deployment Issues

### Issue: Deployment Fails

**Possible Causes:**
- Missing dependencies
- Syntax errors in code
- Invalid configuration

**Solutions:**
1. Check deployment logs
2. Verify requirements.txt is complete
3. Test locally first
4. Validate config.yaml syntax

### Issue: Database Connection Fails

**Possible Causes:**
- Incorrect credentials
- Network/firewall issues
- Database not accessible from mcp-cloud.ai

**Solutions:**
1. Verify environment variables are set correctly
2. Check database host is publicly accessible or use VPN
3. Whitelist mcp-cloud.ai IP addresses in database firewall
4. Test connection from mcp-cloud.ai network

### Issue: Tools Return Errors

**Possible Causes:**
- Insufficient database permissions
- Table/schema doesn't exist
- Query timeout

**Solutions:**
1. Verify database user has required permissions
2. Check table and schema names
3. Increase timeout in config.yaml
4. Review query complexity

### Issue: Performance Problems

**Possible Causes:**
- Insufficient resources
- Database connection pool too small
- Slow queries

**Solutions:**
1. Increase server memory/CPU
2. Adjust connection pool size in config.yaml
3. Add database indexes
4. Optimize queries
5. Enable query caching

## 📞 Support Resources

### Documentation
- [FastMCP Documentation](https://docs.fastmcp.com/)
- [MCP Protocol Docs](https://modelcontextprotocol.io/)
- [FastMCP Cloud Docs](https://docs.fastmcp.com/cloud/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

### Community
- FastMCP Support: support@fastmcp.com
- FastMCP Discord: https://discord.gg/fastmcp
- GitHub Issues: (your-repo-url)
- Community Forum: https://community.fastmcp.com

### Emergency Contacts
- Database Admin: (contact)
- DevOps Team: (contact)
- On-call Engineer: (contact)

## 📝 Deployment Checklist Summary

Pre-deployment:
- [ ] Database tested and accessible
- [ ] Environment variables prepared
- [ ] config.yaml reviewed for production
- [ ] Local testing completed
- [ ] Dependencies verified

Deployment:
- [ ] Files uploaded to mcp-cloud.ai
- [ ] Environment variables configured
- [ ] Server deployed successfully
- [ ] Health check passed

Post-deployment:
- [ ] Tools tested and verified
- [ ] Logs monitored for errors
- [ ] Performance metrics reviewed
- [ ] Documentation updated
- [ ] Team notified of deployment

---

**Document Version:** 1.0.0  
**Last Updated:** December 2025  
**Next Review:** March 2026

