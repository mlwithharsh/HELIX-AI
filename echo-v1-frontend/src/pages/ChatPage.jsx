import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useAI } from '../context/AIContext';
import FeedbackBar from '../components/FeedbackBar';
import PersonalitySelector from '../components/PersonalitySelector';
import { 
  Send, 
  ArrowLeft, 
  Heart,
  Sparkles, 
  Loader2
} from 'lucide-react';

const ChatPage = () => {
  const [inputText, setInputText] = useState('');
  const { isProcessing, processText, history, profile, submitFeedback, systemLabel, personality } = useAI();
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history, isProcessing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || isProcessing) return;
    
    const text = inputText;
    setInputText('');
    try {
      await processText(text);
    } catch (err) {
      console.error('Failed to send text', err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const activePersonaName = personality === 'suzi' ? 'Suzi' : 'Echo';

  return (
    <div id="chat-page" className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Chat Header */}
      <header className="px-6 py-4 border-b border-black/5 flex items-center justify-between bg-[rgba(244,239,230,0.92)] backdrop-blur-md relative z-20">
        <div className="flex items-center space-x-4">
          <Link to="/" id="back-button" className="p-2 rounded-full hover:bg-black/5 text-text-secondary hover:text-text-primary transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h2 className="text-sm font-bold text-text-primary tracking-wide">{activePersonaName}</h2>
            <div className="flex items-center space-x-2">
              <div className="w-1.5 h-1.5 rounded-full bg-[#7f9476] animate-pulse" />
              <span className="text-[10px] text-text-muted font-medium">Online · Ready to listen</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <PersonalitySelector />
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        <div className="h-full">
          {/* Chat Messages */}
          <div className="overflow-y-auto px-6 py-8 space-y-8 scrollbar-hide">
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Empty State */}
              {history.length === 0 && !isProcessing && (
                <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#e8e1d5] to-[#d5dfd0] flex items-center justify-center">
                    <Heart className="w-8 h-8 text-[#7f9476]/60" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-xl font-bold text-text-primary">How are you feeling today?</h3>
                    <p className="text-text-secondary text-sm max-w-xs mx-auto leading-relaxed">
                      I'm here to listen. Share your thoughts, feelings, or just say hello.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center gap-2 max-w-sm">
                    {['Hey there 👋', 'I need to talk', 'Help me think'].map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => { setInputText(suggestion); }}
                        className="px-4 py-2 rounded-full bg-white/80 border border-black/5 text-sm text-text-secondary hover:bg-white hover:text-text-primary hover:shadow-sm transition-all duration-300"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Messages */}
              {history.map((msg, idx) => (
                <div key={msg.interaction_id || idx} className="space-y-4">
                  {/* User Message */}
                  {(msg.input_text || msg.text) && (
                    <motion.div 
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className="flex justify-end"
                    >
                      <div className="max-w-[75%] px-5 py-3.5 rounded-2xl rounded-br-md bg-[#6d7b68] text-white shadow-sm">
                        <p className="text-[14px] leading-relaxed">{msg.input_text || msg.text}</p>
                      </div>
                    </motion.div>
                  )}

                  {/* AI Response */}
                  {msg.response && (
                    <motion.div 
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.1 }}
                      className="flex justify-start"
                    >
                      <div className="max-w-[80%] space-y-3">
                        {/* Avatar + Name */}
                        <div className="flex items-center space-x-2.5">
                          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#c8b89b] to-[#7f9476] flex items-center justify-center shadow-sm">
                            <Sparkles className="w-3.5 h-3.5 text-white" />
                          </div>
                          <span className="text-[11px] font-semibold text-text-muted">{activePersonaName}</span>
                        </div>
                        
                        {/* Response Bubble */}
                        <div className="ml-9 px-5 py-3.5 rounded-2xl rounded-tl-md bg-white border border-black/5 text-text-primary shadow-[0_8px_30px_rgba(61,75,63,0.06)]">
                          <p className="text-[14px] leading-[1.7]">{msg.response}</p>
                        </div>

                        {/* Feedback */}
                        {msg.interaction_id && !msg.pending && (
                          <div className="ml-9">
                            <FeedbackBar interactionId={msg.interaction_id} onSubmit={submitFeedback} />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </div>
              ))}

              {/* Typing Indicator */}
              {isProcessing && (
                <motion.div 
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex items-center space-x-2.5">
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#c8b89b] to-[#7f9476] flex items-center justify-center shadow-sm">
                      <Loader2 className="w-3.5 h-3.5 text-white animate-spin" />
                    </div>
                    <div className="px-5 py-3.5 rounded-2xl rounded-tl-md bg-white border border-black/5 shadow-sm">
                      <div className="flex space-x-1.5">
                        <div className="w-2 h-2 bg-[#7f9476]/40 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-[#7f9476]/40 rounded-full animate-bounce [animation-delay:0.15s]" />
                        <div className="w-2 h-2 bg-[#7f9476]/40 rounded-full animate-bounce [animation-delay:0.3s]" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 md:p-6 bg-[rgba(244,239,230,0.92)] backdrop-blur-md relative z-20 border-t border-black/5">
        <div className="max-w-3xl mx-auto relative">
          <form onSubmit={handleSubmit} className="relative group">
            <textarea
              ref={textareaRef}
              id="chat-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Share your thoughts..."
              className="w-full bg-white border border-black/8 rounded-2xl px-5 py-4 pr-16 text-text-primary placeholder-text-muted resize-none outline-none focus:border-[#7f9476]/30 focus:shadow-[0_0_0_3px_rgba(127,148,118,0.08)] transition-all duration-300 min-h-[56px] max-h-[160px] text-[14px] leading-relaxed shadow-sm"
              rows="1"
            />
            <button
              type="submit"
              id="send-button"
              disabled={!inputText.trim() || isProcessing}
              className={`absolute right-3 bottom-3 p-3 rounded-xl transition-all duration-300 ${
                !inputText.trim() || isProcessing
                  ? 'bg-[#ece6db] text-text-muted cursor-not-allowed'
                  : 'bg-gradient-to-r from-[#bda98a] to-[#7f9476] text-white hover:scale-105 active:scale-95 shadow-md hover:shadow-lg'
              }`}
            >
              {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>
          <p className="mt-2 text-[10px] text-center text-text-muted">
            Your conversations are private and confidential.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
