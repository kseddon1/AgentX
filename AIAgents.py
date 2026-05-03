# AIAgents.py
import pyttsx3
import speech_recognition as sr
import ollama 
import sounddevice as sd
import scipy.io.wavfile as wav
import os
import numpy as np
from enum import Enum

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

    def set_prompt(self, prompt_obj):
        self.prompt_text = prompt_obj.text if hasattr(prompt_obj, 'text') else prompt_obj

    def set_llm(self, model_name):
        self.model_name = model_name

    def execute_chain(self, user_input):
        full_prompt = f"{self.prompt_text}\n\nUser: {user_input}\nAssistant:"
        response = ollama.generate(model=self.model_name, prompt=full_prompt)
        return response['response']

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
        full_prompt = f"{self.prompt_text}\n\nHistory:\n{history_str}\n\nAssistant:"
        
        response = ollama.generate(model=self.model_name, prompt=full_prompt)
        answer = response['response']
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
            # Explicitly delete the engine to force cleanup of the event loop
            del engine
        except Exception as e:
            print(f"TTS Error: {e}")

    def listen(self):
        try:
            fs = 44100 
            duration = 8 # seconds
            print("Listening...")
            
            # Record as float32
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            
            # --- FIX: Convert float32 to int16 (PCM) ---
            # Normalize to -1.0 to 1.0 and convert to 16-bit integers
            audio_int16 = (recording * 32767).astype(np.int16)
            wav.write(self.temp_file, fs, audio_int16)
            # -------------------------------------------
            
            with sr.AudioFile(self.temp_file) as source:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            print(f"Could not recognize voice: {e}")
            return None

    def interact_with_user(self):
        """Alias for run_loop to maintain compatibility with launch.py"""
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
        full_prompt = f"{self.prompt_text}\n\nHistory:\n{history_str}\n\nAssistant:"
        
        response = ollama.generate(model=self.model_name, prompt=full_prompt)
        answer = response['response']
        self.memory.append(f"Assistant: {answer}")
        return answer