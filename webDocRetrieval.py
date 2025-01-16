#This file is licensed under the MIT No Attribution (MIT-0) License

from AIAgents import WebChat, AgentType, AIAgentFactory
from Prompts import Prompt, PromptLibrary

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

library = PromptLibrary()
factory = AIAgentFactory()
agent = factory.create_agent(AgentType.document_web, Ollama(model="llama3.2"), library.prompt["simplememorychat"])
agent.interact_with_user()
