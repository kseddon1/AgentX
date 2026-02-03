#This file is licensed under the MIT No Attribution (MIT-0) License

import curses
import pyfiglet
import subprocess

from AIAgents import ConsoleChat, ConsoleChatWithMemory, VoiceChat, VoiceChatWithMemory, WebChat, WebChatWithMemory, AgentType, AIAgentFactory
from Prompts import Prompt, PromptLibrary

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# Function to print the banner in ASCII art
def print_banner(stdscr, banner_name):
    stdscr.clear()
    ascii_banner = pyfiglet.figlet_format(banner_name)
    stdscr.addstr(0, 0, ascii_banner)
    stdscr.refresh()

# Function to create a bordered window and display chat/output
def display_chat_window(stdscr, chat_content):
    # Create a window for the chat area
    height, width = 10, 40  # Set the size of the window
    start_y, start_x = 5, 5  # Set the position of the window (relative to the screen)

    # Create the window with a border
    chat_window = curses.newwin(height, width, start_y, start_x)
    chat_window.box()  # Add a border around the window

    # Display the chat content inside the window
    chat_window.addstr(1, 1, "Chat Start")  # Add a label or heading
    for i, line in enumerate(chat_content, 2):
        chat_window.addstr(i, 1, line)  # Print each chat line
    
    chat_window.refresh()  # Refresh the window to update the display

# Function to display a menu and handle user input
def main(stdscr):
    # Initialize screen and set cursor to 0 (invisible)
    curses.curs_set(0)
    stdscr.nodelay(1)  # Make getch non-blocking
    stdscr.timeout(2000)  # Refresh every 100ms to handle inputs faster
    
    banner_name = "AgentX"  # Updated project name
    print_banner(stdscr, banner_name)
    
    # Menu options with added space between the last option and quit
    menu = [
        "Console Chat",
        "Console Chat with Memory",
        "Voice Chat",
        "Voice Chat with Memory",
        "Web Chat",
        "Web Article Writer",
        "Web Classifier",
        "Web Chat with Memory",
        "",
        "Quit"
    ]
    current_option = 0  # Initially highlight the first option
    
    while True:
        # Print menu options
        for idx, option in enumerate(menu):
            if idx == current_option:
                stdscr.addstr(10 + idx, 0, option, curses.A_REVERSE)  # Highlight selected option
            else:
                stdscr.addstr(10 + idx, 0, option)
        
        stdscr.refresh()
        
        key = stdscr.getch()  # Capture user input
        
        if key == curses.KEY_UP and current_option > 0:  # Navigate up
            current_option = 0
        elif key == curses.KEY_DOWN and current_option is len(menu) - 3:  # Navigate down
            current_option += 2
        elif key == curses.KEY_DOWN and current_option < len(menu) - 1:  # Navigate down
            current_option += 1
        elif key == 10:  # Enter key

            library = PromptLibrary()
            factory = AIAgentFactory()
            ### --------------------------------------------------------------------------------- ###
            if menu[current_option] == "Console Chat":
                stdscr.clear()
                curses.endwin()
                agent = factory.create_agent(AgentType.console, Ollama(model="lllama3.2:3b"), library.prompt["simplechat"])
                agent.build_chains()
                agent.interact_with_user()
                break
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Console Chat with Memory":
                stdscr.clear()
                curses.endwin()
                agent = factory.create_agent(AgentType.memory_console, Ollama(model="llama3.2:3b"), library.prompt["simplememorychat"])
                agent.build_chains()
                agent.interact_with_user()
                break
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Voice Chat":
                stdscr.clear()
                curses.endwin()
                agent = factory.create_agent(AgentType.voice, Ollama(model="llama3.2:3b"), library.prompt["simplechat"])
                agent.build_chains()
                agent.interact_with_user()
                break
           ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Voice Chat with Memory":
                stdscr.clear()
                curses.endwin()
                agent = factory.create_agent(AgentType.memory_voice, Ollama(model="llama3.2:3b"), library.prompt["simplememorychat"])
                agent.build_chains()
                agent.interact_with_user()
                break
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Web Chat":
                stdscr.clear()
                curses.endwin()
                subprocess.run("streamlit run webChat.py", shell=True)
                stdscr.refresh()
                stdscr.getch()
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Web Article Writer":
                stdscr.clear()
                curses.endwin()
                subprocess.run("streamlit run webArticleWriter.py", shell=True)
                stdscr.refresh()
                stdscr.getch()
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Web Classifier":
                stdscr.clear()
                curses.endwin()
                subprocess.run("streamlit run webClassifier.py", shell=True)
                stdscr.refresh()
                stdscr.getch()
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Web Chat with Memory":
                stdscr.clear()
                curses.endwin()
                subprocess.run("streamlit run webChatWithMemory.py", shell=True)
                stdscr.refresh()
                stdscr.getch()
            ### --------------------------------------------------------------------------------- ###
            elif menu[current_option] == "Quit":
                break  # Exit the program
            ### --------------------------------------------------------------------------------- ###
        # Redraw the banner and menu
        print_banner(stdscr, banner_name)

# Start the curses application
curses.wrapper(main)
