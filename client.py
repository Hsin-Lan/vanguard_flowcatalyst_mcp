from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client
import asyncio
import json
from ollama import chat
from ollama import ChatResponse

# Basic connection
transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp-server")
client = Client(transport)
import random
random.seed(42)
def get_blocker_title_from_user_input(user_input: str) -> str:
    # Use a language model to extract the blocker title from user input
    
    prompt = """Your task is to extract blocker title. Here are some example:
    ---
    {{?few_shot_examples}}
    ---
    Use the examples when extract and categorize the following message:
    ---
    {{?input}}
    ---
    Extract and return a json with the follwoing keys and values:
    - "blocker_title" as extracted blocker title
    Your complete message should be a valid json string that can be read directly and only contain the keys mentioned in the list above. Never enclose it in ```json...```, no newlines, no unnessacary whitespaces.
    """


    example_template = """<example>
    {example_input}

    ## Output

    {example_output}
    </example>"""
    example1 = example_template.format(
        example_input="what does Shopping cart items without assigned supplier mean?",
        example_output=json.dumps({"blocker_title": "Shopping cart items without assigned supplier"})
    )
    example2 = example_template.format(
        example_input="explain the blocker: Missing supplier information in purchase order",
        example_output=json.dumps({"blocker_title": "Missing supplier information in purchase order"})
    )
    examples = [example1, example2]
    messages = [
        {
            'role': 'user',
            'content': user_input,
        },
        {
            'role': 'system',
            'content': prompt.replace("{{?few_shot_examples}}", "\n".join(random.sample(examples, k=1))).replace("{{?input}}", user_input)
        }
    ]
    response: ChatResponse = chat(model='qwen3:0.6b', messages=messages, think=False)
    

    # print(response['message']['content'])
    # or access fields directly from the response object
    # print(response.message.content) # retrieve blocker title and then retrieve blocker information
    return {"messages": messages, "response": response}
model = 'qwen3:0.6b'
# model = 'llama3:13b'

def organized_response(messages: list[object], response: str) -> str:
    prompt = """Your task is to form a result message based on user's query and the retrieved information.
    user's query is about asking details of a blocker in SAP signavio process insight. 
    While the retrieved information is delimited by triple backticks and sorted by similarity on blocker title.
    You should return the most relevant information to answer the user's query.
    ---
    users chat history: {{messages}}
    ---
    retrieved information: {{response}}
    ---
    example output:
    Sure! I can help you retrieve detailed information about the blocker you mentioned. Here is the information I found:
    """
    message1 = messages
    message2 = [
        {
            'role': 'system',
            'content': prompt.replace("{{messages}}", json.dumps(messages)).replace("{{response}}", response)
        }
    ]
    message2 = message1.append(message2[0])
    response: ChatResponse = chat(model='qwen3:0.6b', messages=message2, think=False)
    return response
async def main():
    async with client:
        tools = await client.list_tools()
        # tools -> list[mcp.types.Tool]
        
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            if tool.inputSchema:
                print(f"Parameters: {tool.inputSchema}")
            # Access tags and other metadata
            if hasattr(tool, 'meta') and tool.meta:
                fastmcp_meta = tool.meta.get('_fastmcp', {})
                print(f"Tags: {fastmcp_meta.get('tags', [])}")
        user_input = "Can you show me detailed description of Purchase requisition items manually created??"
        res = get_blocker_title_from_user_input(user_input)
        response = res["response"]
        # print(res.message.content[8:][:-3])
        # print(type(res.message.content))
        content = response.message.content[8:][:-3]
        json_content = json.loads(content)
        blocker_title = json_content.get("blocker_title", "Unknown")
        print("User input:", user_input)
        
        # blocker_title = json.loads(get_blocker_title_from_user_input(user_input).message.content[8:][:-4])
        result = await client.call_tool("get_blocker_by_blocker_title", {"blocker_title": blocker_title})
        final_response = organized_response(res["messages"], result.data)
        


        # result = await client.call_tool("get_blocker_by_blocker_title", {"blocker_title": "Shopping cart items without assigned supplier"})
        print("Result:", final_response)
        
        






asyncio.run(main())
