"""
SQL Agent MCP Server
Model Context Protocol server for database operations and SQL query execution.
Powered by FastMCP for cloud deployment.
"""

import os
import json
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# FastMCP imports
from fastmcp import FastMCP

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Singleton class to manage database connections"""
    
    _instance = None
    _engine = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        """Initialize database connection"""
        db_host = os.getenv("DB_HOST")
        # db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        if not all([db_host, db_name, db_user, db_password]):
            raise ValueError("Missing required database environment variables")
        
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=require&channel_binding=require"
        self._engine = create_engine(connection_string, pool_pre_ping=True)
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        return self._engine
    
    def get_connection_params(self) -> Dict[str, str]:
        """Get connection parameters for psycopg2"""
        return {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "connect_timeout": 10
        }


def classify_query_type(sql_query: str) -> str:
    """
    Classify SQL query type
    Returns: DQL, DML, DDL, DCL, or TCL
    """
    sql_upper = sql_query.strip().upper()
    
    # DQL - Data Query Language
    if sql_upper.startswith("SELECT") or sql_upper.startswith("WITH"):
        return "DQL"
    
    # DML - Data Manipulation Language
    dml_keywords = ["INSERT", "UPDATE", "DELETE", "MERGE"]
    if any(sql_upper.startswith(keyword) for keyword in dml_keywords):
        return "DML"
    
    # DDL - Data Definition Language
    ddl_keywords = ["CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME"]
    if any(sql_upper.startswith(keyword) for keyword in ddl_keywords):
        return "DDL"
    
    # DCL - Data Control Language
    dcl_keywords = ["GRANT", "REVOKE"]
    if any(sql_upper.startswith(keyword) for keyword in dcl_keywords):
        return "DCL"
    
    # TCL - Transaction Control Language
    tcl_keywords = ["COMMIT", "ROLLBACK", "SAVEPOINT"]
    if any(sql_upper.startswith(keyword) for keyword in tcl_keywords):
        return "TCL"
    
    return "UNKNOWN"


# Initialize FastMCP Server
mcp = FastMCP("sql-agent-mcp-server")


# Tool Implementations

@mcp.tool()
async def list_schemas() -> str:
    """List all schemas in the OMNI_STORE database. Use this tool when you need to explore what schemas are available."""
    try:
        db = DatabaseConnection()
        engine = db.get_engine()
        inspector = inspect(engine)
        schemas = inspector.get_schema_names()
        
        # Filter out system schemas
        user_schemas = [s for s in schemas if s not in ['pg_catalog', 'information_schema', 'pg_toast']]
        
        if not user_schemas:
            return "No user schemas found in the database."
        
        result = "Available schemas in OMNI_STORE:\n"
        result += "\n".join(f"  - {schema}" for schema in user_schemas)
        return result
        
    except Exception as e:
        return f"Error listing schemas: {str(e)}"


@mcp.tool()
async def list_tables(schema_name: str = "public") -> str:
    """
    List all tables in a specific schema.
    
    Args:
        schema_name: Name of the schema to list tables from
    
    Returns:
        A formatted string containing all table names in the schema
    """
    try:
        db = DatabaseConnection()
        engine = db.get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema=schema_name)
        
        if not tables:
            return f"No tables found in schema '{schema_name}'."
        
        result = f"Tables in schema '{schema_name}':\n"
        result += "\n".join(f"  - {table}" for table in tables)
        return result
        
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
async def describe_table(table_name: str, schema_name: str = "public") -> str:
    """
    Describe the structure of a specific table including columns, types, and constraints.
    
    Args:
        table_name: Name of the table to describe
        schema_name: Name of the schema (default: "public")
    """
    try:
        db = DatabaseConnection()
        engine = db.get_engine()
        inspector = inspect(engine)
        
        # Get columns
        columns = inspector.get_columns(table_name, schema=schema_name)
        
        if not columns:
            return f"Table '{schema_name}.{table_name}' not found."
        
        result = f"Table: {schema_name}.{table_name}\n\n"
        result += "Columns:\n"
        
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col.get('default') else ""
            result += f"  - {col_name}: {col_type} {nullable} {default}\n".strip() + "\n"
        
        # Get primary keys
        pk = inspector.get_pk_constraint(table_name, schema=schema_name)
        if pk and pk.get('constrained_columns'):
            result += f"\nPrimary Key: {', '.join(pk['constrained_columns'])}\n"
        
        # Get foreign keys
        fks = inspector.get_foreign_keys(table_name, schema=schema_name)
        if fks:
            result += "\nForeign Keys:\n"
            for fk in fks:
                result += f"  - {', '.join(fk['constrained_columns'])} -> "
                result += f"{fk['referred_schema']}.{fk['referred_table']}({', '.join(fk['referred_columns'])})\n"
        
        return result
        
    except Exception as e:
        return f"Error describing table: {str(e)}"


@mcp.tool()
async def execute_select_query(sql_query: str) -> str:
    """
    Execute a SELECT query (DQL - Data Query Language) on the database.
    This tool executes queries without confirmation as they are read-only.
    
    Args:
        sql_query: The SELECT SQL query to execute
    """
    try:
        # Validate it's a SELECT query
        query_type = classify_query_type(sql_query)
        if query_type != "DQL":
            return f"Error: This tool only executes SELECT queries. Query type detected: {query_type}. Use execute_write_query for modifications."
        
        db = DatabaseConnection()
        conn_params = db.get_connection_params()
        
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql_query)
                results = cursor.fetchall()
                
                if not results:
                    return "Query executed successfully. No results returned (empty result set)."
                
                # Format results
                result_str = f"Query returned {len(results)} row(s):\n\n"
                
                # Limit display to first 100 rows
                display_results = results[:100]
                
                # Get column names
                if display_results:
                    columns = list(display_results[0].keys())
                    
                    # Create header
                    result_str += " | ".join(columns) + "\n"
                    result_str += "-" * (len(" | ".join(columns))) + "\n"
                    
                    # Add rows
                    for row in display_results:
                        result_str += " | ".join(str(row[col]) for col in columns) + "\n"
                    
                    if len(results) > 100:
                        result_str += f"\n... and {len(results) - 100} more row(s)"
                
                return result_str
                
    except Exception as e:
        return f"Error executing query: {str(e)}\n\nQuery attempted:\n{sql_query}"


@mcp.tool()
async def execute_write_query(sql_query: str, confirmed: bool = False) -> str:
    """
    Execute a write query (DML, DDL, DCL, or TCL) on the database.
    These queries modify the database and require confirmation.
    
    Args:
        sql_query: The SQL query to execute
        confirmed: Whether the user has confirmed execution (default: False)
    """
    try:
        # Classify query type
        query_type = classify_query_type(sql_query)
        
        if query_type == "DQL":
            return "Error: SELECT queries should use execute_select_query tool instead."
        
        if query_type == "UNKNOWN":
            return "Error: Unable to classify query type. Please check your SQL syntax."
        
        # Check if confirmation is needed
        if not confirmed:
            return f"""CONFIRMATION_REQUIRED
Query Type: {query_type}
SQL Query:
{sql_query}

This query will modify the database. It requires user confirmation before execution.
Please ask the user: "Do you want to proceed with this {query_type} operation? (yes/no)"
"""
        
        # Execute the query
        db = DatabaseConnection()
        conn_params = db.get_connection_params()
        
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                affected_rows = cursor.rowcount
                conn.commit()
                
                return f"Query executed successfully. {affected_rows} row(s) affected."
                
    except Exception as e:
        return f"Error executing query: {str(e)}\n\nQuery attempted:\n{sql_query}"


@mcp.tool()
async def get_sample_data(table_name: str, schema_name: str = "public", limit: int = 5) -> str:
    """
    Get sample data from a table to understand its content.
    
    Args:
        table_name: Name of the table
        schema_name: Name of the schema (default: "public")
        limit: Number of rows to return (default: 5)
    """
    try:
        sql_query = f'SELECT * FROM "{schema_name}"."{table_name}" LIMIT {limit}'
        return await execute_select_query(sql_query)
    except Exception as e:
        return f"Error getting sample data: {str(e)}"

