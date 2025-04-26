from typing import List, Dict, Any
from .base import BaseDatabaseService

class OracleDatabaseService(BaseDatabaseService):
    async def get_schema(self) -> List[Dict[str, Any]]:
        if not self._engine:
            raise Exception("Not connected to database")
        
        schema_query = """
        SELECT 
            owner as schema_name,
            table_name,
            column_name,
            data_type,
            nullable as is_nullable,
            CASE WHEN column_name IN (
                SELECT column_name 
                FROM all_cons_columns 
                WHERE constraint_name IN (
                    SELECT constraint_name 
                    FROM all_constraints 
                    WHERE constraint_type = 'P'
                    AND table_name = t.table_name
                )
            ) THEN 'PRI' ELSE '' END as column_key
        FROM all_tab_columns t
        WHERE owner = USER
        ORDER BY table_name, column_id
        """
        
        return await self.execute_query(schema_query)
    
    async def connect(self, connection_string: str) -> None:
        # Ensure Oracle specific connection string format
        if not connection_string.startswith("oracle+cx_oracle://"):
            connection_string = f"oracle+cx_oracle://{connection_string}"
        await super().connect(connection_string) 