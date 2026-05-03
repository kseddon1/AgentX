# AIAgents.py
import pyttsx3
import speech_recognition as sr
import ollama 
import sounddevice as sd
import scipy.io.wavfile as wav
import os
import numpy as np
import json
from enum import Enum

# --- Tool Registry System ---
class ToolRegistry:
    """Registry to hold functions that the AI can call."""
    def __init__(self):
        self.tools = {}

    def register(self, name, func, description):
        self.tools[name] = {"func": func, "description": description}

    def get_tool_definitions(self):
        """Returns a string description of all tools for the LLM prompt."""
        defs = []
        for name, info in self.tools.items():
            defs.append(f"- {name}: {info['description']}")
        return "\n".join(defs)

    def call_tool(self, tool_name, args_str):
        if tool_name in self.tools:
            try:
                # Convert args_str (e.g., '"New York"') to Python object
                args = json.loads(args_str) if args_str else None
                return self.tools[tool_name]["func"](args)
            except Exception as e:
                return f"Error executing tool {tool_name}: {str(e)}"
        return f"Tool {tool_name} not found."

# --- Example Tool Implementations ---
def get_weather(city):
    # In a real app, you would call a weather API here
    return f"The weather in {city} is currently 72°F and sunny."

def open_app(app_name):
    # In a real app, you would use os.system or subprocess to open apps
    print(f"--- System: Opening {app_name}... ---")
    return f"Successfully opened {app_name}."

# Global registry instance
registry = ToolRegistry()
registry.register("get_weather", get_weather, "Get current weather. Arg: City name as string.")
registry.register("open_app", open_app, "Open a system application. Arg: App name as string.")

class AgentType(str, Enum):
    console = "console"
    memory_console = "memoryconsole"
    voice = "voice"
    memory_voice = "memoryvoice"
    web = "web"
    memory_web = "memoryweb"

class AIAgent:
    def __init__(self):
        self.model_name = ""
        self.prompt_text = ""
        self.tool_registry = registry

    def set_prompt(self, prompt_obj):
        self.prompt_text = prompt_obj.text if hasattr(prompt_obj, 'text') else prompt_obj

    def set_llm(self, model_name):
        self.model_name = model_name

    def execute_chain(self, user_input):
        # Tool-aware prompt logic
        tool_defs = self.tool_registry.get_tool_definitions()
        system_instructions = (
            f"{self.prompt_text}\n\n"
            f"AVAILABLE TOOLS:\n{tool_defs}\n\n"
            "If you need to use a tool to answer the user, respond EXACTLY in this format:\n"
            "TOOL_CALL: [tool_name] | ARGS: [json_args]\n"
            "If no tool is needed, respond normally."
        )
        
        full_prompt = f"{system_instructions}\n\nUser: {user_input}\nAssistant:"
        response = ollama.generate(model=self.model_name, prompt=full_prompt)
        text = response['response']

        # Intercept tool calls
        if "TOOL_CALL:" in text:
            try:
                # Extract tool name and arguments
                parts = text.split("TOOL_CALL:")[1].split("| ARGS:")
                tool_name = parts[0].strip()
                args_str = parts[1].strip()
                
                print(f"[*] AI is calling tool: {tool_name} with {args_str}")
                tool_result = self.tool_registry.call_tool(tool_name, args_str)
                
                # Feed the tool result back to the LLM for a natural language final response
                final_prompt = (
                    f"{system_instructions}\n\n"
                    f"User: {user_input}\n"
                    f"Assistant: TOOL_CALL: {tool_name} | ARGS: {args_str}\n"
                    f"Tool Result: {tool_result}\n"
                    f"Assistant (Final Response):"
                )
                final_response = ollama.generate(model=self.model_name, prompt=final_prompt)
                return final_response['response']
            except Exception as e:
                return f"I tried to use a tool but encountered an error: {e}"

        return text

class ConsoleChat(AIAgent):
    def interact_with_user(self):
        print("AI Console Ready. Type 'exit' to quit.")
        while True:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            response_text = self.execute_chain(user_input)
            print(f"AI: {response_text}")

