# Streamlit entrypoint (UI: upload, chat, greeting)
import streamlit as st
from src.pdf_parser import extract_text_from_pdf
from src.vector_store import create_fresh_vectorstore, cleanup_session_data
from src.qa_chain import build_qa_chain
from src.guardrail import validate_safety, validate_output_quality
from src.memory_store import create_session_memory
from src.config import settings
import os
import uuid

st.set_page_config(page_title="File Q&A Bot", layout="wide")
st.title("📄 Q&A Bot — Upload a PDF & Ask")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.conversation_memory = create_session_memory()
    st.session_state.current_file = None
    st.session_state.vectorstore = None
    st.session_state.messages = []

# Greeting
if not st.session_state.messages:
    greeting = "Hi, welcome to the Q&A bot! Please upload a file and I'll help answer your questions about it."
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# File upload section
st.sidebar.header("📁 File Upload")
uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # Check if this is a new file
    if st.session_state.current_file != uploaded_file.name:
        # Clear previous conversation and data for new file
        st.session_state.messages = []
        st.session_state.conversation_memory = create_session_memory()
        st.session_state.current_file = uploaded_file.name
        
        # Process new file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Processing document..."):
            # Clean up previous session data if exists
            if hasattr(st.session_state, 'previous_session_id'):
                cleanup_session_data(st.session_state.previous_session_id)
            
            # Extract text and create fresh vector store
            text = extract_text_from_pdf(file_path)
            vectorstore = create_fresh_vectorstore(
                text, 
                metadata={
                    "source": uploaded_file.name,
                    "session_id": st.session_state.session_id
                }
            )
            st.session_state.vectorstore = vectorstore
            st.session_state.previous_session_id = st.session_state.session_id
        
        st.sidebar.success(f" {uploaded_file.name} processed successfully!")
        
        # Add welcome message for new file
        welcome_msg = f"Great! I've processed '{uploaded_file.name}'. You can now ask me questions about this document."
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Display current file info
if st.session_state.current_file:
    st.sidebar.info(f"📄 Current file: {st.session_state.current_file}")

# Chat interface
st.header("💬 Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the uploaded file..."):
    # Check if file is uploaded
    if not st.session_state.vectorstore:
        st.error("⚠️ Please upload a PDF file first before asking questions.")
        st.stop()
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Only validate for safety (minimal input validation)
    ok, reason = validate_safety(prompt)
    if not ok:
        error_msg = f"❌ {reason}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.markdown(error_msg)
        st.stop()
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build QA chain with memory and get response
                chain = build_qa_chain(st.session_state.vectorstore, st.session_state.conversation_memory)
                
                res = chain({"question": prompt})
                
                answer = res["answer"]
                source_docs = res.get("source_documents", [])
                question_type = res.get("question_type", "document")
                
                # Smart output validation based on question type
                is_valid, response = validate_output_quality(
                    answer, source_docs, prompt, question_type
                )
                
                if not is_valid:
                    response = "I can only answer questions based on the content of the uploaded document. Please ask something related to the uploaded file."
                
                # Display response
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                
                            
            except Exception as e:
                error_response = f"I encountered an error while processing your question: {str(e)}. Please try rephrasing your question or upload a new document."
                st.error(error_response)
                st.session_state.messages.append({"role": "assistant", "content": error_response})
                # For debugging - you can remove this in production
                st.write("Debug info:", str(e))

# Sidebar controls
st.sidebar.header("🔧 Controls")
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state.messages = []
    st.session_state.conversation_memory = create_session_memory()
    st.rerun()

if st.sidebar.button("🔄 Reset Session"):
    # Clean up session data before reset
    if hasattr(st.session_state, 'session_id'):
        cleanup_session_data(st.session_state.session_id)
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
