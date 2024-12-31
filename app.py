import streamlit as st
import requests
import json
from streamlit_chat import message


# Define constants
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"  # Update with your Rasa server URL
LMS_FILE = "lms_data.json"  # Path to the JSON file containing links

# Load LMS JSON data
def load_lms_data():
    try:
        with open(LMS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("LMS file not found. Please check the path.")
        return {}

# Function to send user input to Rasa and get a response
def get_rasa_response(user_message):
    payload = {"message": user_message, "sender": "streamlit_user"}
    try:
        response = requests.post(RASA_URL, json=payload)
        if response.status_code == 200:
            return response.json()  # List of bot responses
        else:
            st.error(f"Error: Unable to fetch response from Rasa (Status {response.status_code})")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Rasa: {str(e)}")
        return []

# Initialize the Streamlit app
st.title("Chatbot for Personalized learning")

# Load LMS data
lms_data = load_lms_data()

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input form
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Ask a question...")
    submit = st.form_submit_button("Send")

# Handle user input
if submit and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response from Rasa bot
    rasa_responses = get_rasa_response(user_input)
    for response in rasa_responses:
        # Check if the Rasa response indicates a request for references or a definition
        bot_message = response.get("text", "")
        if "define" in user_input.lower():  # User asked for a definition
            st.session_state.messages.append({"role": "bot", "content": bot_message})
        elif "reference" in user_input.lower() or "link" in user_input.lower():  # User asked for references
            topic = next((t for t in lms_data if t.lower() in user_input.lower()), None)
            if topic:
                st.session_state.messages.append({"role": "bot", "content": f"References for {topic}:"})
                references = lms_data.get(topic, [])
                for ref in references:
                    st.session_state.messages.append(
                        {"role": "bot", "content": f"- [{ref['name']}]({ref['url']})"}
                    )
        else:  # General bot response
            st.session_state.messages.append({"role": "bot", "content": bot_message})

# Display conversation history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        message(msg["content"], is_user=True, key=f"user_{i}")
    else:
        message(msg["content"], key=f"bot_{i}")
# Add sidebar with additional information
with st.sidebar:
    st.header("About Learning Assistant")
    st.write("This chatbot helps you find the right programming courses based on interests.")
    st.write("Try asking about:")
    st.write("- Python")
    st.write("- Data Science")
    st.write("- Machine Learning")
    st.write("- Artificial Intelligence")