/**
 * Chat Component
 * 
 * Main chat interface for the HR Chatbot application.
 * Features:
 * - Real-time messaging with RAG-powered responses
 * - Domain badge display for knowledge base answers
 * - User profile display in header
 * - Auto-scrolling message list
 * - Loading states and animations
 * - Theme toggle and logout functionality
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { chatAPI } from '../services/api';
import ThemeToggle from './ThemeToggle';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Add welcome message
        setMessages([
            {
                id: 1,
                type: 'bot',
                text: `Bonjour ${user?.full_name || user?.username} ! Je suis votre assistant RH. Comment puis-je vous aider aujourd'hui ?`,
                timestamp: new Date(),
            },
        ]);
    }, [user]);

    const handleSendMessage = async (e) => {
        e.preventDefault();

        if (!inputMessage.trim() || loading) return;

        const userMessage = {
            id: Date.now(),
            type: 'user',
            text: inputMessage,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputMessage('');
        setLoading(true);

        try {
            const response = await chatAPI.sendMessage(inputMessage);

            const botMessage = {
                id: Date.now() + 1,
                type: 'bot',
                text: response.answer,
                domain: response.domain,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error('Failed to send message:', error);

            const errorMessage = {
                id: Date.now() + 1,
                type: 'bot',
                text: "Désolé, une erreur s'est produite. Veuillez réessayer.",
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="min-h-screen flex flex-col bg-[var(--color-bg-primary)]">
            {/* Header */}
            <header className="bg-primary-600 dark:bg-gray-800 text-white shadow-lg">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Chatbot RH</h1>
                        {user && (
                            <p className="text-sm text-primary-100 dark:text-gray-300">
                                {user.full_name} - {user.employee_type} ({user.department})
                            </p>
                        )}
                    </div>
                    <div className="flex items-center gap-3">
                        <ThemeToggle />
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors duration-200 text-sm font-medium"
                        >
                            Déconnexion
                        </button>
                    </div>
                </div>
            </header>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <div className="container mx-auto max-w-4xl">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'
                                } animate-slide-up`}
                        >
                            <div
                                className={
                                    message.type === 'user' ? 'message-user' : 'message-bot'
                                }
                            >
                                <p className="whitespace-pre-wrap">{message.text}</p>
                                {message.domain && (
                                    <div className="mt-2 flex items-center gap-2">
                                        <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-300 border border-primary-200 dark:border-primary-800">
                                            Domain: {message.domain}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start animate-slide-up">
                            <div className="message-bot">
                                <div className="flex space-x-2">
                                    <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                                    <div
                                        className="w-2 h-2 bg-current rounded-full animate-bounce"
                                        style={{ animationDelay: '0.1s' }}
                                    ></div>
                                    <div
                                        className="w-2 h-2 bg-current rounded-full animate-bounce"
                                        style={{ animationDelay: '0.2s' }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input */}
            <div className="border-t border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-4">
                <form
                    onSubmit={handleSendMessage}
                    className="container mx-auto max-w-4xl flex gap-2"
                >
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Posez votre question RH..."
                        className="input-field flex-1"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !inputMessage.trim()}
                        className="btn-primary px-6"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                            />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Chat;
