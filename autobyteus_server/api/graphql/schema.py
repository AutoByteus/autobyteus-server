"""
Module: schema

This module combines all GraphQL queries and mutations to form the main GraphQL schema.
"""

import strawberry
from autobyteus_server.api.graphql.mutations import workspace_mutations, subtask_implementation_mutations
from autobyteus_server.api.graphql.queries import workspace_queries
# Make sure to expose the LLMModel enum to GraphQL
@strawberry.type
class Query(workspace_queries.Query):
    pass

@strawberry.type
class Mutation(
    workspace_mutations.Mutation,
    subtask_implementation_mutations.SubtaskImplementationMutation
):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
