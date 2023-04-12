import os

import openai
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents import load_tools
from langchain.callbacks.base import CallbackManager
from langchain.llms import OpenAI

# Set up your API key for OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

manager = CallbackManager([])

llm = OpenAI(temperature=0, callback_manager=manager, verbose=True)

tools = load_tools(["serpapi", "llm-math"], llm=llm)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run(
    "Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"
)
