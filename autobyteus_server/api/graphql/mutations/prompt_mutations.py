"""
Module: prompt_mutations

This module provides GraphQL mutations related to prompt operations.
"""
import logging
import strawberry
from autobyteus_server.api.graphql.types.prompt_types import Prompt, CreatePromptInput, UpdatePromptInput, MarkActivePromptInput
from autobyteus_server.prompt_engineering.services.prompt_service import PromptService

# Initialize logger with the module's name
logger = logging.getLogger(__name__)
prompt_service = PromptService()

@strawberry.type
class PromptMutation:
    @strawberry.mutation
    def create_prompt(self, input: CreatePromptInput) -> Prompt:
        """
        Creates a new prompt.
        
        Args:
            input (CreatePromptInput): The input data for creating a prompt.
            
        Returns:
            Prompt: The created prompt.
        """
        try:
            created_prompt = prompt_service.create_prompt(
                name=input.name,
                category=input.category,
                prompt_text=input.prompt_text
            )
            return Prompt(
                id=created_prompt.id,
                name=created_prompt.name,
                category=created_prompt.category,
                prompt_text=created_prompt.prompt_text,
                created_at=created_prompt.created_at,
                updated_at=created_prompt.updated_at,
                parent_prompt_id=created_prompt.parent_id
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise Exception(str(e))
        except Exception as e:
            logger.error(f"Error creating prompt: {str(e)}")
            raise Exception("Internal server error")
    
    @strawberry.mutation
    def update_prompt(self, input: UpdatePromptInput) -> Prompt:
        """
        Updates an existing prompt by prompt ID.
        
        Args:
            input (UpdatePromptInput): The input data for updating a prompt.
            
        Returns:
            Prompt: The updated prompt.
        """
        try:
            updated_prompt = prompt_service.update_prompt(
                prompt_id=input.id,
                new_prompt_text=input.new_prompt_text
            )
            return Prompt(
                id=updated_prompt.id,
                name=updated_prompt.name,
                category=updated_prompt.category,
                prompt_text=updated_prompt.prompt_text,
                created_at=updated_prompt.created_at,
                updated_at=updated_prompt.updated_at,
                parent_prompt_id=updated_prompt.parent_id
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise Exception(str(e))
        except Exception as e:
            logger.error(f"Error updating prompt: {str(e)}")
            raise Exception("Internal server error")
    
    @strawberry.mutation
    def mark_active_prompt(self, input: MarkActivePromptInput) -> Prompt:
        """
        Marks a prompt as active by prompt ID.
        
        Args:
            input (MarkActivePromptInput): The input data containing the prompt ID.
            
        Returns:
            Prompt: The prompt marked as active.
        """
        try:
            updated_prompt = prompt_service.mark_active_prompt(prompt_id=input.id)
            return Prompt(
                id=updated_prompt.id,
                name=updated_prompt.name,
                category=updated_prompt.category,
                prompt_text=updated_prompt.prompt_text,
                created_at=updated_prompt.created_at,
                updated_at=updated_prompt.updated_at,
                parent_prompt_id=updated_prompt.parent_id
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise Exception(str(e))
        except Exception as e:
            logger.error(f"Error marking prompt as active: {str(e)}")
            raise Exception("Internal server error")
