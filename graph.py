from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import search_tool, make_campaign, make_ad_set, make_ad_creative, make_ad, make_ad_image 
from graph_utilities import State, BasicToolNode, route_tools
import getpass 
import os
from dotenv import load_dotenv

load_dotenv()

# store api key in environment variable
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

graph_builder = StateGraph(State)

#initalize llm 
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

# provide tools 
tools = [search_tool, make_campaign, make_ad_set, make_ad_creative, make_ad, make_ad_image]

# create llm with tools that has knowledge of tool input arguments schema 
llm_with_tools = llm.bind_tools(tools)

# define various nodes of the graph 
def chatbot_with_tools(state: State):
    return {"messages":[llm_with_tools.invoke(state['messages'])]}

tool_node = BasicToolNode(tools = tools)

# create the nodes of the graph
graph_builder.add_node("chatbot_with_tools", chatbot_with_tools)
graph_builder.add_node("tools", tool_node)

# create edges of the graph
graph_builder.add_edge("tools", "chatbot_with_tools")
graph_builder.add_edge(START, "chatbot_with_tools")

graph_builder.add_conditional_edges(
    "chatbot_with_tools",
    route_tools,
    #define the output to a specific node in graph
    {"tools": "tools", END: END},
)

# create the graph
graph = graph_builder.compile()




