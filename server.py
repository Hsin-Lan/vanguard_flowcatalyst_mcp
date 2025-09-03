from src.vf_mcpserver import vf_mcp
from starlette.applications import Starlette
from starlette.routing import Mount

# Create the ASGI app
mcp_app = vf_mcp.http_app(path='/mcp-server', json_response=True, stateless_http=False)
    
# Create a Starlette app and mount the MCP server
app = Starlette(
    routes=[
        Mount("/", app=mcp_app),
    ],
    lifespan=mcp_app.lifespan,
)
