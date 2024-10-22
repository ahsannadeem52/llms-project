from flask import Flask, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variable to control the conversation activity
conversation_active = False

def generate_agent_response(agent, topic):
    """
    Generate short responses for an agent based on the topic.
    This simulates AI agent responses.
    """
    responses = [
        f"{agent} thinks {topic} is interesting.",
        f"{agent} wants to know more about {topic}.",
        f"{agent} agrees with the other agent on {topic}.",
        f"{agent} is considering different perspectives on {topic}.",
        f"{agent} raises a point about {topic}."
    ]
    return responses

def simulate_conversation(agents, topic):
    """
    Simulates conversation by agents on a given topic and emits responses
    one by one to the frontend via socket.io.
    """
    global conversation_active
    while conversation_active:  # Keep the conversation going until stopped
        for agent in agents:
            if not conversation_active:
                break  # If conversation is stopped, exit the loop

            responses = generate_agent_response(agent, topic)
            for response in responses:
                if not conversation_active:
                    break  # Exit if conversation is stopped
                
                # Emit 'typing' event before sending the message
                socketio.emit('agent_typing', {"agent": agent})
                time.sleep(2)  # Simulate typing delay

                socketio.emit('conversation_response', {"agent": agent, "message": response})
                time.sleep(2)  # Simulate time delay for the next response

@app.route("/")
def index():
    return "Server is running."

@socketio.on('start_conversation')
def start_conversation(data):
    """
    Handle the event to start the conversation. Receives agents and topic from the frontend
    and starts simulating the conversation.
    """
    global conversation_active
    conversation_active = True  # Set the conversation as active

    topic = data['topic']
    agents = data['agents'].split(", ")

    # Start the conversation in a separate process
    simulate_conversation(agents, topic)

@socketio.on('stop_conversation')
def stop_conversation():
    """
    Handle the event to stop the conversation.
    """
    global conversation_active
    conversation_active = False  # Stop the conversation

if __name__ == '__main__':
    socketio.run(app, debug=True)
