"""
Module: search_queries

This module provides GraphQL queries related to code search operations.
"""

import json
import logging
from typing import List
import strawberry
from strawberry.scalars import JSON
from autobyteus_server.codeverse.search.search_result import SearchResult
from autobyteus_server.codeverse.search.search_service import SearchService

search_service = SearchService()
logger = logging.getLogger(__name__)

@strawberry.type
class Query:
    @strawberry.field
    def search_code_entities(self, query: str) -> JSON:
        """
        Searches for relevant code entities based on the provided query.

        Args:
            query (str): The search query.

        Returns:
            JSON: The search results.
        """
        try:
            search_result: SearchResult = search_service.search(query)
            return search_result.to_json()
        except Exception as e:
            error_message = f"Error while searching code entities: {str(e)}"
            logger.error(error_message)
            return json.dumps({"error": error_message})