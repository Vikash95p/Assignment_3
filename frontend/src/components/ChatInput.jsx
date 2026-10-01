import React, { useState, useRef } from 'react';
import { Send, Paperclip, X, Loader } from 'lucide-react';
import { documentService } from '../services/api';

const ChatInput = ({ onSend, loading }) => {
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleSend = () => {
    if (text.trim() || attachments.length > 0) {
      onSend(text, attachments.map(a => a.id));
      setText('');
      setAttachments([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const doc = await documentService.uploadDocument(file);
      setAttachments(prev => [...prev, doc]);
    } catch (err) {
      alert("Failed to upload document");
    } finally {
      setUploading(false);
      e.target.value = null; // reset
    }
  };

  const removeAttachment = (id) => {
    setAttachments(prev => prev.filter(a => a.id !== id));
  };

  return (
    <div className="input-area">
      <div className="input-container">
        {attachments.length > 0 && (
          <div className="attachments-preview">
            {attachments.map(doc => (
              <div key={doc.id} className="attachment-chip">
                {doc.file_type?.startsWith('image/') ? (
                  <img 
                    src={`http://localhost:8000/api/documents/${doc.id}/content`} 
                    alt={doc.filename}
                    style={{ height: '32px', width: '32px', objectFit: 'cover', borderRadius: '4px' }}
                  />
                ) : (
                  <span>{doc.filename}</span>
                )}
                <X size={14} style={{ cursor: 'pointer', marginLeft: '4px' }} onClick={() => removeAttachment(doc.id)} />
              </div>
            ))}
          </div>
        )}
        
        <div className="input-row">
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            onChange={handleFileChange} 
          />
          <button 
            className="icon-btn" 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading || loading}
            title="Attach Document or Image"
          >
            {uploading ? <Loader size={20} className="animate-spin" /> : <Paperclip size={20} />}
          </button>
          
          <textarea
            className="chat-input"
            placeholder="Type your message..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={1}
          />
          
          <button 
            className="icon-btn primary" 
            onClick={handleSend}
            disabled={(!text.trim() && attachments.length === 0) || loading}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
