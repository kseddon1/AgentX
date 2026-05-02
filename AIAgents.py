#This file includes code snippets derived from Generative AI with LangChain, First Edition, which is licensed under the MIT License.
#
#Copyright (c) 2024 Ben Auffarth
#
#https://github.com/benman1/generative_ai_with_langchain/tree/softupdate
#
#The MIT License applies to the original snippets. See the full license in the LICENSE file.

import os
import sys
import tempfile
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import pyttsx3
import queue
import time

from enum import Enum
from typing import Optional

import streamlit as st
import speech_recognition as sr

from Prompts import Prompt
from DocumentLoaders import load_document, DocumentLoader

from langchain_community.llms import Ollama

from langchain_classic.chains import LLMChain
from langchain_classic.chains import ConversationChain
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.chains import SequentialChain

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_classic.memory import ConversationBufferMemory, CombinedMemory, ConversationSummaryMemory
from langchain_community.callbacks import StreamlitCallbackHandler

from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.docarray import DocArrayInMemorySearch

# Define an enum for agent types
class AgentType(str, Enum):
    console = "console"
    memory_console = "memoryconsole"
    voice = "voice"
    memory_voice = "memoryvoice"
    web = "web"
    memory_web = "memoryweb"

# Define an interface for agents
class AIAgent:
    def __init__(self):
        pass

    def set_prompt(self, prompt: Prompt):
        if prompt.examples == '':
           self.prompt = PromptTemplate(input_variables=prompt.variables, template=prompt.text)
        else:
           example_prompt = PromptTemplate(
               template="{input} -> {output}",
               input_variables=["input", "output"]
           )
           self.prompt = FewShotPromptTemplate(examples=prompt.examples, example_prompt=example_prompt, suffix=prompt.text, input_variables=prompt.variables)

    def set_llm(self, llm):
        self.llm = llm

    def build_chains(self):
        raise NotImplementedError("Must be implemented by subclass")
    
    def execute_chain(self, user_input):
        raise NotImplementedError("Must be implemented by subclass")

# Define a concrete agent class for console interactions
class ConsoleChat(AIAgent):
    def __init__(self):
        super().__init__()

    def build_chains(self):
        self.chat_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def execute_chain(self, user_input):
        model_response = self.chat_chain.invoke({"input": user_input})
        return model_response.get("text", "No response text found.")

    def interact_with_user(self):
        while True:

            user_input = input("User: ")
    
            if user_input.lower() in ["exit", "quit", "bye", "goodbye", "good bye"]:
                print("Chatbot: Goodbye!")
                exit() 
            else:
                 # Using invoke method to execute chain
                response_text = self.execute_chain(user_input)
                print(f"Chatbot: {response_text}")

# Define a concrete agent class for memory console interactions
class ConsoleChatWithMemory(ConsoleChat):
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history_lines", input_key="input")
        super().__init__()

    def build_chains(self):
        self.chat_chain = ConversationChain(llm=self.llm, memory=self.memory, prompt=self.prompt)

    def execute_chain(self, user_input):
        return self.chat_chain.invoke({"input": user_input})['response']

class VoiceChat(AIAgent):
    def __init__(self):
        self.r = sr.Recognizer()
        super().__init__()

    def build_chains(self):
        self.voice_chat_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def execute_chain(self, user_input):
        model_response = self.voice_chat_chain.invoke({"input": user_input})
        return model_response.get("text", "No response text found.")

    # 🎤 NEW: record audio without PyAudio
    def record_audio(self, fs=16000, silence_threshold=500, silence_duration=10):
        print("🎤 Listening...")
    
        q = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(indata.copy())

        silence_chunks = 0
        max_silence_chunks = int(silence_duration * fs / 1024)

        recording = []

        with sd.InputStream(samplerate=fs, channels=1, dtype='int16', callback=callback):
            while True:
                chunk = q.get()
                recording.append(chunk)

                volume = np.abs(chunk).mean()

                if volume < silence_threshold:
                    silence_chunks += 1
                else:
                    silence_chunks = 0  # reset if speech resumes

                # stop after enough silence
                if silence_chunks > max_silence_chunks:
                    break

        audio_data = np.concatenate(recording, axis=0)
        return fs, audio_data

    # 🔊 NEW: Windows TTS
    def speak(self, text):
        try:

            print(f"TTS → {text}")

            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
        except Exception as e:
            print(f"TTS ERROR: {e}")


    def listen_and_transcribe(self):
        fs, audio_data = self.record_audio()
        if audio_data is None:
            return ""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav.write(f.name, fs, audio_data)
            filename = f.name

        with sr.AudioFile(filename) as source:
            audio = self.r.record(source)

        try:
            print("🧠 Recognizing...")
            text = self.r.recognize_google(audio)
            print(f"✅ You said: {text}")
        except Exception as e:
            print(f"❌ Recognition failed: {e}")
            text = ""

        os.remove(filename)
        return text

    def interact_with_user(self):
        while True:
            user_input = self.listen_and_transcribe()
            if not user_input:
                continue

            else:
                 bot_response = self.parse_and_respond(user_input)
                 self.speak(bot_response)


    def parse_and_respond(self, user_input):
        response_text = self.execute_chain(user_input)

        print(f"Bot Response: {response_text}")
        return response_text


# Define a concrete agent class for memory voice interactions
class VoiceChatWithMemory(VoiceChat):
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history_lines", input_key="input")
        super().__init__()

    def build_chains(self):
        self.voice_chat_chain = ConversationChain(llm=self.llm, memory=self.memory, prompt=self.prompt)

    def execute_chain(self, user_input):
        return self.voice_chat_chain.invoke({"input": user_input})['response']

# Define a concrete agent class for web interactions
class WebChat(AIAgent):
    def __init__(self):
        super().__init__()

    def build_chains(self):
        self.web_chat_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def execute_chain(self, user_input):
        model_response = self.web_chat_chain.invoke({"input": user_input})
        return model_response.get("text", "No response text found.")

    def interact_with_user(self):
        if prompt := st.chat_input(placeholder="Ask me anything!"):
           st.chat_message("user").write(prompt)
           with st.chat_message("assistant"):
              response = self.execute_chain(prompt)
              st.write(response)

# Define a concrete agent class for memory voice interactions
class WebChatWithMemory(WebChat):
    def __init__(self):
        if 'memory' not in st.session_state:
           st.session_state.memory = ConversationBufferMemory(memory_key="chat_history_lines", input_key="input")
        super().__init__()

    def build_chains(self):
        self.web_chat_chain = ConversationChain(llm=self.llm, memory=st.session_state.memory, prompt=self.prompt)

    def execute_chain(self, user_input):
        return self.web_chat_chain.invoke({"input": user_input})['response']
    


# Define a factory class to create agents based on type and prompt
class AIAgentFactory:
    def __init__(self):
        self.agents = {}

    def create_agent(self, agent_type: AgentType, llm, prompt):
        if agent_type not in self.agents:
            agent = None
            if agent_type == AgentType.console:
                agent = ConsoleChat()
            elif agent_type == AgentType.memory_console:
                agent = ConsoleChatWithMemory()
            elif agent_type == AgentType.voice:
                agent = VoiceChat()
            elif agent_type == AgentType.memory_voice:
                agent = VoiceChatWithMemory()
            elif agent_type == AgentType.web:
                agent = WebChat()
            elif agent_type == AgentType.memory_web:
                agent = WebChatWithMemory()
            
            agent.set_llm(llm)
            agent.set_prompt(prompt)
            return agent