from typing import List, Any
from sqlalchemy.orm import Query
from autobyteus_server.search.search_criteria import (
    SearchCriterion,
    GroupingCriterion,
    OrderingCriterion,
    PaginationCriterion
)

class SQLSearchQueryConverter:
    def __init__(self, model: Any, initial_query: Query):
        self.model = model
        self.query = initial_query

    def apply_criteria(self, criteria: List[SearchCriterion]) -> Query:
        # Separate criteria: filters, grouping, ordering, pagination
        filter_criteria = []
        grouping_criteria = []
        ordering_criteria = []
        pagination_criteria = []

        for criterion in criteria:
            if isinstance(criterion, GroupingCriterion):
                grouping_criteria.append(criterion)
            elif isinstance(criterion, OrderingCriterion):
                ordering_criteria.append(criterion)
            elif isinstance(criterion, PaginationCriterion):
                pagination_criteria.append(criterion)
            else:
                filter_criteria.append(criterion)

        # Apply filter criteria
        for criterion in filter_criteria:
            self.query = criterion.apply_sql(self.query, self.model)

        # Apply grouping criteria
        for group_criterion in grouping_criteria:
            self.query = group_criterion.apply_sql(self.query, self.model)

        # Apply ordering criteria
        if ordering_criteria:
            for order_criterion in ordering_criteria:
                self.query = order_criterion.apply_sql(self.query, self.model)
        else:
            self.query = self.query.order_by(self.model.id)

        # Apply pagination criteria (take last one if multiple provided)
        if pagination_criteria:
            pagination = pagination_criteria[-1]
            self.query = pagination.apply_sql(self.query, self.model)

        return self.query
