from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Query

class SearchCriterion(ABC):
    def __init__(self, field: str):
        self.field = field

    @abstractmethod
    def apply_sql(self, query: Query, model: Any) -> Query:
        """Apply this criterion to an SQLAlchemy query."""
        pass

    @abstractmethod
    def apply_mongo(self, query_filter: dict) -> None:
        """Modify the MongoDB filter dict to include this criterion."""
        pass

class EqualCriterion(SearchCriterion):
    def __init__(self, field: str, value: Any):
        super().__init__(field)
        self.value = value

    def apply_sql(self, query: Query, model: Any) -> Query:
        if hasattr(model, self.field):
            return query.filter(getattr(model, self.field) == self.value)
        raise ValueError(f"Model {model} has no attribute '{self.field}'")

    def apply_mongo(self, query_filter: dict) -> None:
        query_filter[self.field] = self.value

class RangeCriterion(SearchCriterion):
    def __init__(self, field: str, start: Any = None, end: Any = None):
        super().__init__(field)
        self.start = start
        self.end = end

    def apply_sql(self, query: Query, model: Any) -> Query:
        if not hasattr(model, self.field):
            raise ValueError(f"Model {model} has no attribute '{self.field}'")
        column = getattr(model, self.field)
        if self.start is not None:
            query = query.filter(column >= self.start)
        if self.end is not None:
            query = query.filter(column <= self.end)
        return query

    def apply_mongo(self, query_filter: dict) -> None:
        range_filter = {}
        if self.start is not None:
            range_filter["$gte"] = self.start
        if self.end is not None:
            range_filter["$lte"] = self.end
        if range_filter:
            query_filter[self.field] = range_filter

class OrderingCriterion(SearchCriterion):
    def __init__(self, field: str, ascending: bool = True):
        super().__init__(field)
        self.ascending = ascending

    def apply_sql(self, query: Query, model: Any) -> Query:
        if hasattr(model, self.field):
            column = getattr(model, self.field)
            return query.order_by(column if self.ascending else column.desc())
        raise ValueError(f"Model {model} has no attribute '{self.field}'")

    def apply_mongo(self, query_filter: dict) -> None:
        # Ordering is handled separately in Mongo queries
        pass

class PaginationCriterion(SearchCriterion):
    def __init__(self, offset: int = 0, limit: int = 10):
        super().__init__(field="__pagination__")
        self.offset = offset
        self.limit = limit

    def apply_sql(self, query: Query, model: Any) -> Query:
        return query.offset(self.offset).limit(self.limit)

    def apply_mongo(self, query_filter: dict) -> None:
        # Pagination is applied outside of filter construction in Mongo queries
        pass

class GroupingCriterion(SearchCriterion):
    def __init__(self, field: str):
        super().__init__(field)

    def apply_sql(self, query: Query, model: Any) -> Query:
        if hasattr(model, self.field):
            return query.group_by(getattr(model, self.field))
        raise ValueError(f"Model {model} has no attribute '{self.field}'")

    def apply_mongo(self, query_filter: dict) -> None:
        # Grouping for MongoDB would require aggregation which is not implemented here
        pass
