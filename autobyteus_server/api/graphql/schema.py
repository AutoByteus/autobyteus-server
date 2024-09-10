"""
Module: schema

This module combines all GraphQL queries and mutations to form the main GraphQL schema.
"""

import strawberry
from autobyteus_server.api.graphql.mutations import workspace_mutations

from autobyteus_server.api.graphql.queries import workspace_queries

@strawberry.type
class Query(workspace_queries.Query):
    pass

@strawberry.type
class Mutation(workspace_mutations.Mutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
