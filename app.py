import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from engine import get_chat_engine
from audio import transcribe_audio

st.set_page_config(page_title="Tera Khas Dost", page_icon="💬", layout="centered")
st.title("💬 Tera Khas Dost")
st.caption("Kuch bhi baat kar, mai tujhe jawab dunga!")


@st.cache_resource
def load_engine():
    return get_chat_engine()

chat_chain = load_engine()


if "mic_key" not in st.session_state:
    st.session_state.mic_key = 0

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        1: {"title": " ", "messages": []}
    }
    st.session_state.current_session_id = 1
    st.session_state.session_counter = 1

curr_id = st.session_state.current_session_id
current_messages = st.session_state.chat_sessions[curr_id]["messages"]

with st.sidebar:
    st.header("Voice Chat 🎙️")
    audio_file = st.audio_input("🎤 Record Message", key=f"mic_{st.session_state.mic_key}")
    
    st.divider()
    
    st.header("📜 Chat History")
    
    # NEW CHAT BUTTON
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.session_counter += 1
        new_id = st.session_state.session_counter
        # Create a blank session and set it as active
        st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_session_id = new_id
        st.session_state.mic_key += 1
        st.rerun()

    st.subheader("Previous Chats")
    
    for session_id, session_data in reversed(st.session_state.chat_sessions.items()):
        is_active = (session_id == st.session_state.current_session_id)
        # Visual indicator for the active chat
        icon = "🟢" if is_active else "💬"
        
        if st.button(f"{icon} {session_data['title']}", key=f"chat_btn_{session_id}", use_container_width=True):
            st.session_state.current_session_id = session_id
            st.session_state.mic_key += 1
            st.rerun()

for message in current_messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)
user_input = st.chat_input("Yahan type kar...")
final_input = None

if user_input:
    final_input = user_input
elif audio_file:
    final_input = transcribe_audio(audio_file)

if final_input:
    # Display user message instantly
    with st.chat_message("user"):
        st.markdown(final_input)
    
    
    if len(current_messages) == 0:
        st.session_state.chat_sessions[curr_id]["title"] = final_input[:20] + "..."

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            response = chat_chain.invoke({
                "chat_history": current_messages,
                "user_input": final_input
            })
            
            output_text = response.content
            response_placeholder.markdown(output_text)
            

            st.session_state.chat_sessions[curr_id]["messages"].append(HumanMessage(content=final_input))
            st.session_state.chat_sessions[curr_id]["messages"].append(AIMessage(content=output_text))
            
        except Exception as e:
            st.error(f"Error aagya bhai: {e}")

if audio_file:
    st.session_state.mic_key += 1
    st.rerun()
