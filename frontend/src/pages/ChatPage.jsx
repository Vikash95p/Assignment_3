import React, { useState, useEffect } from 'react';
import { PlusCircle, MessageSquare } from 'lucide-react';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import { chatService, conversationService } from '../services/api';

const ChatPage = () => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const convs = await conversationService.getConversations();
      setConversations(convs);
    } catch (err) {
      console.error('Failed to load conversations', err);
    }
  };

  const loadConversation = async (id) => {
    try {
      const conv = await conversationService.getConversation(id);
      setCurrentConversation(conv.id);
      setMessages(conv.messages || []);
    } catch (err) {
      console.error('Failed to load conversation', err);
    }
  };

  const handleNewChat = () => {
    setCurrentConversation(null);
    setMessages([]);
  };

  const handleSendMessage = async (text, attachments) => {
    try {
      setLoading(true);
      
      // Optimistically add user message
      const userMsg = { role: 'user', content: text, metadata: { attachments } };
      setMessages(prev => [...prev, userMsg]);
      
      const response = await chatService.sendMessage(text, currentConversation, attachments);
      
      if (!currentConversation && response.conversation_id) {
        setCurrentConversation(response.conversation_id);
        loadConversations(); // refresh list
      }
      
      // Add assistant response
      setMessages(prev => [...prev, {
        role: response.role,
        content: response.content,
        metadata: { sources: response.sources }
      }]);
      
    } catch (err) {
      console.error('Failed to send message', err);
      // Optional: Add an error message bubble
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <PlusCircle size={20} />
          New Chat
        </button>
        
        <div className="conversation-list">
          {conversations.map(conv => (
            <div 
              key={conv.id} 
              className={`conversation-item ${currentConversation === conv.id ? 'active' : ''}`}
              onClick={() => loadConversation(conv.id)}
            >
              <MessageSquare size={16} />
              {conv.title}
            </div>
          ))}
        </div>
      </div>
      
      <div className="chat-area">
        <ChatWindow messages={messages} loading={loading} />
        <ChatInput onSend={handleSendMessage} loading={loading} />
      </div>
    </div>
  );
};

export default ChatPage;
