'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import WelcomeScreen from '@/components/WelcomeScreen';
import CategoryFilter from '@/components/CategoryFilter';
import { Category } from '@/types/legal-types';
import { MessageCircle } from 'lucide-react';

export default function Home() {
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category>(Category.ALL);
  const [initialQuestion, setInitialQuestion] = useState<string | null>(null);

  const handleQuestionClick = (question: string) => {
    setInitialQuestion(question);
    setHasStartedChat(true);
  };

  const handleCategoryChange = (category: Category) => {
    setSelectedCategory(category);
  };

  const handleNewChat = () => {
    setHasStartedChat(false);
    setInitialQuestion(null);
    setSelectedCategory(Category.ALL);
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🇵🇱</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Polish Legal Assistant</h1>
              <p className="text-xs text-gray-500">Powered by OpenAI GPT-4</p>
            </div>
          </div>

          {hasStartedChat && (
            <button
              onClick={handleNewChat}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded-lg transition-colors"
            >
              <MessageCircle className="w-4 h-4" />
              <span>New Chat</span>
            </button>
          )}
        </div>
      </header>

      {/* Category Filter - only show when chat has started */}
      {hasStartedChat && (
        <CategoryFilter
          selectedCategory={selectedCategory}
          onSelectCategory={handleCategoryChange}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {hasStartedChat ? (
          <ChatInterfaceWrapper
            key={initialQuestion || 'chat'}
            initialCategory={selectedCategory}
            initialQuestion={initialQuestion}
          />
        ) : (
          <WelcomeScreen onQuestionClick={handleQuestionClick} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-2 px-4">
        <div className="max-w-7xl mx-auto">
          <p className="text-xs text-gray-500 text-center">
            This assistant provides general information. For specific legal advice, consult a qualified attorney.
          </p>
        </div>
      </footer>
    </div>
  );
}

// Wrapper component to handle initial question
function ChatInterfaceWrapper({
  initialCategory,
  initialQuestion,
}: {
  initialCategory: Category;
  initialQuestion: string | null;
}) {
  return (
    <ChatInterface
      initialCategory={initialCategory}
    />
  );
}
