from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import search_tool, make_campaign, make_ad_set, make_ad_creative, make_ad, make_ad_image 
from typing import Annotated
from typing_extensions import TypedDict
from graph_utilities import BasicToolNode, route_tools
import getpass 
import os

from dotenv import load_dotenv
load_dotenv()

# store api key in environment variable
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

if "TAVILY_API_KEY" not in os.environ:
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter your Tavily API key: ")

class State(TypedDict):

    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

tools = [search_tool, make_campaign, make_ad_set, make_ad_creative, make_ad, make_ad_image]

llm_with_tools = llm.bind_tools(tools)

def chatbot_with_tools(state: State):
    return {"messages":[llm_with_tools.invoke(state['messages'])]}

tool_node = BasicToolNode(tools = tools)


graph_builder.add_node("chatbot_with_tools", chatbot_with_tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge("tools", "chatbot_with_tools")
graph_builder.add_edge(START, "chatbot_with_tools")

graph_builder.add_conditional_edges(
    "chatbot_with_tools",
    route_tools,
    #define the output to a specific node in graph
    {"tools": "tools", END: END},
)

graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


