
from typing import List
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord
from autobyteus_server.token_usage.models.sql.token_usage_record import TokenUsageRecord as SQLTokenUsageRecord
import uuid
from datetime import datetime

class SQLConverter:
    def to_domain_model(self, sql_record: SQLTokenUsageRecord) -> TokenUsageRecord:
        """Convert a SQL TokenUsageRecord to a domain TokenUsageRecord object."""
        return TokenUsageRecord(
            conversation_id=sql_record.conversation_id,
            conversation_type=sql_record.conversation_type,
            role=sql_record.role,
            token_count=sql_record.token_count,
            cost=sql_record.cost,
            created_at=sql_record.created_at,
            token_usage_record_id=sql_record.usage_record_id
        )

    def to_sql_model(self, domain_record: TokenUsageRecord) -> SQLTokenUsageRecord:
        """Convert a domain TokenUsageRecord object to a SQL TokenUsageRecord."""
        return SQLTokenUsageRecord(
            usage_record_id=domain_record.token_usage_record_id or str(uuid.uuid4()),
            conversation_id=domain_record.conversation_id,
            conversation_type=domain_record.conversation_type,
            role=domain_record.role,
            token_count=domain_record.token_count,
            cost=domain_record.cost,
            created_at=domain_record.created_at or datetime.utcnow()
        )

    def to_domain_models(self, sql_records: List[SQLTokenUsageRecord]) -> List[TokenUsageRecord]:
        """Convert a list of SQL TokenUsageRecords to domain TokenUsageRecord objects."""
        return [self.to_domain_model(record) for record in sql_records]

    def to_sql_models(self, domain_records: List[TokenUsageRecord]) -> List[SQLTokenUsageRecord]:
        """Convert a list of domain TokenUsageRecords to SQL TokenUsageRecords."""
        return [self.to_sql_model(record) for record in domain_records]
