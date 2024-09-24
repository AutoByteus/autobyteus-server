from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from autobyteus_server.api.graphql.schema import schema
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

app = FastAPI()

origins = [
    "http://localhost:3000",
    # Add other origins if required
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_router = GraphQLRouter(schema, subscription_protocols=[
    GRAPHQL_WS_PROTOCOL,
    GRAPHQL_TRANSPORT_WS_PROTOCOL,
],)
app.include_router(graphql_router, prefix="/graphql")

def graphql_server_mode(config, host, port, dev_mode=False):
    """
    Run the application in GraphQL server mode.

    :param config: Config object containing the loaded configuration.
    :param host: Server hostname.
    :param port: Server port.
    :param dev_mode: Boolean flag to enable development mode (auto-reload).
    """
    print("Running in GraphQL server mode")
    if dev_mode:
        print("Development mode enabled (auto-reload)")
        uvicorn.run("autobyteus_server.startup_mode.graphql_server_mode:app", host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    graphql_server_mode({}, "127.0.0.1", 8000, False)
    