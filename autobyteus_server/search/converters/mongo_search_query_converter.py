from typing import List
from pymongo import ASCENDING, DESCENDING
from autobyteus_server.search.search_criteria import (
    SearchCriterion,
    OrderingCriterion,
    PaginationCriterion
)

class MongoSearchQueryConverter:
    def __init__(self, collection, model_class):
        self.collection = collection
        self.model_class = model_class
        self.query_filter = {}
        self.ordering_criteria = []
        self.pagination_criteria = []

    def apply_criteria(self, criteria: List[SearchCriterion]):
        # Separate criteria: ordering, pagination, others as filters
        for criterion in criteria:
            if isinstance(criterion, OrderingCriterion):
                self.ordering_criteria.append(criterion)
            elif isinstance(criterion, PaginationCriterion):
                self.pagination_criteria.append(criterion)
            else:
                criterion.apply_mongo(self.query_filter)

        cursor = self.collection.find(self.query_filter)

        # Apply ordering if criteria present
        if self.ordering_criteria:
            for order_criterion in self.ordering_criteria:
                sort_order = ASCENDING if order_criterion.ascending else DESCENDING
                cursor = cursor.sort(order_criterion.field, sort_order)
        else:
            cursor = cursor.sort("_id", ASCENDING)

        # Apply pagination from last pagination criterion if available
        if self.pagination_criteria:
            pagination = self.pagination_criteria[-1]
            cursor = cursor.skip(pagination.offset).limit(pagination.limit)

        return cursor
