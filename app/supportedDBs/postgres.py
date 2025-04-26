from typing import List, Dict, Any
from .base import BaseDatabaseService
from sqlalchemy import text

class PostgresDatabaseService(BaseDatabaseService):
    async def get_schema(self) -> List[Dict[str, Any]]:
        if not self._engine:
            raise Exception("Not connected to database")
        
        schema_query = """
        SELECT 
            table_schema as schema_name,
            table_name,
            column_name,
            data_type,
            is_nullable,
            CASE WHEN column_name IN (
                SELECT column_name 
                FROM information_schema.key_column_usage 
                WHERE table_schema = current_schema()
                AND table_name = t.table_name
            ) THEN 'PRI' ELSE '' END as column_key
        FROM information_schema.columns t
        WHERE table_schema = current_schema()
        ORDER BY table_name, ordinal_position
        """
        
        with self._engine.connect() as connection:
            result = connection.execute(text(schema_query))
            return [dict(zip(result.keys(), row)) for row in result]
    
    async def connect(self, connection_string: str) -> None:
        # Ensure PostgreSQL specific connection string format
        if not connection_string.startswith("postgresql+psycopg2://"):
            connection_string = f"postgresql+psycopg2://{connection_string}"
        await super().connect(connection_string) 

    def database_type(self) -> str: 
        return "postgres"
