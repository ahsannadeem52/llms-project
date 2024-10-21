import openai
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import time  # To simulate real-time communication delays
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv('key.env')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

# Function to simulate a dialogue between agents in real-time
def generate_agent_discussion(agents, topic, rounds=3):
    system_prompt = f"Agents: {', '.join(agents)}. Discuss the following topic: {topic}. Each agent will take turns responding."

    messages = [{"role": "system", "content": system_prompt}]
    conversation_responses = []

    # Simulating rounds of conversation between agents
    for i in range(rounds):
        for agent in agents:
            previous_response = conversation_responses[-1] if conversation_responses else topic

            # Agent responding to the previous response
            agent_prompt = f"{agent} responds to: {previous_response}"
            messages.append({"role": "user", "content": agent_prompt})

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=20  # Allowing shorter responses (adjust as needed)
                )
                agent_response = response['choices'][0]['message']['content'].strip()
                conversation_responses.append(agent_response)

                # Emit each agent's response as it happens (simulating real-time communication)
                socketio.emit('conversation_response', {
                    'agent': agent,
                    'response': agent_response
                })

                # Delay to simulate real-time conversation
                time.sleep(1)

            except Exception as e:
                print(f"Error in OpenAI API call: {e}")
                break

# Socket handler for starting the conversation
@socketio.on('start_conversation')
def handle_conversation(data):
    topic = data.get('topic', '')
    agents = data.get('agents', '').split(', ')
    rounds = data.get('rounds', 3)

    if not agents or not topic:
        emit('error', {'error': 'Please provide valid agents and topic'})
        return

    # Generate a conversation log based on the agents and topic
    generate_agent_discussion(agents, topic, rounds)

if __name__ == '__main__':
    socketio.run(app, debug=True)
