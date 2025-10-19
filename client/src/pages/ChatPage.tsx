import { useState, useRef, useEffect } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import { useSendMessage, useChatHistory, useClearChatHistory } from '../hooks/useApi';
import { 
  Send, 
  Upload, 
  Trash2, 
  Bot, 
  User, 
  Loader2,
  FileText,
  AlertCircle
} from 'lucide-react';

interface Message {
  message_id: string;
  timestamp: string;
  user_message: string;
  agent_response: string;
  agent_name: string;
  success: boolean;
}

export default function ChatPage() {
  const { authenticated, user } = usePrivy();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const walletAddress = user?.wallet?.address || '';
  
  const { data: chatHistory, isLoading: historyLoading } = useChatHistory(walletAddress);
  const sendMessageMutation = useSendMessage();
  const clearHistoryMutation = useClearChatHistory();

  const messages: Message[] = chatHistory?.messages || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (file?: File) => {
    if ((!input.trim() && !file) || !authenticated || isLoading) return;

    setIsLoading(true);
    try {
      await sendMessageMutation.mutateAsync({
        walletAddress,
        message: input.trim() || (file ? `Upload file: ${file.name}` : ''),
        file: file,
      });
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearHistory = async () => {
    if (!authenticated) return;
    
    try {
      await clearHistoryMutation.mutateAsync(walletAddress);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && authenticated) {
      // Send the file directly through chat
      handleSendMessage(file);
    }
  };

  if (!authenticated) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center">
          <Bot className="w-16 h-16 text-eco-600 dark:text-eco-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Connect Your Wallet to Start Chatting
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Connect your wallet to chat with our AI sustainability assistant and get personalized recommendations.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Bot className="w-8 h-8 text-eco-600 dark:text-eco-400" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                EcoChain AI Assistant
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                Ask me about sustainability, upload documents, or get recommendations
              </p>
            </div>
          </div>
          
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              disabled={clearHistoryMutation.isPending}
              className="btn-secondary text-sm"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear History
            </button>
          )}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="card mb-6">
        <div className="h-96 overflow-y-auto space-y-4">
          {historyLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-6 h-6 animate-spin text-eco-600" />
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center text-gray-500 dark:text-gray-400 py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Start a conversation with our AI assistant!</p>
              <p className="text-sm mt-2">Try asking: "How can I improve my sustainability score?"</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.message_id} className="space-y-3">
                {/* User Message */}
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-eco-100 dark:bg-eco-900/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-eco-600 dark:text-eco-400" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                      <p className="text-gray-900 dark:text-white">{message.user_message}</p>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>

                {/* Agent Response */}
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-blue-50 dark:bg-blue-900/10 rounded-lg p-3">
                      {message.success ? (
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                            {message.agent_response}
                          </p>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
                          <AlertCircle className="w-4 h-4" />
                          <p>Failed to get response. Please try again.</p>
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {message.agent_name} • {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1">
                <div className="bg-blue-50 dark:bg-blue-900/10 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                    <p className="text-gray-600 dark:text-gray-300">AI is thinking...</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="card">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about sustainability, upload documents, or get recommendations..."
              className="input-field resize-none"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <div className="flex flex-col space-y-2">
            <input
              type="file"
              id="file-upload"
              accept=".json"
              onChange={handleFileUpload}
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className="btn-secondary p-2 cursor-pointer"
              title="Upload JSON file"
            >
              <Upload className="w-4 h-4" />
            </label>
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              className="btn-primary p-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
        
        <div className="mt-3 text-sm text-gray-500 dark:text-gray-400">
          <p>💡 <strong>Try asking:</strong></p>
          <ul className="list-disc list-inside space-y-1 mt-1">
            <li>"How much credits do I have?"</li>
            <li>"What do I need for 100 credits?"</li>
            <li>"How can I improve my sustainability score?"</li>
            <li>"Upload this document" (then use the upload button)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