class ConsoleChatWithMemory(ConsoleChat):
    def __init__(self):
        super().__init__()
        self.memory = []
        
    def execute_chain(self, user_input):
        self.memory.append(f"User: {user_input}")
        history_str = "\n".join(self.memory[-10:])
        
        tool_defs = self.tool_registry.get_tool_definitions()
        system_instructions = (
            f"{self.prompt_text}\n\n"
            f"AVAILABLE TOOLS:\n{tool_defs}\n\n"
            "If you need to use a tool, respond EXACTLY in this format:\n"
            "TOOL_CALL: [tool_name] | ARGS: [json_args]\n"
            "Otherwise, respond normally."
        )
        
        full_prompt = f"{system_instructions}\n\nHistory:\n{history_str}\n\nAssistant:"
        
        response = ollama.generate(model=self.model_name, prompt=full_prompt)
        text = response['response']

        if "TOOL_CALL:" in text:
            try:
                parts = text.split("TOOL_CALL:")[1].split("| ARGS:")
                tool_name = parts[0].strip()
                args_str = parts[1].strip()
                tool_result = self.tool_registry.call_tool(tool_name, args_str)
                
                final_prompt = (
                    f"{system_instructions}\n\nHistory:\n{history_str}\n\n"
                    f"Assistant: TOOL_CALL: {tool_name} | ARGS: {args_str}\n"
                    f"Tool Result: {tool_result}\n"
                    f"Assistant (Final Response):"
                )
                final_response = ollama.generate(model=self.model_name, prompt=final_prompt)
                answer = final_response['response']
            except Exception as e:
                answer = f"Tool error: {e}"
        else:
            answer = text

        self.memory.append(f"Assistant: {answer}")
        return answer

class VoiceAgent(AIAgent):
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.temp_file = "temp_rec.wav"

    def speak(self, text):
        print(f"AI: {text}")
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            del engine
        except Exception as e:
            print(f"TTS Error: {e}")

    def listen(self):
        try:
            fs = 44100 
            duration = 8 
            print("Listening...")
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            audio_int16 = (recording * 32767).astype(np.int16)
            wav.write(self.temp_file, fs, audio_int16)
            with sr.AudioFile(self.temp_file) as source:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            print(f"Could not recognize voice: {e}")
            return None

    def interact_with_user(self):
        self.run_loop()

    def interact(self):
        text = self.listen()
        if text:
            print(f"You said: {text}")
            return text
        return None

    def get_input(self):
        return self.listen()

    def run_loop(self):
        print("Voice Agent Ready. Speak into the microphone.")
        while True:
            user_input = self.get_input()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "shutdown"]:
                break
            print(f"User: {user_input}")
            response = self.execute_chain(user_input)
            self.speak(response)

class VoiceAgentWithMemory(VoiceAgent):
    def __init__(self):
        super().__init__()
        self.memory = []

    def execute_chain(self, user_input):
        self.memory.append(f"User: {user_input}")
        history_str = "\n".join(self.memory[-10:])
        
        tool_defs = self.tool_registry.get_tool_definitions()
        system_instructions = (
            f"{self.prompt_text}\n\n"
            f"AVAILABLE TOOLS:\n{tool_defs}\n\n"
            "If you need to use a tool, respond EXACTLY in this format:\n"
            "TOOL_CALL: [tool_name] | ARGS: [json_args]\n"
            "Otherwise, respond normally."
        )
        
        full_prompt = f"{system_instructions}\n\nHistory:\n{history_str}\n\nAssistant:"
        
        response = ollama.generate(model=self.model_name, prompt=full_prompt)
        text = response['response']

        if "TOOL_CALL:" in text:
            try:
                parts = text.split("TOOL_CALL:")[1].split("| ARGS:")
                tool_name = parts[0].strip()
                args_str = parts[1].strip()
                tool_result = self.tool_registry.call_tool(tool_name, args_str)
                
                final_prompt = (
                    f"{system_instructions}\n\nHistory:\n{history_str}\n\n"
                    f"Assistant: TOOL_CALL: {tool_name} | ARGS: {args_str}\n"
                    f"Tool Result: {tool_result}\n"
                    f"Assistant (Final Response):"
                )
                final_response = ollama.generate(model=self.model_name, prompt=final_prompt)
                answer = final_response['response']
            except Exception as e:
                answer = f"Tool error: {e}"
        else:
            answer = text

        self.memory.append(f"Assistant: {answer}")
        return answer