from mistralai import Mistral
from .base import BaseAIService
from typing import Dict, Any
import json


class MistralAIService(BaseAIService):
    def _setup_services(self):
        self.api_key = self.config.get("mistral_api_key")
        if not self.api_key:
            raise ValueError("Mistral API key not found in config.")

        self.model = self.config.get("mistral_model", "mistral-small-latest")
        self.client = Mistral(api_key=self.api_key)

    async def generate_sql_query(self, natural_language: str, schema: Dict[str, Any], databaseType: str) -> str:
        prompt = f"""
        You are a {databaseType} database expert. Do not respond with any information unrelated to databases or queries.
        Use the following {databaseType} database schema when creating your answers:
        {json.dumps(schema, indent=2)}

        Generate a valid {databaseType} SQL query that can be executed without errors against the schema for the following: {natural_language}

        Return only the SQL query without any explanation and do not use markdown.
        """

        try:
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )

            query_content = response.choices[0].message.content
            return self._clean_sql_query(query_content)

        except Exception as e:
            raise Exception(f"Failed to generate SQL query using Mistral client: {str(e)}")