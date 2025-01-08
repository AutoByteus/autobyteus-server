
import os
import logging
from typing import List, Optional, Type
from datetime import datetime

from autobyteus_server.token_usage.models.sql.token_usage_record import TokenUsageRecord
from autobyteus_server.token_usage.provider.provider import PersistenceProvider
from autobyteus_server.token_usage.provider.provider_registry import TokenUsageProviderRegistry
from autobyteus.llm.utils.token_usage import TokenUsage

logger = logging.getLogger(__name__)

class PersistenceProxy:
    """
    Proxy for TokenUsageRecord persistence that handles provider selection and initialization.
    This is the main interface for interacting with the TokenUsageRecord persistence layer.
    """
    
    def __init__(self):
        """Initialize the TokenUsageRecord persistence proxy."""
        self._provider: Optional[PersistenceProvider] = None
        self._registry = TokenUsageProviderRegistry()
    
    @property
    def provider(self) -> PersistenceProvider:
        """
        Lazy initialization of the actual persistence provider.
        
        Returns:
            PersistenceProvider: The configured persistence provider.
        
        Raises:
            ValueError: If the configured provider is not supported.
        """
        if self._provider is None:
            self._provider = self._initialize_provider()
        return self._provider
    
    def _initialize_provider(self) -> PersistenceProvider:
        """
        Initialize the appropriate provider based on environment configuration.
        
        Returns:
            PersistenceProvider: Initialized provider instance.
        
        Raises:
            ValueError: If the configured provider is not supported.
        """
        provider_type = os.getenv('PERSISTENCE_PROVIDER', 'mongodb').lower()
        provider_class = self._registry.get_provider_class(provider_type)
        
        if not provider_class:
            available_providers = ', '.join(self._registry.get_available_providers())
            raise ValueError(
                f"Unsupported token usage persistence provider: {provider_type}. "
                f"Available providers: {available_providers}"
            )
        
        try:
            logger.info(f"Initializing TokenUsageRecord persistence provider: {provider_type}")
            return provider_class()
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {str(e)}")
            raise
    
    def create_token_usage_record(
        self,
        conversation_id: str,
        conversation_type: str,
        role: str,
        token_count: int,
        cost: float
    ) -> TokenUsageRecord:
        """
        Create and store a new TokenUsageRecord.
        
        Args:
            conversation_id (str): The ID of the conversation.
            conversation_type (str): The type of the conversation (e.g., WORKFLOW, AI_TERMINAL).
            role (str): The role of the message sender.
            token_count (int): The number of tokens used.
            cost (float): The cost associated with the tokens.
        
        Returns:
            TokenUsageRecord: The created TokenUsageRecord.
        
        Raises:
            Exception: If there is an error during creation.
        """
        try:
            record = self.provider.create_token_usage_record(
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                role=role,
                token_count=token_count,
                cost=cost
            )
            logger.info(f"Created TokenUsageRecord with ID: {record.token_usage_record_id}")
            return record
        except Exception as e:
            logger.error(f"Failed to create TokenUsageRecord: {str(e)}")
            raise

    def create_conversation_token_usage_records(
        self,
        conversation_id: str,
        conversation_type: str,
        token_usage: TokenUsage
    ) -> tuple[TokenUsageRecord, TokenUsageRecord]:
        """
        Create token usage records for both prompt and completion tokens in a conversation.
        
        Args:
            conversation_id (str): The ID of the conversation
            conversation_type (str): The type of the conversation (e.g., WORKFLOW, AI_TERMINAL)
            token_usage (TokenUsage): Token usage information containing prompt and completion details
            
        Returns:
            tuple[TokenUsageRecord, TokenUsageRecord]: Tuple containing (prompt_record, completion_record)
            
        Raises:
            Exception: If there is an error during creation
        """
        try:
            # Create prompt token usage record
            prompt_record = self.provider.create_token_usage_record(
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                role='user',
                token_count=token_usage.prompt_tokens,
                cost=token_usage.prompt_cost or 0.0
            )
            
            # Create completion token usage record
            completion_record = self.provider.create_token_usage_record(
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                role='assistant',
                token_count=token_usage.completion_tokens,
                cost=token_usage.completion_cost or 0.0
            )
            
            logger.info(
                f"Created token usage records for conversation {conversation_id}: "
                f"prompt tokens={token_usage.prompt_tokens}, "
                f"completion tokens={token_usage.completion_tokens}"
            )
            
            return prompt_record, completion_record
        except Exception as e:
            logger.error(f"Failed to create conversation token usage records: {str(e)}")
            raise
    
    def get_token_usage_records(
        self,
        conversation_id: Optional[str] = None,
        conversation_type: Optional[str] = None
    ) -> List[TokenUsageRecord]:
        """
        Retrieve TokenUsageRecords based on filters.
        
        Args:
            conversation_id (Optional[str]): Filter by conversation ID.
            conversation_type (Optional[str]): Filter by conversation type.
        
        Returns:
            List[TokenUsageRecord]: A list of TokenUsageRecords matching the filters.
        
        Raises:
            Exception: If there is an error during retrieval.
        """
        try:
            records = self.provider.get_token_usage_records(
                conversation_id=conversation_id,
                conversation_type=conversation_type
            )
            logger.info(f"Retrieved {len(records)} TokenUsageRecords")
            return records
        except Exception as e:
            logger.error(f"Failed to retrieve TokenUsageRecords: {str(e)}")
            raise
    
    def get_total_cost_in_period(self, start_date: datetime, end_date: datetime) -> float:
        """
        Calculate the total cost of tokens used within a specified period.
        
        Args:
            start_date (datetime): The start date of the period.
            end_date (datetime): The end date of the period.
        
        Returns:
            float: The total cost of tokens used.
        
        Raises:
            Exception: If there is an error during calculation.
        """
        try:
            total_cost = self.provider.get_total_cost_in_period(start_date, end_date)
            logger.info(f"Total cost from {start_date} to {end_date}: {total_cost}")
            return total_cost
        except Exception as e:
            logger.error(f"Failed to calculate total cost in period: {str(e)}")
            raise
    
    def get_total_cost_by_conversation_type(self, conversation_type: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """
        Calculate the total cost of tokens used for a specific conversation type within an optional period.
        
        Args:
            conversation_type (str): The type of conversation (e.g., WORKFLOW, AI_TERMINAL).
            start_date (Optional[datetime]): The start date of the period.
            end_date (Optional[datetime]): The end date of the period.
        
        Returns:
            float: The total cost of tokens used.
        
        Raises:
            Exception: If there is an error during calculation.
        """
        try:
            total_cost = self.provider.get_total_cost_in_period(start_date, end_date)
            logger.info(f"Total cost for conversation type '{conversation_type}' from {start_date} to {end_date}: {total_cost}")
            return total_cost
        except Exception as e:
            logger.error(f"Failed to calculate total cost for conversation type '{conversation_type}': {str(e)}")
            raise
    
    def register_provider(self, name: str, provider_class: Type[PersistenceProvider]) -> None:
        """
        Register a new TokenUsageRecord persistence provider.
        
        Args:
            name (str): The name of the provider.
            provider_class (Type[PersistenceProvider]): The provider class.
        """
        self._registry.register_provider(name, provider_class)
        logger.info(f"Registered new TokenUsageRecord persistence provider: {name}")
