from typing import List, Dict, Any
from .base import BaseDatabaseService

class MySQLDatabaseService(BaseDatabaseService):
    async def get_schema(self) -> List[Dict[str, Any]]:
        if not self._engine:
            raise Exception("Not connected to database")
        
        schema_query = """
        SELECT 
            TABLE_SCHEMA as schema_name,
            TABLE_NAME as table_name,
            COLUMN_NAME as column_name,
            DATA_TYPE as data_type,
            IS_NULLABLE as is_nullable,
            COLUMN_KEY as column_key
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        
        return await self.execute_query(schema_query)
    
    async def connect(self, connection_string: str) -> None:
        # Ensure MySQL specific connection string format
        if not connection_string.startswith("mysql+pymysql://"):
            connection_string = f"mysql+pymysql://{connection_string}?ssl_disabled=true"
        await super().connect(connection_string) 

    def database_type(self) -> str: 
        return "mysql"
