"""
Module: schema

This module combines all GraphQL queries and mutations to form the main GraphQL schema.
"""

import strawberry
from autobyteus_server.api.graphql.mutations import workspace_mutations
from autobyteus_server.api.graphql.mutations import workflow_step_mutations
from autobyteus_server.api.graphql.mutations import file_explorer_mutations
from autobyteus_server.api.graphql.mutations import api_key_mutations
from autobyteus_server.api.graphql.subscriptions import workflow_step_subscriptions
from autobyteus_server.api.graphql.queries import workspace_queries
from autobyteus_server.api.graphql.queries import file_explorer_queries
from autobyteus_server.api.graphql.queries import code_search_queries
from autobyteus_server.api.graphql.queries import api_key_queries
from autobyteus_server.api.graphql.types.llm_model_types import LLMModel

@strawberry.type
class Query(
    workspace_queries.Query,
    code_search_queries.Query,
    file_explorer_queries.Query,
    api_key_queries.Query
):
    pass

@strawberry.type
class Mutation(
    workspace_mutations.Mutation, 
    workflow_step_mutations.WorkflowStepMutation,
    file_explorer_mutations.Mutation,
    api_key_mutations.Mutation
):
    pass

@strawberry.type
class Subscription(workflow_step_subscriptions.Subscription):
    pass

schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation, 
    subscription=Subscription,
    types=[LLMModel]
)