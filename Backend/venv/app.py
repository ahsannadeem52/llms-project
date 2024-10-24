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
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flag to track if conversation should stop
conversation_active = True

# Function to check moderation
def check_moderation(response):
    """
    Checks the response for moderation and toxicity.
    """
    try:
        moderation_response = openai.Moderation.create(input=response)
        return moderation_response
    except Exception as e:
        print(f"Error in moderation check: {e}")
        return None

# Function to generate conversation between agents
def generate_agent_response(agent, previous_response, topic, prompt_message=None):
    """
    Generates a response for an agent based on the previous agent's response.
    """
    if previous_response:
        system_prompt = f"{agent} responds briefly to the previous message: {previous_response}."
    else:
        system_prompt = f"{agent} responds briefly to the topic: {topic}."

    messages = [{"role": "system", "content": system_prompt}]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=25  # Set to a lower value for shorter responses
        )
        agent_response = response['choices'][0]['message']['content'].strip()
        return agent_response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return None

# Start conversation handler
def simulate_conversation(agents, topic, prompt_message=None):
    """
    Simulates a discussion between agents on a given topic and prompt.
    Each agent responds to the previous agent's response.
    """
    global conversation_active
    previous_response = None  # This will store the last agent's response

    while conversation_active:
        for agent in agents:
            if not conversation_active:
                break

            # Generate OpenAI-based response for the current agent, considering the previous agent's response
            response = generate_agent_response(agent, previous_response, topic, prompt_message)

            # Check for moderation and toxicity
            if response:
                moderation_result = check_moderation(response)

                # If the response is flagged, skip it
                if moderation_result and moderation_result['results'][0]['flagged']:
                    print(f"Moderation flagged response from {agent}: {response}")
                    continue  # Skip this response

                if conversation_active:
                    # Emit 'typing' event before sending the message
                    socketio.emit('agent_typing', {"agent": agent})
                    time.sleep(1)

                    # Emit the response to the frontend
                    socketio.emit('conversation_response', {"agent": agent, "message": response})

                    # Update the previous_response to the current agent's response for the next iteration
                    previous_response = response

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
    prompt_message = data.get('prompt', '')  # Extract the prompt from the frontend if available

    simulate_conversation(agents, topic, prompt_message)

@socketio.on('stop_conversation')
def stop_conversation():
    """
    Handle the event to stop the conversation.
    """
    global conversation_active
    conversation_active = False

if __name__ == '__main__':
    socketio.run(app, debug=True)
