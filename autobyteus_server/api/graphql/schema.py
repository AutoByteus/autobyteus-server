"""
Module: schema
This module combines all GraphQL queries and mutations to form the main GraphQL schema.
"""
import strawberry
from autobyteus_server.api.graphql.mutations import workspace_mutations
from autobyteus_server.api.graphql.mutations import workflow_step_mutations
from autobyteus_server.api.graphql.mutations import file_explorer_mutations
from autobyteus_server.api.graphql.mutations import llm_provider_mutations
from autobyteus_server.api.graphql.mutations import prompt_mutations
from autobyteus_server.api.graphql.mutations import server_settings_mutations  # New import
from autobyteus_server.api.graphql.subscriptions import workflow_step_subscriptions
from autobyteus_server.api.graphql.queries import (
    context_search_queries,
    workspace_queries,
    file_explorer_queries,
    code_search_queries,
    conversation_queries,
    llm_provider_queries,
    token_usage_statistics_query,
    prompt_queries,
    server_settings_queries  # New import
)

@strawberry.type
class Query(
    workspace_queries.Query,
    code_search_queries.Query,
    file_explorer_queries.Query,
    conversation_queries.Query,
    context_search_queries.ContextQuery,
    llm_provider_queries.Query,
    token_usage_statistics_query.TokenUsageStatisticsQuery,
    prompt_queries.PromptQuery,
    server_settings_queries.Query,  # Add ServerSettingsQuery
):
    pass

@strawberry.type
class Mutation(
    workspace_mutations.Mutation,
    workflow_step_mutations.WorkflowStepMutation,
    file_explorer_mutations.Mutation,
    llm_provider_mutations.Mutation,
    prompt_mutations.PromptMutation,
    server_settings_mutations.Mutation,  # Add ServerSettingsMutation
):
    pass

@strawberry.type
class Subscription(
    workflow_step_subscriptions.Subscription,
):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
