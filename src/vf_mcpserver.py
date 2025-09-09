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

chroma_handler = ChromaHandler()

@vf_mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

@vf_mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@vf_mcp.tool
def get_blocker_by_blocker_title(blocker_title: str) -> str | None:
    """
    Retrieve blocker information by blocker title.
    
    Args:
        blocker_title (str): blocker title
    
    Returns:
        str: blocker information 
    """
    
    # make a request to ChromaDB
    data = make_request_to_chroma(blocker_title)
    return format_chroma_response(data)

def make_request_to_chroma(querystr: str, ids=[]):
    try: 
        # chroma_handler = ChromaHandler()
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

@vf_mcp.tool
def get_blocker_by_blocker_title_with_lev_and_embedding(i_blocker_title: str) -> str | None:
    """
    Retrieve blocker information by blocker title.
    
    Args:
        blocker_title (str): blocker title
    
    Returns:
        str: blocker information 
    """
    sorted_blocker_infos = calculate_lev_distance_for_i_blocker_title(i_blocker_title)
    data = make_request_to_chroma(
        querystr=i_blocker_title,
        ids=[sorted_blocker_info[2] for sorted_blocker_info in sorted_blocker_infos]
    )
    return format_chroma_response(data)

def format_chroma_response(data):
    if not data or "metadatas" not in data:
        return "Unable to fetch blocker information or no blockers found."
    
    if not data["metadatas"]:
        return "No blockers found for this query."
    
    blockers_info = [format_blocker_info(item) for item in data["metadatas"][0]]
    return "\n---\n".join(blockers_info)

def calculate_lev_distance_for_i_blocker_title(i_blocker_title):
    import Levenshtein
    blocker_collection_data = chroma_handler.get_collection_data()
    blocker_titles = blocker_collection_data["documents"]
    blocker_ids = blocker_collection_data["ids"]
    
    sorted_blocker_infos = []
    for i in range(len(blocker_titles)):
        lev_distance = Levenshtein.distance(i_blocker_title, blocker_titles[i])
        sorted_blocker_infos.append([lev_distance, blocker_titles[i], blocker_ids[i]])
    sorted_blocker_infos.sort(key=lambda x: x[0])
    sorted_blocker_infos = sorted_blocker_infos[:5] # fetch top 5
    return sorted_blocker_infos