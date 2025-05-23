from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import END
from typing_extensions import TypedDict
from typing import Annotated
import json

# define the shared state of the graph
class State(TypedDict):
    messages: Annotated[list, add_messages]


# tool node to infer tool calls and invoke the tools with provided arguments
class BasicToolNode:
    """A node that runs the tool requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}
    
    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message  = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"])
            outputs.append(
                ToolMessage(
                    content = json.dumps(tool_result),
                    name = tool_call['name'],
                    tool_call_id = tool_call['id'],
                )
            )
        return {"messages": outputs}


def route_tools(state: State):
    """ used in conditional_edge to route to the ToolNode if the last message has tool calls.
    Otherwise route to the end."""

    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls)>0:
        return "tools"
    return END


def stream_graph_updates(graph, user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)