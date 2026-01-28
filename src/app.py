import os
import streamlit as st
from dotenv import load_dotenv
from ollama import Client

from data_loader import load_tables
import tools as T
from agent_core import route_to_tool, run_tool, llm_answer


st.set_page_config(page_title="Healthcare AI Agent (Local)", layout="wide")

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

@st.cache_data
def get_tables():
    return load_tables()

tables = get_tables()
client = Client(host="http://localhost:11434")

st.title("🏥 Healthcare AI Agent (Local, Free)")
st.caption("Synthetic demo data • Runs locally with Ollama • Not medical advice")

with st.sidebar:
    st.header("Quick actions")

    if st.button("List tables"):
        st.session_state["last_result"] = T.list_tables(tables)

    if st.button("Show schema"):
        st.session_state["last_result"] = T.show_schema(tables)

    st.divider()
    st.header("Examples")
    st.code("patients with ICD10 E11")
    st.code("summary P001")
    st.code("latest A1C for P001")
    st.code("find patient Amy")

    st.divider()
    st.write("Model:", MODEL)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Tool output")
    st.write(st.session_state.get("last_result", "Click a quick action, or ask a question on the right."))

with col2:
    st.subheader("Chat")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    user = st.chat_input("Ask something… (e.g., 'patients with ICD10 E11')")
    if user:
        st.session_state["messages"].append({"role": "user", "content": user})
        with st.chat_message("user"):
            st.markdown(user)

        tool_name, tool_args = route_to_tool(user)
        if tool_name:
            answer = run_tool(tables, tool_name, tool_args)
            st.session_state["last_result"] = answer
        else:
            answer = llm_answer(client, MODEL, user)

        st.session_state["messages"].append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
