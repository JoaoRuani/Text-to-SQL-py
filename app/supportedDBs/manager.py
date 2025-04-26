from typing import Dict, Type
from .base import DatabaseService
from .mysql import MySQLDatabaseService
from .sqlserver import SQLServerDatabaseService
from .postgres import PostgresDatabaseService
from .oracle import OracleDatabaseService

class DatabaseManagerService:
    def __init__(self):
        self._services: Dict[str, Type[DatabaseService]] = {
            "mysql": MySQLDatabaseService,
            "sqlserver": SQLServerDatabaseService,
            "postgres": PostgresDatabaseService,
            "oracle": OracleDatabaseService
        }
        self._current_service: DatabaseService = None
    
    def get_service(self, db_type: str) -> DatabaseService:
        if db_type.lower() not in self._services:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        service_class = self._services[db_type.lower()]
        self._current_service = service_class()
        return self._current_service
    
    def get_current_service(self) -> DatabaseService:
        if not self._current_service:
            raise Exception("No database service is currently active")
        return self._current_service 