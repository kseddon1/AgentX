#This file is licensed under the MIT No Attribution (MIT-0) License

import streamlit as st

web_chat = st.Page("webChat.py", title="Web Chat", icon=":material/add_circle:")
web_chat_with_memory = st.Page("webChatWithMemory.py", title="Web Chat with Memory", icon=":material/add_circle:")
web_sentiment_classifier = st.Page("webClassifier.py", title="Web Classifier", icon=":material/add_circle:")

pg = st.navigation([web_chat, web_chat_with_memory,web_sentiment_classifier])
st.set_page_config(page_title="Multi-Page Web App", page_icon=":material/edit:")
pg.run()