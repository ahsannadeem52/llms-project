import openai
from flask import Flask, request, jsonify, render_template
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

# Function to generate conversation between agents
def generate_agent_discussion(agents, topic, toxicity=0, mediator_enabled=False, rounds=3):
    if mediator_enabled:
        mediator = "Mediator"
        agents.append(mediator)
    
    # Adjust the prompt to influence the conversation based on toxicity level
    if toxicity >= 4:
        system_prompt = f"Agents: {', '.join(agents)}. Discuss the following topic: {topic} in a more confrontational and critical manner."
    elif toxicity >= 2:
        system_prompt = f"Agents: {', '.join(agents)}. Discuss the following topic: {topic} in a balanced and neutral tone."
    else:
        system_prompt = f"Agents: {', '.join(agents)}. Discuss the following topic: {topic} in a polite and friendly manner."
    
    messages = [{"role": "system", "content": system_prompt}]
    conversation_responses = []

    for i in range(rounds):
        for agent in agents:
            previous_response = conversation_responses[-1] if conversation_responses else topic

            # Mediator intervention logic
            if mediator_enabled and agent == mediator:
                agent_prompt = f"{mediator} mediates between agents after the round."
            else:
                agent_prompt = f"{agent} responds to: {previous_response}"

            messages.append({"role": "user", "content": agent_prompt})

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=20
                )
                agent_response = response['choices'][0]['message']['content'].strip()
                conversation_responses.append(agent_response)

                socketio.emit('conversation_response', {
                    'agent': agent,
                    'response': agent_response
                })

                time.sleep(1)

            except Exception as e:
                print(f"Error in OpenAI API call: {e}")
                break

@socketio.on('start_conversation')
def handle_conversation(data):
    topic = data.get('topic', '')
    agents = data.get('agents', '').split(', ')
    toxicity = int(data.get('toxicity', 0))  # Get the toxicity level
    mediator = data.get('mediator', False)  # Check if mediator is enabled
    rounds = data.get('rounds', 3)

    if not agents or not topic:
        emit('error', {'error': 'Please provide valid agents and topic'})
        return

    generate_agent_discussion(agents, topic, toxicity, mediator, rounds)

if __name__ == '__main__':
    socketio.run(app, debug=True)
