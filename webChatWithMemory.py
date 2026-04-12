#This file is licensed under the MIT No Attribution (MIT-0) License

from AIAgents import WebChat, AgentType, AIAgentFactory
from Prompts import Prompt, PromptLibrary

from langchain_community.llms.ollama import Ollama
# PromptTemplate not required in 1.x – not imported

library = PromptLibrary()
factory = AIAgentFactory()
agent = factory.create_agent(AgentType.memory_web, Ollama(model="gemma4:31b"), library.prompt["simplememorychat"])
agent.build_chains()
agent.interact_with_user()
