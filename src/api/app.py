from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from src.api.middleware import SessionMiddleware
from src.graphql.resolvers import resolvers
from src.graphql.schema import type_defs

schema = make_executable_schema(type_defs, resolvers)

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(SessionMiddleware),
]

app = Starlette(middleware=middleware)
graphql_app = GraphQL(schema, debug=True)

app.mount("/graphql", graphql_app)
