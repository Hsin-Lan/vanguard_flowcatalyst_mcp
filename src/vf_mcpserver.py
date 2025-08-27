from fastmcp import FastMCP
from src.vfchromaapi.chroma_handler import ChromaHandler
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create your FastMCP server
vf_mcp = FastMCP(
    name="VanguardFlowCatalystAssistant",
    instructions="""
        This server provides data retrieval tools.
        Call get_blocker_by_blocker_title(blocker_title) to get blocker information by blocker title.
    """
)

@vf_mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

@vf_mcp.tool
def get_blocker_by_blocker_title(blocker_title: str) -> str | None:
    """
    Retrieve blocker information by blocker title.
    """
    
    # make a request to ChromaDB
    data = make_request_to_chroma(blocker_title)
    if not data or "metadatas" not in data:
        return "Unable to fetch blocker information or no blockers found."
    
    if not data["metadatas"]:
        return "No blockers found for this query."
    
    blockers_info = [format_blocker_info(item) for item in data["metadatas"][0]]
    return "\n---\n".join(blockers_info)

def make_request_to_chroma(querystr: str):
    try: 
        chroma_handler = ChromaHandler()
        result = chroma_handler.query(querystr)
    except Exception as e:
        print(f"Error initializing ChromaHandler: {e}")
        return None
    return result

def format_blocker_info(metadata: dict) -> str:
    """
    Format the blocker information retrieved into a readable string.
    """
    # documents = blocker_info["documents"]
    return f"""
    Process Flow: {metadata.get('process_flow', 'Unknown')}
    Stage Title: {metadata.get('stage_title', 'Unknown')}
    Stage Description: {metadata.get('stage_description', 'Unknown')}
    Blocker Title: {metadata.get('blocker_title', 'Unknown')}
    Blocker Description: {metadata.get('blocker_description', 'Unknown')}
    """
    