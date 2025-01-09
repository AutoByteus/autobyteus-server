from typing import List, Optional
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord
from autobyteus_server.token_usage.models.mongodb.token_usage_record import MongoTokenUsageRecord

class MongoDBConverter:
    def to_domain_model(self, mongo_record: MongoTokenUsageRecord) -> TokenUsageRecord:
        """Convert a MongoDB TokenUsageRecord to a domain TokenUsageRecord object."""
        return TokenUsageRecord(
            conversation_id=mongo_record.conversation_id,
            conversation_type=mongo_record.conversation_type,
            role=mongo_record.role,
            token_count=mongo_record.token_count,
            cost=mongo_record.cost,
            created_at=mongo_record.created_at,
            token_usage_record_id=None,
            llm_model=mongo_record.llm_model
        )

    def to_mongo_model(self, domain_record: TokenUsageRecord) -> MongoTokenUsageRecord:
        """Convert a domain TokenUsageRecord object to a MongoDB TokenUsageRecord."""
        return MongoTokenUsageRecord(
            conversation_id=domain_record.conversation_id,
            conversation_type=domain_record.conversation_type,
            role=domain_record.role,
            token_count=domain_record.token_count,
            cost=domain_record.cost,
            created_at=domain_record.created_at,
            llm_model=domain_record.llm_model
        )

    def to_domain_models(self, mongo_records: List[MongoTokenUsageRecord]) -> List[TokenUsageRecord]:
        """Convert a list of MongoDB TokenUsageRecords to domain TokenUsageRecord objects."""
        return [self.to_domain_model(record) for record in mongo_records]

    def to_mongo_models(self, domain_records: List[TokenUsageRecord]) -> List[MongoTokenUsageRecord]:
        """Convert a list of domain TokenUsageRecords to MongoDB TokenUsageRecords."""
        return [self.to_mongo_model(record) for record in domain_records]
