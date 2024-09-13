"""
Module: schema

This module combines all GraphQL queries and mutations to form the main GraphQL schema.
"""

import strawberry
from autobyteus_server.api.graphql.mutations import workspace_mutations
from autobyteus_server.api.graphql.mutations import subtask_implementation_mutations
from autobyteus_server.api.graphql.subscriptions import subtask_implementation_subscriptions
from autobyteus_server.api.graphql.queries import workspace_queries
from autobyteus_server.api.graphql.queries import code_search_queries
from autobyteus_server.api.graphql.types.llm_model_types import LLMModel

@strawberry.type
class Query(workspace_queries.Query, code_search_queries.Query):
    pass

@strawberry.type
class Mutation(
    workspace_mutations.Mutation, 
    subtask_implementation_mutations.SubtaskImplementationMutation
):
    pass

@strawberry.type
class Subscription(subtask_implementation_subscriptions.Subscription):
    pass

schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation, 
    subscription=Subscription,
    types=[LLMModel]
)
