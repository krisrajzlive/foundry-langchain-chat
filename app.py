"""Streamlit chat UI backed by an Azure AI Foundry model deployment via LangChain."""

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from chat_model import build_chat_model, load_settings

SYSTEM_PROMPT = "You are a helpful assistant."

st.set_page_config(page_title="Foundry Chat", page_icon="💬", layout="centered")
st.title("💬 Foundry Chat")

settings = load_settings()
missing = settings.missing()
if missing:
    st.error(f"Missing configuration: {', '.join(missing)}. Copy `.env.example` to `.env` and fill it in.")
    st.stop()


@st.cache_resource
def get_model():
    return build_chat_model(settings)


st.caption(f"Deployment: `{settings.deployment}` · LangChain + Azure AI Foundry")

if st.sidebar.button("Clear conversation"):
    st.session_state.history = []
    st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    st.chat_message(role).write(msg.content)

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.history.append(HumanMessage(prompt))
    st.chat_message("user").write(prompt)

    messages = [SystemMessage(SYSTEM_PROMPT), *st.session_state.history]
    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(chunk.content for chunk in get_model().stream(messages))
        except Exception as exc:  # surface auth/deployment errors in the UI
            st.session_state.history.pop()
            st.error(f"Model call failed: {exc}")
            st.stop()
    st.session_state.history.append(AIMessage(reply))
