import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { FileText, Link as LinkIcon, Image as ImageIcon } from 'lucide-react';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({node, inline, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    {...props}
                    children={String(children).replace(/\n$/, '')}
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                  />
                ) : (
                  <code {...props} className={className}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>

      {message.metadata?.sources?.length > 0 && (
        <div className="sources-container">
          <strong>Sources:</strong>
          <div className="sources-list">
            {message.metadata.sources.map((src, idx) => (
              <div key={idx} className="source-item">
                {src.type === 'document' ? (
                  <><FileText size={14} /> {src.name} (Page {src.page || 'N/A'})</>
                ) : (
                  <><LinkIcon size={14} /> <a href={src.url} target="_blank" rel="noreferrer">{src.title}</a></>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
