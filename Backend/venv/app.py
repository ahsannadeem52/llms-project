import openai
from flask import Flask
from flask_socketio import SocketIO, emit
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv('key.env')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Corrected the environment variable name

# Flag to track if conversation should stop
conversation_active = True

# Function to generate conversation between agents
def generate_agent_discussion(agent, topic, toxicity=0, mediator_enabled=False):
    system_prompt = f"{agent} responds to the topic: {topic}."
    messages = [{"role": "system", "content": system_prompt}]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=20
        )
        agent_response = response['choices'][0]['message']['content'].strip()
        return agent_response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return None

# Start conversation handler
def simulate_conversation(agents, topic):
    """
    Simulates conversation by agents on a given topic and emits responses
    one by one to the frontend via socket.io.
    """
    global conversation_active
    while conversation_active:
        for agent in agents:
            if not conversation_active:
                break

            # Generate OpenAI-based responses
            response = generate_agent_discussion(agent, topic)
            if response and conversation_active:
                # Emit 'typing' event before sending the message
                socketio.emit('agent_typing', {"agent": agent})
                time.sleep(2)

                # Emit the response to the frontend
                socketio.emit('conversation_response', {"agent": agent, "message": response})
                time.sleep(2)


@app.route("/")
def index():
    return "Server is running."


@socketio.on('start_conversation')
def start_conversation(data):
    """
    Handle the event to start the conversation.
    """
    global conversation_active
    conversation_active = True

    topic = data['topic']
    agents = data['agents'].split(", ")

    simulate_conversation(agents, topic)


@socketio.on('stop_conversation')
def stop_conversation():
    """
    Handle the event to stop the conversation.
    """
    global conversation_active
    conversation_active = False


if __name__ == '__main__':
    socketio.run(app, debug=True)
