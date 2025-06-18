import React, { createContext, useState, useContext, useEffect } from 'react';

// Create context
const ChatContext = createContext();

// Chat history structure:
// {
//   id: string,
//   title: string,
//   messages: Array<{type: 'user'|'bot', content: string, sources?: Array}>
//   createdAt: Date,
//   updatedAt: Date
// }

export const ChatProvider = ({ children }) => {
  const [chatHistory, setChatHistory] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load chat history from localStorage on component mount
  useEffect(() => {
    const storedChatHistory = localStorage.getItem('chatHistory');
    if (storedChatHistory) {
      try {
        const parsedHistory = JSON.parse(storedChatHistory);
        setChatHistory(parsedHistory);
        
        // Set active chat to the most recent one if it exists
        if (parsedHistory.length > 0) {
          setActiveChatId(parsedHistory[0].id);
        }
      } catch (error) {
        console.error('Error parsing chat history from localStorage:', error);
      }
    }
  }, []);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  // Get the active chat
  const activeChat = chatHistory.find(chat => chat.id === activeChatId) || null;

  // Create a new chat
  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    setChatHistory([newChat, ...chatHistory]);
    setActiveChatId(newChat.id);
    return newChat;
  };

  // Add a message to the active chat
  const addMessage = (message) => {
    if (!activeChatId) {
      const newChat = createNewChat();
      setChatHistory(prev => {
        const updated = prev.map(chat => 
          chat.id === newChat.id 
            ? { 
                ...chat, 
                messages: [...chat.messages, message],
                updatedAt: new Date().toISOString(),
                title: message.type === 'user' ? generateChatTitle(message.content) : chat.title
              }
            : chat
        );
        return updated;
      });
    } else {
      setChatHistory(prev => {
        const updated = prev.map(chat => 
          chat.id === activeChatId 
            ? { 
                ...chat, 
                messages: [...chat.messages, message],
                updatedAt: new Date().toISOString(),
                // Update title if this is the first user message
                title: chat.messages.length === 0 && message.type === 'user' 
                  ? generateChatTitle(message.content) 
                  : chat.title
              }
            : chat
        );
        return updated;
      });
    }
  };

  // Generate a title from the first user message
  const generateChatTitle = (content) => {
    // Truncate to first 20 characters or first line
    const title = content.split('\n')[0].trim().substring(0, 20);
    return title + (title.length >= 20 ? '...' : '');
  };

  // Delete a chat
  const deleteChat = (chatId) => {
    setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
    
    // If the deleted chat was active, set the first available chat as active
    if (chatId === activeChatId) {
      const remainingChats = chatHistory.filter(chat => chat.id !== chatId);
      if (remainingChats.length > 0) {
        setActiveChatId(remainingChats[0].id);
      } else {
        setActiveChatId(null);
      }
    }
  };

  // Clear all chat history
  const clearAllChats = () => {
    setChatHistory([]);
    setActiveChatId(null);
    localStorage.removeItem('chatHistory');
  };

  return (
    <ChatContext.Provider value={{ 
      chatHistory, 
      activeChat, 
      activeChatId, 
      setActiveChatId, 
      createNewChat, 
      addMessage, 
      deleteChat, 
      clearAllChats,
      isLoading,
      setIsLoading
    }}>
      {children}
    </ChatContext.Provider>
  );
};

// Custom hook to use the chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}; 