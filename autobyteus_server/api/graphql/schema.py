"""
Module: schema

This module combines all GraphQL queries and mutations to form the main GraphQL schema.
"""

import strawberry
from autobyteus_server.api.graphql.mutations.workspace_mutations import Mutation as WorkspaceMutation
from autobyteus_server.api.graphql.mutations.workflow_step_mutations import WorkflowStepMutation
from autobyteus_server.api.graphql.mutations.file_explorer_mutations import Mutation as FileExplorerMutation
from autobyteus_server.api.graphql.mutations.api_key_mutations import Mutation as ApiKeyMutation
from autobyteus_server.api.graphql.subscriptions.workflow_step_subscriptions import Subscription as WorkflowStepSubscription
from autobyteus_server.api.graphql.queries.context_search_queries import ContextQuery
from autobyteus_server.api.graphql.queries.workspace_queries import Query as WorkspaceQuery
from autobyteus_server.api.graphql.queries.file_explorer_queries import Query as FileExplorerQuery
from autobyteus_server.api.graphql.queries.code_search_queries import Query as CodeSearchQuery
from autobyteus_server.api.graphql.queries.api_key_queries import Query as ApiKeyQuery
from autobyteus_server.api.graphql.queries.conversation_queries import Query as ConversationQuery
from autobyteus_server.api.graphql.types.llm_model_types import LLMModel

@strawberry.type
class Query(
    WorkspaceQuery,
    CodeSearchQuery,
    FileExplorerQuery,
    ApiKeyQuery,
    ConversationQuery,
    ContextQuery,
):
    pass

@strawberry.type
class Mutation(
    WorkspaceMutation,
    WorkflowStepMutation,
    FileExplorerMutation,
    ApiKeyMutation,
):
    pass

@strawberry.type
class Subscription(
    WorkflowStepSubscription,
):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    types=[LLMModel]
)