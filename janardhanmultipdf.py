import streamlit as st
from openai import AzureOpenAI
import pandas as pd
import pdfplumber
import tempfile

# Azure OpenAI Client
client = AzureOpenAI(
    api_key="CMfEAxVMt34Nq8hQlkz9erOq7PcvKhNCvtyCXB7PhT8ypv7vctuyJQQJ99BDACHYHv6XJ3w3AAABACOGGQbS",
    api_version="2024-12-01-preview",
    azure_endpoint="https://cybersofttrainingday2.openai.azure.com"
)

st.title("🧠 Multi Modal Chatbot")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": "You are a helpful assistant. If a file is uploaded, summarize it or answer based on its content."
    }]

if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False

# File Uploader (Multiple PDFs)
uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

file_text = ""

# Process uploaded files
if uploaded_files and not st.session_state.files_uploaded:
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        if "pdf" in file_type:
            with pdfplumber.open(tmp_path) as pdf:
                file_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        if file_text:
            st.session_state.messages.append({
                "role": "user",
                "content": f"I've uploaded a file. Please analyze the following content:\n{file_text}"
            })
    st.session_state.files_uploaded = True

# Show Chat History
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    visible_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=visible_messages
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})