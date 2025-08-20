from contextlib import asynccontextmanager

from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from fastadmin import fastapi_app as admin_app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.auth_middleware import AuthenticationMiddleware
from src.api.middleware import SessionMiddleware
from src.graphql.directives.auth import RequiresAuthDirective, RequiresRoleDirective
from src.graphql.resolvers import resolvers
from src.graphql.schema import type_defs

schema = make_executable_schema(
    type_defs,
    resolvers,
    directives={
        "requiresAuth": RequiresAuthDirective,
        "requiresRole": RequiresRoleDirective,
    },
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Import admin config to register models
    from src.admin import config

    yield
    # Shutdown


app = FastAPI(
    title="Radmind Backend API",
    description="FastAPI backend with GraphQL and Admin interface",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware)

# Add custom session middleware
app.add_middleware(SessionMiddleware)


@app.get("/")
async def health_check():
    return {"status": "ok"}


# Mount GraphQL
graphql_app = GraphQL(schema, debug=False)
app.mount("/graphql", graphql_app)

# Mount Admin interface
app.mount("/admin", admin_app)
