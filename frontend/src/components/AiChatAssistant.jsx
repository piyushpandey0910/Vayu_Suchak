import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, AlertCircle } from 'lucide-react';
import { Card } from './Card';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export function AiChatAssistant({ city, currentAqi, pollutants }) {
  const { notifyRateLimit } = useApp();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: `Hello! I'm your **Vayu Suchak AI Health Assistant**. Based on current conditions in **${city}** (AQI: ${Math.round(currentAqi || 85)}), feel free to ask me any questions regarding mask usage, jogging, asthma management, or indoor air precautions.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const messagesEndRef = useRef(null);

  const quickPrompts = [
    "Can I go for a run/walk today?",
    "Should I wear an N95 mask outside?",
    "Is it safe for asthmatics right now?",
    "Do I need an air purifier at home?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    const userMsg = {
      id: String(Date.now()),
      sender: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const resp = await api.postAIChat(text, city, currentAqi, pollutants);
      const botMsg = {
        id: String(Date.now() + 1),
        sender: 'bot',
        text: resp.reply,
        source: resp.source,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      if (err.isRateLimit) {
        notifyRateLimit(err.message);
        setErrorMsg("Rate limit reached. Please wait a moment before sending another message.");
      } else {
        setErrorMsg("Could not connect to health advisor service. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="AI Health Assistant"
      subtitle="Personalized medical & environmental guidance powered by AI"
      className="flex flex-col h-[520px]"
    >
      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-3 mb-3 text-sm">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs ${
                  isUser ? 'bg-teal-700 text-white' : 'bg-slate-200 text-slate-700'
                }`}
              >
                {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
              </div>
              <div
                className={`max-w-[82%] px-3.5 py-2.5 rounded-xl ${
                  isUser
                    ? 'bg-teal-700 text-white rounded-br-none'
                    : 'bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200/60'
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed text-[13px]">
                  {m.text}
                </div>
                <div
                  className={`text-[10px] mt-1 text-right ${
                    isUser ? 'text-teal-200' : 'text-slate-400'
                  }`}
                >
                  {m.time} {m.source && `• ${m.source}`}
                </div>
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="bg-slate-100 px-3.5 py-2.5 rounded-xl rounded-bl-none text-slate-500 text-xs flex items-center gap-2 border border-slate-200/60">
              <Sparkles className="w-3.5 h-3.5 text-teal-700 animate-spin" />
              <span>Analyzing air quality metrics...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {errorMsg && (
        <div className="mb-2 p-2 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Suggested Quick Prompts */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-1 mb-2 no-scrollbar">
        {quickPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
            className="text-[11px] whitespace-nowrap bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-600 px-2.5 py-1 rounded-full border border-slate-200 transition-colors flex-shrink-0"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 pt-2 border-t border-slate-100"
      >
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask about outdoor health, masks, or air safety..."
          disabled={isLoading}
          className="flex-1 px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs md:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-700 focus:bg-white transition-all"
        />
        <button
          type="submit"
          disabled={!inputMessage.trim() || isLoading}
          className="px-3.5 py-2 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </Card>
  );
}
