import { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import './App.css';

function App() {
  const [showAgentDetails, setShowAgentDetails] = useState(false);
  const [topicDiscussion, setTopicDiscussion] = useState('');
  const [agentName, setAgentName] = useState('');
  const [agentRole, setAgentRole] = useState('');
  const [agents, setAgents] = useState([]);
  const [showAgents, setShowAgents] = useState(false);
  const [promptMessage, setPromptMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkTheme, setDarkTheme] = useState(true);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [toxicityLevel, setToxicityLevel] = useState(0);
  const [mediatorEnabled, setMediatorEnabled] = useState(false);

  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io('http://localhost:5000');

    socketRef.current.on('conversation_response', (data) => {
      setLoading(false);
      setConversation((prev) => [...prev, data]);  // Append each new message
    });

    socketRef.current.on('error', (error) => {
      setLoading(false);
      console.error("Socket error:", error);
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  const addAgent = () => {
    setShowAgentDetails(!showAgentDetails);
  };

  const handleData = () => {
    if (agentName) {
      setAgents([...agents, { name: agentName, role: agentRole }]);
      setAgentName('');
      setAgentRole('');
      setShowAgentDetails(false);
    }
  };

  const handleConversation = () => {
    setLoading(true);
    const dataToSend = {
      topic: topicDiscussion,
      agents: agents.map(a => `${a.name} (${a.role})`).join(', '),
      prompt: promptMessage,
      toxicity: toxicityLevel,
      mediator: mediatorEnabled,
    };

    if (socketRef.current) {
      socketRef.current.emit('start_conversation', dataToSend);
    }
    setSidebarVisible(false);
  };

  const showSidebar = () => {
    setSidebarVisible(true);
    setTopicDiscussion('');
    setAgents([]);
    setPromptMessage('');
  };

  const toggleTheme = () => {
    setDarkTheme(!darkTheme);
  };

  return (
    <div className={`flex justify-between w-full h-[600px] overflow-scroll scrollbar-hidden ${darkTheme ? 'bg-black text-white' : 'bg-white text-black'}`}>
      {sidebarVisible && (
        <div className={`text-gray-500 border ${darkTheme ? 'border-gray-400' : 'border-black'} rounded-lg m-1 p-6 w-80 h-auto overflow-scroll scrollbar-hidden`}>
          <button onClick={toggleTheme} className={`text-black ${darkTheme ? 'bg-gray-700 text-white' : 'bg-gray-300 text-black'} rounded-lg p-2 m-2 w-30`}>
            {darkTheme ? 'Light' : 'Dark'} Theme
          </button><br />

          <label htmlFor="">Topic</label>:<br />
          <input
            value={topicDiscussion}
            onChange={(e) => setTopicDiscussion(e.target.value)}
            type="text"
            placeholder="Enter Topic"
            className={`w-full mb-2 ${darkTheme ? 'bg-gray-800 text-white border border-gray-400' : 'bg-gray-200 text-black border border-black'}`}
          /><br />

          {/* Toxicity Level Slider */}
          <label htmlFor="toxicity">Toxicity Level ({toxicityLevel})</label>:<br />
          <input
            type="range"
            min="0"
            max="5"
            value={toxicityLevel}
            onChange={(e) => setToxicityLevel(e.target.value)}
            className="w-full mb-2"
          /><br />

          {/* Mediator Control Checkbox */}
          <label htmlFor="mediator">Enable Mediator</label>
          <input
            type="checkbox"
            checked={mediatorEnabled}
            onChange={(e) => setMediatorEnabled(e.target.checked)}
            className="ml-2"
          /><br /><br />

          <button
            onClick={addAgent}
            className={`p-2 mt-3 mb-3 cursor-pointer w-full ${darkTheme ? 'bg-gray-700 text-white' : 'bg-gray-300 text-black'} rounded-lg`}
          >
            <span className="float-left">Add Agent</span>
          </button>

          <div id="agent-Details" className={`agent-details ${showAgentDetails ? 'visible' : 'hidden'}`}>
            <label htmlFor="">Agent Name</label>:<br />
            <input
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              type="text"
              placeholder="Agent name"
              className={`w-full ${darkTheme ? 'bg-gray-800 text-white border border-gray-400' : 'bg-gray-200 text-black border border-black'}`}
            /><br />
            <label htmlFor="">Agent Role</label><br />
            <textarea
              value={agentRole}
              onChange={(e) => setAgentRole(e.target.value)}
              className={`w-full ${darkTheme ? 'bg-gray-800 text-white border border-gray-400' : 'bg-gray-200 text-black border border-black'}`}
            ></textarea><br /><br />
            <button onClick={handleData} className={`text-black ${darkTheme ? 'bg-gray-700 text-white' : 'bg-gray-300 text-black'} rounded-lg p-2 m-2 w-30`}>Add Agent</button>
          </div>

          <div className="p-1 w-full">
            <button
              onClick={() => setShowAgents(!showAgents)}
              className={`p-2 w-full ${darkTheme ? 'bg-gray-700 text-white' : 'bg-gray-300 text-black'} rounded-lg`}
            >
              <span className="float-left">Agents</span>
            </button>

            {agents.map((agent, index) => (
              <div key={index} className={`show-agents ${showAgents ? 'visibleAgents' : 'hideAgents'}`}>
                <strong>Name:</strong> {agent.name}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className='w-full m-1 p-3'>
        <div className='ml-[10%]'>
          <h1 className='font-bold'>MultiAgent Chatbot</h1><br />
          <label htmlFor="">Prompt</label><br />
          <input
            value={promptMessage}
            onChange={(e) => setPromptMessage(e.target.value)}
            className={`w-[50%] ${darkTheme ? 'bg-gray-800 text-white border border-gray-400' : 'bg-gray-200 text-black border border-black'}`}
            type="text"
            placeholder='Write a project description of agent(s) to converse in round(s)' 
          /><br />
          <button onClick={handleConversation} className={`text-black ${darkTheme ? 'bg-gray-700 text-white' : 'bg-gray-300 text-black'} rounded-lg p-1 m-2 w-40`}>
            Start Conversation
          </button>

          {!sidebarVisible && (
            <button onClick={showSidebar} className={`text-black ${darkTheme ? 'bg-gray-700 text-white' : 'bg-gray-300 text-black'} rounded-lg p-1 m-2 w-40`}>
              Add Agents
            </button>
          )}
        </div>

        <div>
          <h2>Conversation:</h2>
          {loading && <p>Loading...</p>}
          {conversation.length > 0 ? (
            <div>
              {conversation.map((item, index) => (
                <div key={index} className={`flex mb-2 ${index % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
                  <div className={`max-w-[40%] p-2 rounded-lg mb-1 ${index % 2 === 0 ? (darkTheme ? 'bg-gray-700' : 'bg-gray-200') : (darkTheme ? 'bg-blue-800' : 'bg-blue-200')}`}>
                    <strong>{item.agent}:</strong> {item.response}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No conversation yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
