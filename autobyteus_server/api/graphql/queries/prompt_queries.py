"""
Module: prompt_queries

This module provides GraphQL queries related to prompt operations.
"""
import logging
from typing import List, Optional
import strawberry
from autobyteus_server.api.graphql.types.prompt_types import Prompt
from autobyteus_server.prompt_engineering.services.prompt_service import PromptService

logger = logging.getLogger(__name__)
prompt_service = PromptService()

@strawberry.type
class PromptQuery:
    @strawberry.field
    def activePrompts(self) -> List[Prompt]:
        """
        Fetches all active prompts.
        
        Returns:
            List[Prompt]: A list of all active prompts.
        """
        try:
            domain_prompts = prompt_service.get_all_active_prompts()
            return [
                Prompt(
                    id=p.id,
                    name=p.name,
                    category=p.category,
                    prompt_text=p.prompt_text,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    parent_prompt_id=p.parent_id
                ) for p in domain_prompts
            ]
        except Exception as e:
            logger.error(f"Error fetching prompts: {str(e)}")
            raise Exception("Unable to fetch prompts at this time.")
    
    @strawberry.field
    def promptDetails(self, id: str) -> Optional[Prompt]:
        """
        Fetch a single prompt by its ID.
        
        Args:
            id (str): The ID of the prompt.
            
        Returns:
            Optional[Prompt]: The prompt if found, otherwise None.
        """
        try:
            domain_prompt = prompt_service.get_prompt_by_id(id)
            return Prompt(
                id=domain_prompt.id,
                name=domain_prompt.name,
                category=domain_prompt.category,
                prompt_text=domain_prompt.prompt_text,
                created_at=domain_prompt.created_at,
                updated_at=domain_prompt.updated_at,
                parent_prompt_id=domain_prompt.parent_id
            )
        except ValueError:
            # If prompt not found, return None
            return None
        except Exception as e:
            logger.error(f"Error fetching prompt by ID: {str(e)}")
            raise Exception("Unable to fetch prompt at this time.")
