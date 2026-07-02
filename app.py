import os
from pathlib import Path

import streamlit as st
from openai import OpenAI


SYSTEM_PROMPT = """You are Vijay's Chatbot, a professional AI assistant designed for business, support, writing, analysis, and productivity tasks. Respond clearly, concisely, and helpfully. Keep your tone polished, trustworthy, and professional."""


def load_env_file(env_path: Path | None = None) -> None:
    path = env_path or Path(__file__).resolve().parent / ".env"
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file()


def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not found in .env"
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    return client

def generate_reply(messages: list[dict]) -> str:

    client = get_client()

    response = client.chat.completions.create(

        model=os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-5.2"
        ),

        extra_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-OpenRouter-Title": "Vijay Chatbot",
        },

        messages=messages,

        max_tokens=300,
    )

    return response.choices[0].message.content

st.set_page_config(page_title="Vijay's Chatbot", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Vijay's Chatbot")
st.caption("Professional AI assistant for business, support, drafting, research, and everyday productivity.")

with st.sidebar:
    st.header("About")
    st.write("Vijay's Chatbot is designed for professional conversations with a polished and dependable experience.")
    st.divider()
    st.subheader("Quick actions")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state["welcome_shown"] = False
        st.rerun()

    st.divider()
    st.write("Tip: add your API key to the .env file or your environment before chatting.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False

if not st.session_state.welcome_shown and not st.session_state.messages:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I’m Vijay's Chatbot. I can help with professional writing, summaries, planning, brainstorming, and clear explanations.",
        }
    ]
    st.session_state.welcome_shown = True

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask Vijay's Chatbot anything...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
        conversation.extend(message for message in st.session_state.messages[-10:])
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = generate_reply(conversation)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as exc:
        error_message = f"I’m unable to respond right now. {exc}"
        with st.chat_message("assistant"):
            st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
