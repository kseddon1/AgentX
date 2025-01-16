#This file is licensed under the MIT No Attribution (MIT-0) License

from AIAgents import ConsoleChatChat, AIAgentFactory
factory = AIAgentFactory()
agent = factory.create_agent("console")
agent.interact()
