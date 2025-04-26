from typing import List, Dict, Any
from .base import BaseDatabaseService

class SQLServerDatabaseService(BaseDatabaseService):
    async def get_schema(self) -> List[Dict[str, Any]]:
        if not self._engine:
            raise Exception("Not connected to database")
        
        schema_query = """
        SELECT 
            SCHEMA_NAME(t.schema_id) as schema_name,
            t.name as table_name,
            c.name as column_name,
            ty.name as data_type,
            c.is_nullable as is_nullable,
            CASE WHEN pk.column_id IS NOT NULL THEN 'PRI' ELSE '' END as column_key
        FROM sys.tables t
        INNER JOIN sys.columns c ON t.object_id = c.object_id
        INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
        LEFT JOIN (
            SELECT ic.column_id, ic.object_id
            FROM sys.index_columns ic
            INNER JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
            WHERE i.is_primary_key = 1
        ) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
        ORDER BY t.name, c.column_id
        """
        
        return await self.execute_query(schema_query)
    
    async def connect(self, connection_string: str) -> None:
        # Ensure SQL Server specific connection string format
        if not connection_string.startswith("mssql+pyodbc://"):
            connection_string = f"mssql+pyodbc://{connection_string}"
        await super().connect(connection_string) 