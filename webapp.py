#This file is licensed under the MIT No Attribution (MIT-0) License

import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Multi-Page Web App", page_icon=":material/edit:")

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

login = authenticator.login('main', key='Login')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
    web_chat_llama = st.Page("webChatWithMemory.py", title="Web Chat (Llama 3.2)", icon=":material/add_circle:")
    web_chat_deepseek = st.Page("webChatDeepSeek.py", title="Web Chat (DeepSeek-r1)", icon=":material/add_circle:")
    web_chat_codellama = st.Page("webChatCodeLlama.py", title="Web Chat (CodeLLama)", icon=":material/add_circle:")
    web_chat_mistral = st.Page("webChatMistral.py", title="Web Chat (CodeLLama)", icon=":material/add_circle:")
    web_sentiment_classifier = st.Page("webClassifier.py", title="Web Classifier", icon=":material/add_circle:")
    pg = st.navigation([web_chat_llama, web_chat_deepseek, web_chat_codellama, web_chat_mistral, web_sentiment_classifier])
    pg.run()
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')