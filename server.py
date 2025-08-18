from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create your FastMCP server
mcp = FastMCP("MyServer")

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Create the ASGI app
mcp_app = mcp.http_app(path='/mcp', json_response=True, stateless_http=False)

# add a status 200 check for /mcp-server/mcp

# Create a Starlette app and mount the MCP server
app = Starlette(
    routes=[
        Mount("/mcp-server", app=mcp_app),
        # Add other routes as needed
    ],
    lifespan=mcp_app.lifespan,
)
