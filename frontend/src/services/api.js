import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

export const chatService = {
  sendMessage: async (message, conversationId, attachments = []) => {
    const response = await api.post('/chat', {
      message,
      conversation_id: conversationId,
      attachments
    });
    return response.data;
  }
};

export const conversationService = {
  getConversations: async () => {
    const response = await api.get('/conversations');
    return response.data;
  },
  getConversation: async (id) => {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },
  createConversation: async (title = 'New Conversation') => {
    const response = await api.post('/conversations', { title });
    return response.data;
  },
  deleteConversation: async (id) => {
    const response = await api.delete(`/conversations/${id}`);
    return response.data;
  }
};

export const documentService = {
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  createDocument: async (content, filename, format = 'txt') => {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('filename', filename);
    formData.append('format', format);
    
    const response = await api.post('/documents/create', formData);
    return response.data;
  }
};

export const searchService = {
  searchWeb: async (query) => {
    const response = await api.post('/search', { query });
    return response.data;
  }
};

export default api;
