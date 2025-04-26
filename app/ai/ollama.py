from .base import BaseAIService
import json
import requests
from typing import Dict, Any


class OllamaAIService(BaseAIService):
    def _setup_services(self):
        self.ollama_endpoint = self.config.get("ollama_endpoint", "http://localhost:11434")
        self.model = self.config.get("ollama_model", "llama3.2")

    async def generate_sql_query(self, natural_language: str, schema: Dict[str, Any], databaseType: str) -> str:
        prompt = f"""
        You are a {databaseType} database expert. Do not respond with any information unrelated to databases or queries.
        Use the following {databaseType} database schema when creating your answers:
        {json.dumps(schema, indent=2)}
        
        Generate a valid {databaseType} SQL query that can be executed without errors against the schema for the following: {natural_language}
        
        Return only the SQL query without any explanation and do not use markdown.
        """

        try:
            response = requests.post(
                f"{self.ollama_endpoint}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return self._clean_sql_query(result["message"]["content"])
        except Exception as e:
            raise Exception(f"Failed to generate SQL query: {str(e)}")