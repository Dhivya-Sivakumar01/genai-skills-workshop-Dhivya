# Import the Streamlit library
import streamlit as st

# Import your backend function that handles the chatbot response
from backend import process_user_input

# Configure the Streamlit page (title, icon, layout)
st.set_page_config(page_title="Alaska SnowBot", page_icon="❄️")

# Show a header at the top of the page
st.header("❄️ _Alaska Department of Snow Online Agent_")

# Inject custom CSS to improve layout and padding
st.markdown("""
    <style>
        .chat-container {
            display: flex;
            flex-direction: column-reverse;
            max-width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize the chat history in session state (only once)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input
user_input = st.chat_input("Type your question here...")

# Process input only when user submits
if user_input:
    with st.spinner("Thinking..."):  # Show loading spinner
        # backend function call
        response = process_user_input(user_input)
        # Append user input and bot response to the chat history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))

# Display the full chat history from top to bottom
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        with st.chat_message("User"):
            st.markdown(msg)
    else:
        with st.chat_message("Bot"):
            st.markdown(msg)
           


