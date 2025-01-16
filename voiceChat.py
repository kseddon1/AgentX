#This file is licensed under the MIT No Attribution (MIT-0) License

from AIAgents import VoiceChat, AIAgentFactory
factory = AIAgentFactory()
agent = factory.create_agent("voice")
agent.interact()