from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

import getpass
import os
from tools import search_tool, make_campaign, make_ad_set, make_ad_creative, make_ad, make_ad_image 

from dotenv import load_dotenv

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")
prompt = hub.pull("hwchase17/react")
tools = [search_tool, make_campaign, make_ad_set, make_ad_creative, make_ad, make_ad_image]

agent = create_react_agent(
    llm= llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)



    
