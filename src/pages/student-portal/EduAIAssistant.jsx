import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  Paperclip,
  User,
  RotateCcw,
  Loader2,
  AlertCircle
} from 'lucide-react';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import { useAuth } from '../../context/AuthContext';
import { aiAssistantService } from '../../services/aiAssistantService';

export function EduAIAssistant() {
  const { user, currentUser, role } = useAuth();
  const activeUser = user || currentUser;
  const userRole = role || activeUser?.role || 'student';
  const userName = activeUser?.full_name || activeUser?.name || 'there';

  const getInitialGreeting = () => {
    if (userRole === 'student') {
      return `Hello ${userName}! I am EduAI, your personal academic assistant. How can I help you today with your courses, attendance records, exam marks, or academic progress?`;
    } else if (userRole === 'teacher') {
      return `Hello Professor ${userName}! I am EduAI. You can ask me about class attendance, students at academic risk, or specific student performance analyses.`;
    } else {
      return `Hello ${userName}! I am EduAI. You can request institutional performance summaries, departmental risk distributions, or academic trend analysis.`;
    }
  };

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      message: getInitialGreeting(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputVal, setInputVal] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [suggestions, setSuggestions] = useState(aiAssistantService.getDefaultSuggestions(userRole));
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Update suggestions when user role changes
  useEffect(() => {
    setSuggestions(aiAssistantService.getDefaultSuggestions(userRole));
  }, [userRole]);

  const handleSend = async (e) => {
    e?.preventDefault();
    const query = inputVal.trim();
    if (!query || isLoading) return;

    setErrorMsg(null);
    const userTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      message: query,
      time: userTimestamp,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal('');
    setIsLoading(true);

    try {
      const responseData = await aiAssistantService.sendMessage(query);

      const aiMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        message: responseData.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        contextUsed: responseData.context_used,
      };

      setMessages((prev) => [...prev, aiMsg]);

      if (responseData.suggestions && Array.isArray(responseData.suggestions) && responseData.suggestions.length > 0) {
        setSuggestions(responseData.suggestions.map((s) => ({ label: s })));
      }
    } catch (err) {
      const errorMessageText = err.message || 'Unable to connect to the EduAI assistant. Please try again.';
      setErrorMsg(errorMessageText);

      const aiErrorReply = {
        id: Date.now() + 1,
        sender: 'ai',
        message: `⚠️ **Service Notice**: ${errorMessageText}`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isError: true,
      };
      setMessages((prev) => [...prev, aiErrorReply]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipClick = (promptText) => {
    setInputVal(promptText);
  };

  const handleClearChat = () => {
    setErrorMsg(null);
    setMessages([
      {
        id: Date.now(),
        sender: 'ai',
        message: getInitialGreeting(),
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setSuggestions(aiAssistantService.getDefaultSuggestions(userRole));
  };

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col space-y-4">
      {/* Header Banner */}
      <div className="flex items-center justify-between p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-xl shadow-soft">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-indigo-600 text-white flex items-center justify-center shadow-xs">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display font-bold text-base sm:text-lg text-on-surface">EduAI Academic Assistant</h1>
              <Badge variant="primary" size="sm">Live Connected</Badge>
            </div>
            <p className="text-xs text-on-surface-variant">
              Role-aware academic intelligence powered by real attendance, marks, and risk records.
            </p>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RotateCcw}
          onClick={handleClearChat}
        >
          Clear Chat
        </Button>
      </div>

      {/* Main Chat Box Container */}
      <div className="flex-1 bg-surface-container-lowest border border-outline-variant/60 rounded-2xl shadow-soft flex flex-col overflow-hidden">
        {/* Error Alert if present */}
        {errorMsg && (
          <div className="px-4 py-2 bg-error-container/40 border-b border-error/20 flex items-center gap-2 text-xs text-on-error-container">
            <AlertCircle className="w-4 h-4 text-error shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Messages Stream */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                  msg.sender === 'user'
                    ? 'bg-primary text-white'
                    : msg.isError
                    ? 'bg-error/10 text-error border border-error/20'
                    : 'bg-primary/10 text-primary border border-primary/20'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs ${
                  msg.sender === 'user'
                    ? 'bg-primary text-white rounded-tr-none'
                    : msg.isError
                    ? 'bg-error-container/20 text-on-surface border border-error/30 rounded-tl-none'
                    : 'bg-surface-container-low text-on-surface border border-outline-variant/40 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-line">{msg.message}</div>
                <span
                  className={`text-[10px] mt-2 block font-medium ${
                    msg.sender === 'user' ? 'text-blue-200' : 'text-on-surface-variant'
                  }`}
                >
                  {msg.time}
                </span>
              </div>
            </div>
          ))}

          {/* Loading Typing Indicator */}
          {isLoading && (
            <div className="flex gap-3 max-w-3xl">
              <div className="w-8 h-8 rounded-full bg-primary/10 text-primary border border-primary/20 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-2xl bg-surface-container-low text-on-surface border border-outline-variant/40 rounded-tl-none flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-primary animate-spin" />
                <span className="text-xs text-on-surface-variant">EduAI is analyzing academic records...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts Pills */}
        <div className="p-3 bg-surface-container-low/60 border-t border-outline-variant/30 flex items-center gap-2 overflow-x-auto no-scrollbar">
          <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1 flex-shrink-0 pl-1">
            <Sparkles className="w-3 h-3 text-primary" /> Suggestions:
          </span>
          {suggestions.map((prompt, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleChipClick(prompt.label)}
              className="px-3 py-1 bg-surface-container-lowest border border-outline-variant/50 hover:border-primary text-on-surface hover:text-primary rounded-full text-xs font-medium whitespace-nowrap transition-colors"
            >
              {prompt.label}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-3 sm:p-4 bg-surface-container-lowest border-t border-outline-variant/40 flex items-center gap-2">
          <button
            type="button"
            className="p-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-xl transition-colors"
            title="Attach assignment or lecture PDF"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={`Ask EduAI about your ${userRole === 'student' ? 'attendance, marks, or syllabus' : userRole === 'teacher' ? 'students, attendance, or risk insights' : 'institutional academic performance'}...`}
            className="flex-1 py-2 px-3 bg-surface-container-low border border-outline-variant/50 rounded-xl text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            disabled={isLoading}
          />
          <Button
            type="submit"
            variant="container"
            size="md"
            icon={isLoading ? Loader2 : Send}
            disabled={!inputVal.trim() || isLoading}
          >
            {isLoading ? 'Thinking...' : 'Send'}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default EduAIAssistant;
