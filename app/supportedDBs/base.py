from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

class DatabaseService(ABC):
    @property
    @abstractmethod
    def database_type(self) -> str:
        """Identifies the type of database this service handles (e.g., 'postgres', 'mysql')."""
        pass

    @abstractmethod
    async def connect(self, connection_string: str) -> None:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
    
    @abstractmethod
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_schema(self) -> List[Dict[str, Any]]:
        pass

class BaseDatabaseService(DatabaseService):
    def __init__(self):
        self._engine: Engine = None
        self._connection_string: str = None

    def database_type(self) -> str: 
        raise NotImplementedError("Database type must be implemented by specific database service") 

    async def connect(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self._engine = create_engine(connection_string)
    
    async def disconnect(self) -> None:
        if self._engine:
            self._engine.dispose()
            self._engine = None
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self._engine:
            raise Exception("Not connected to database")
        
        with self._engine.connect() as connection:
            result = connection.execute(text(query))
            return [dict(zip(result.keys(), row)) for row in result]
    
    async def get_schema(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Schema retrieval must be implemented by specific database service") 