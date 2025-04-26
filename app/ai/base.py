import re
from typing import Dict, Any

class BaseAIService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._setup_services()

    def _setup_services(self):
        raise NotImplementedError("Subclasses must implement _setup_services")

    def _clean_sql_query(self, query: str) -> str:
        query = re.sub(r'```sql\n?', '', query)
        query = re.sub(r'```\n?', '', query)
        query = re.sub(r'`', '', query)
        query = re.sub(r'\n', ' ', query)
        return query.strip()