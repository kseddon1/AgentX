# launch.py
import curses
import ollama
from AIAgents import AgentType, ConsoleChat, ConsoleChatWithMemory, VoiceAgent, VoiceAgentWithMemory
from Prompts import Prompt, PromptLibrary

def draw_menu(stdscr, selections, current_row):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, "=== AgentX Configuration ===", curses.A_BOLD)
    
    for idx, selection in enumerate(selections):
        x = 2
        y = 3 + idx
        if idx == current_row:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, f"> {selection}")
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, f"  {selection}")
    
    stdscr.refresh()

def get_user_choice(stdscr, options):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row = 0
    
    while True:
        draw_menu(stdscr, options, current_row)
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row

def main():
    # Wrap the curses logic
    def run_ui(stdscr):
        # 1. Select Agent Type
        agent_options = [
            (AgentType.console, "Console Chat"),
            (AgentType.memory_console, "Console Chat (with Memory)"),
            (AgentType.voice, "Voice Agent"),
            (AgentType.memory_voice, "Voice Agent (with Memory)")
        ]
        idx = get_user_choice(stdscr, [opt[1] for opt in agent_options])
        selected_agent_type = agent_options[idx][0]

        # 2. Select Model
        # You can expand this list with your available Ollama models
        model_options = ["llama3.2:3b", "llama3.1:8b", "gpt-oss:20b", "gemma4:31b"]
        m_idx = get_user_choice(stdscr, model_options)
        selected_model = model_options[m_idx]

        return selected_agent_type, selected_model

    # Execute Curses wrapper
    agent_type, model_name = curses.wrapper(run_ui)

    # --- Now transition from UI to Logic ---
    
    # Initialize Prompt Library
    library = PromptLibrary()
    
    # Map agent type to specific prompt from library
    if agent_type in [AgentType.console, AgentType.voice]:
        my_prompt = library.prompt["simplechat"]
    elif agent_type in [AgentType.memory_console, AgentType.memory_voice]:
        my_prompt = library.prompt["simplememorychat"]
    else:
        my_prompt = library.prompt["simplechat"]

    # Agent Factory
    if agent_type == AgentType.console:
        agent = ConsoleChat()
    elif agent_type == AgentType.memory_console:
        agent = ConsoleChatWithMemory()
    elif agent_type == AgentType.voice:
        agent = VoiceAgent()
    elif agent_type == AgentType.memory_voice:
        agent = VoiceAgentWithMemory()
    else:
        print("Unsupported agent type")
        return

    # Setup and Run
    agent.set_prompt(my_prompt)
    agent.set_llm(model_name) 
    
    print(f"\n--- AgentX Started ---")
    print(f"Mode: {agent_type.value} | Model: {model_name}")
    print("Type 'exit' to quit.")
    print("--------------------------\n")
    
    try:
        agent.interact_with_user()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()