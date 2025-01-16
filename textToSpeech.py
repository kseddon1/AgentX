#This file is licensed under the MIT No Attribution (MIT-0) License

import os

text = "Hello. It is nice to meet you."

# Call Festival from the command line
os.system(f"echo '{text}' | festival --tts")
