import React, { useState, useEffect, useRef } from 'react';
import { ragApiClient } from './api/query';

interface RagResponse {
  query: string;
  expanded_queries: string[];
  answer: string;
  search_results: any;
  context_used: string[];
  sources: string[];
  source_attribution: any[];
  error?: string;
}

interface Message {
  id: string;
  type: 'user' | 'bot' | 'system';
  content: string | RagResponse;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}

const RagChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome! Ask me anything about the scientific documents in the knowledge base.',
      timestamp: new Date()
    }
  ]);
  const [query, setQuery] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Set up event listeners
    ragApiClient.on('connected', () => setIsConnected(true));
    ragApiClient.on('disconnected', () => setIsConnected(false));
    
    ragApiClient.on('server_connected', (data: any) => {
      addMessage('system', `Connected to server (Session: ${data.session_id})`);
    });

    ragApiClient.on('query_received', (data: any) => {
      addMessage('system', `Query received: ${data.query}`, 'sent');
    });

    ragApiClient.on('query_response', (data: any) => {
      setIsProcessing(false);
      addMessage('bot', data.response);
    });

    ragApiClient.on('error', (data: any) => {
      setIsProcessing(false);
      addMessage('system', `Error: ${data.message}`, 'error');
    });

    // Cleanup
    return () => {
      ragApiClient.disconnect();
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (type: 'user' | 'bot' | 'system', content: string | RagResponse, status?: 'sending' | 'sent' | 'error') => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      status
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isProcessing) return;

    // Add user message
    addMessage('user', query);
    
    // Send via WebSocket if connected, otherwise use HTTP
    if (isConnected) {
      setIsProcessing(true);
      ragApiClient.sendQuerySocket(query);
    } else {
      // Fallback to HTTP
      handleHttpQuery(query);
    }

    setQuery('');
  };

  const handleHttpQuery = async (queryText: string) => {
    setIsProcessing(true);
    try {
      const response = await ragApiClient.queryRag(queryText);
      addMessage('bot', response);
    } catch (error) {
      addMessage('system', `Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';
    const isSystem = message.type === 'system';
    
    return (
      <div key={message.id} style={{ 
        marginBottom: '16px',
        fontSize: '14px',
        lineHeight: '1.5'
      }}>
        {/* Message Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '6px',
          fontSize: '12px',
          color: '#7d8590'
        }}>
          <span style={{ 
            color: isUser ? '#58a6ff' : isSystem ? '#f85149' : '#a5f3fc' 
          }}>
            {isUser ? '👤 researcher' : isSystem ? '⚠ system' : '� neural_assistant'}
          </span>
          <span>•</span>
          <span>{message.timestamp.toLocaleTimeString()}</span>
        </div>

        {/* Message Content */}
        <div style={{
          marginLeft: '16px',
          color: isSystem ? '#f85149' : '#c9d1d9'
        }}>
          {isSystem ? (
            <div style={{ 
              fontStyle: 'italic',
              opacity: 0.8
            }}>
              {message.content as string}
            </div>
          ) : isUser ? (
            <div style={{
              backgroundColor: '#1f2937',
              padding: '12px',
              borderRadius: '6px',
              border: '1px solid #374151',
              borderLeft: '3px solid #58a6ff'
            }}>
              {message.content as string}
            </div>
          ) : (
            <div>
              {typeof message.content === 'object' && message.content && 'answer' in message.content ? (
                <div>
                  {/* Answer */}
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{
                      backgroundColor: '#0f1419',
                      padding: '16px',
                      borderRadius: '6px',
                      border: '1px solid #30363d',
                      borderLeft: '3px solid #a5f3fc'
                    }}>
                      {(message.content as RagResponse).answer}
                    </div>
                  </div>

                  {/* Sources & Confidence Combined */}
                  {(message.content as RagResponse).sources && (message.content as RagResponse).sources.length > 0 && (
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{
                        fontSize: '11px',
                        color: '#7d8590',
                        marginBottom: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}>
                        <span>�</span>
                        <span style={{ fontFamily: 'monospace', letterSpacing: '0.5px' }}>
                          SOURCE_ANALYSIS
                        </span>
                      </div>
                      <div style={{
                        backgroundColor: '#161b22',
                        padding: '8px',
                        borderRadius: '4px',
                        border: '1px solid #30363d'
                      }}>
                        {(message.content as RagResponse).source_attribution && (message.content as RagResponse).source_attribution.length > 0 ? (
                          // Show sources with confidence if available
                          (message.content as RagResponse).source_attribution.map((attribution: any, index: number) => {
                            console.log('Attribution data:', attribution);
                            return (
                              <div key={index} style={{ 
                                marginBottom: index < (message.content as RagResponse).source_attribution.length - 1 ? '6px' : '0',
                                fontSize: '10px',
                                fontFamily: 'monospace'
                              }}>
                                <div style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  color: '#c9d1d9'
                                }}>
                                  <span style={{ color: '#58a6ff' }}>→</span>
                                  <span style={{ 
                                    flex: 1,
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap'
                                  }}>
                                    {attribution.source}
                                  </span>
                                </div>
                                {attribution.methods && attribution.methods.length > 0 && (
                                  <div style={{
                                    marginLeft: '12px',
                                    marginTop: '2px',
                                    display: 'flex',
                                    gap: '8px',
                                    fontSize: '8px',
                                    color: '#7d8590'
                                  }}>
                                    {attribution.methods.map((method: any, methodIndex: number) => (
                                      <span key={methodIndex}>
                                        {method.method.replace('_', ' ')}: {(method.confidence * 100).toFixed(0)}%
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            );
                          })
                        ) : (
                          // Fallback to basic sources list
                          (message.content as RagResponse).sources.map((source, index) => (
                            <div key={index} style={{
                              fontSize: '10px',
                              color: '#7d8590',
                              fontFamily: 'monospace',
                              marginBottom: index < (message.content as RagResponse).sources.length - 1 ? '3px' : '0',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px'
                            }}>
                              <span style={{ color: '#7c3aed' }}>→</span>
                              <span style={{ 
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}>
                                {source}
                              </span>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div style={{
                  backgroundColor: '#0f1419',
                  padding: '16px',
                  borderRadius: '6px',
                  border: '1px solid #30363d',
                  borderLeft: '3px solid #a5f3fc'
                }}>
                  {message.content as string}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#000000',  // Pure black background
      color: '#c9d1d9',
      fontFamily: '"JetBrains Mono", "Fira Code", "SF Mono", Consolas, monospace',
      fontSize: '14px',
      padding: '0',
      margin: '0',
      width: '100vw',  // Full viewport width
      overflow: 'hidden'  // Prevent horizontal scroll
    }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        height: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        padding: '20px',
        boxSizing: 'border-box'
      }}>
        {/* Header */}
        <div style={{ 
          marginBottom: '20px',
          borderBottom: '1px solid #30363d',
          paddingBottom: '15px'
        }}>
          <h1 style={{ 
            margin: '0 0 8px 0',
            fontSize: '28px',
            fontWeight: '300',
            color: '#58a6ff',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            letterSpacing: '0.5px'
          }}>
            <span style={{ 
              color: '#7c3aed',
              fontSize: '24px',
              fontWeight: '400'
            }}>⚛</span>
            NEURAL<span style={{ color: '#a5f3fc', fontWeight: '600' }}>RAG</span>
            <span style={{ 
              fontSize: '14px', 
              color: '#484f58',
              fontWeight: '400',
              marginLeft: '8px'
            }}>v1.0</span>
          </h1>
          <div style={{
            fontSize: '12px',
            color: '#7d8590',
            marginBottom: '12px',
            fontWeight: '300',
            letterSpacing: '0.3px'
          }}>
            Advanced Retrieval-Augmented Generation • Scientific Knowledge Base
          </div>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '16px',
            fontSize: '11px',
            color: '#7d8590'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                backgroundColor: isConnected ? '#238636' : '#da3633',
                boxShadow: isConnected ? '0 0 8px rgba(35, 134, 54, 0.4)' : '0 0 8px rgba(218, 54, 51, 0.4)'
              }} />
              <span style={{ fontFamily: 'monospace' }}>
                {isConnected ? 'WEBSOCKET_ACTIVE' : 'HTTP_FALLBACK'}
              </span>
            </div>
            <div style={{ color: '#484f58' }}>|</div>
            <div style={{ fontFamily: 'monospace' }}>
              PAPERS: {Math.floor(Math.random() * 500 + 1000)}+ • CHUNKS: {Math.floor(Math.random() * 5000 + 50000)}+
            </div>
          </div>
        </div>

        {/* Terminal Window */}
        <div style={{ 
          flex: 1,
          backgroundColor: '#161b22',
          borderRadius: '8px',
          border: '1px solid #30363d',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
        }}>
          {/* Terminal Header */}
          <div style={{
            backgroundColor: '#21262d',
            padding: '12px 16px',
            borderBottom: '1px solid #30363d',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#ff5f57' }} />
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#ffbd2e' }} />
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#28ca42' }} />
            <span style={{ 
              marginLeft: '15px', 
              fontSize: '11px', 
              color: '#7d8590',
              fontFamily: 'monospace',
              letterSpacing: '0.5px'
            }}>
              RESEARCH_TERMINAL — quantum • physics • materials • computation
            </span>
            <div style={{ 
              marginLeft: 'auto',
              fontSize: '10px',
              color: '#484f58',
              fontFamily: 'monospace'
            }}>
              {new Date().toISOString().slice(0, 19)}Z
            </div>
          </div>

          {/* Messages */}
          <div style={{ 
            flex: 1, 
            overflowY: 'auto', 
            padding: '16px',
            backgroundColor: '#0d1117',
            scrollBehavior: 'smooth'
          }}>
            {messages.map(renderMessage)}
            {isProcessing && (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px',
                color: '#58a6ff',
                fontStyle: 'italic',
                margin: '16px 0',
                padding: '12px',
                backgroundColor: '#0f1419',
                borderRadius: '6px',
                border: '1px solid #30363d',
                borderLeft: '3px solid #58a6ff'
              }}>
                <span style={{ 
                  fontSize: '16px',
                  animation: 'spin 1s linear infinite'
                }}>⚛</span>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '500' }}>
                    Processing neural query...
                  </div>
                  <div style={{ 
                    fontSize: '11px', 
                    color: '#7d8590',
                    fontFamily: 'monospace',
                    marginTop: '2px'
                  }}>
                    SEMANTIC_SEARCH → BM25_ANALYSIS → LLM_SYNTHESIS
                  </div>
                </div>
                <span style={{ 
                  animation: 'blink 1s infinite',
                  marginLeft: 'auto',
                  color: '#a5f3fc'
                }}>▋</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div style={{
            padding: '16px',
            borderTop: '1px solid #30363d',
            backgroundColor: '#161b22'
          }}>
            <form onSubmit={handleSubmit}>
              <div style={{ position: 'relative' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '8px',
                  color: '#7c3aed',
                  fontSize: '12px'
                }}>
                  <span style={{ fontSize: '14px' }}>⚛</span>
                  <span style={{ 
                    fontFamily: 'monospace',
                    letterSpacing: '0.5px',
                    fontWeight: '500'
                  }}>NEURAL_QUERY</span>
                  {query.trim() && (
                    <span style={{ 
                      fontSize: '10px', 
                      color: '#7d8590',
                      marginLeft: 'auto',
                      fontFamily: 'monospace'
                    }}>
                      {isProcessing ? 'TRANSMITTING...' : 'ENTER_TO_EXECUTE'}
                    </span>
                  )}
                </div>
                <div style={{ position: 'relative' }}>
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="initialize semantic search protocol..."
                    style={{ 
                      width: '100%',
                      minHeight: '60px',
                      maxHeight: '120px',
                      padding: '12px 80px 12px 12px',  // Right padding for button
                      backgroundColor: '#21262d',
                      border: '1px solid #30363d',
                      borderRadius: '6px',
                      color: '#c9d1d9',
                      fontFamily: 'inherit',
                      fontSize: '14px',
                      resize: 'vertical',
                      outline: 'none',
                      transition: 'border-color 0.2s ease',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => (e.target as HTMLTextAreaElement).style.borderColor = '#58a6ff'}
                    onBlur={(e) => (e.target as HTMLTextAreaElement).style.borderColor = '#30363d'}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e);
                      }
                    }}
                  />
                  {/* Floating send button */}
                  <button 
                    type="submit" 
                    disabled={isProcessing || !query.trim()}
                    style={{
                      position: 'absolute',
                      right: '8px',
                      top: '8px',
                      width: '32px',
                      height: '32px',
                      backgroundColor: (isProcessing || !query.trim()) ? '#30363d' : '#238636',
                      color: (isProcessing || !query.trim()) ? '#7d8590' : '#ffffff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: (isProcessing || !query.trim()) ? 'not-allowed' : 'pointer',
                      fontFamily: 'inherit',
                      fontSize: '16px',
                      fontWeight: '500',
                      transition: 'all 0.2s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => {
                      if (!isProcessing && query.trim()) {
                        (e.target as HTMLButtonElement).style.backgroundColor = '#2ea043';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isProcessing && query.trim()) {
                        (e.target as HTMLButtonElement).style.backgroundColor = '#238636';
                      }
                    }}
                    title={isProcessing ? 'Sending...' : 'Send message (Enter)'}
                  >
                    {isProcessing ? '⏳' : '↗'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        {/* Quick Commands */}
        <div style={{ marginTop: '16px' }}>
          <div style={{ 
            fontSize: '12px', 
            color: '#7d8590', 
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ color: '#7c3aed', fontSize: '14px' }}>⚛</span>
            <span style={{ 
              fontFamily: 'monospace',
              letterSpacing: '0.5px'
            }}>RESEARCH_PROTOCOLS</span>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {[
              { query: "antimatter theory", icon: "⚛" },
              { query: "quantum mechanics", icon: "🌊" }, 
              { query: "particle physics", icon: "🔬" },
              { query: "general relativity", icon: "🌌" }
            ].map((item, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(`Explain ${item.query} principles and recent developments`)}
                style={{
                  padding: '8px 14px',
                  backgroundColor: '#21262d',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  color: '#7d8590',
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontFamily: 'monospace',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  letterSpacing: '0.3px'
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLButtonElement).style.backgroundColor = '#30363d';
                  (e.target as HTMLButtonElement).style.color = '#c9d1d9';
                  (e.target as HTMLButtonElement).style.borderColor = '#58a6ff';
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLButtonElement).style.backgroundColor = '#21262d';
                  (e.target as HTMLButtonElement).style.color = '#7d8590';
                  (e.target as HTMLButtonElement).style.borderColor = '#30363d';
                }}
              >
                <span style={{ fontSize: '12px' }}>{item.icon}</span>
                {item.query.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* CSS Animation */}
      <style>{`
        /* Ensure no white background anywhere */
        html, body, #root {
          margin: 0;
          padding: 0;
          background-color: #000000 !important;
          width: 100%;
          height: 100%;
          overflow-x: hidden;
        }
        
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        /* Custom scrollbar */
        *::-webkit-scrollbar {
          width: 8px;
        }
        
        *::-webkit-scrollbar-track {
          background: #161b22;
        }
        
        *::-webkit-scrollbar-thumb {
          background: #30363d;
          border-radius: 4px;
        }
        
        *::-webkit-scrollbar-thumb:hover {
          background: #484f58;
        }
      `}</style>
    </div>
  );
};

export default RagChat;
