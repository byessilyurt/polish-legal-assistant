'use client';

import { MessageCircle } from 'lucide-react';

interface WelcomeScreenProps {
  onQuestionClick: (question: string) => void;
}

const sampleQuestions = [
  {
    question: 'How do I get a residence permit in Poland?',
    category: 'Immigration',
  },
  {
    question: 'What is the difference between B2B and employment contract?',
    category: 'Employment',
  },
  {
    question: 'How to register with NFZ for healthcare?',
    category: 'Healthcare',
  },
  {
    question: 'I received a speeding ticket, what should I do?',
    category: 'Traffic',
  },
];

export default function WelcomeScreen({ onQuestionClick }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-12 animate-fade-in">
      {/* Hero Section */}
      <div className="text-center mb-12 max-w-2xl">
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            <div className="w-20 h-20 bg-primary-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-4xl">🇵🇱</span>
            </div>
            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
              <MessageCircle className="w-5 h-5 text-primary-600" />
            </div>
          </div>
        </div>

        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Polish Legal Assistant
        </h1>
        <p className="text-lg md:text-xl text-gray-600 mb-2">
          Get help with immigration, employment, healthcare, and daily life in Poland
        </p>
        <p className="text-sm text-gray-500">
          Powered by OpenAI GPT-4 with verified Polish government sources
        </p>
      </div>

      {/* Sample Questions */}
      <div className="w-full max-w-2xl">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 text-center">
          Popular Questions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sampleQuestions.map((item, index) => (
            <button
              key={index}
              onClick={() => onQuestionClick(item.question)}
              className="group p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-500 hover:shadow-md transition-all duration-200 text-left"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <MessageCircle className="w-5 h-5 text-primary-600 group-hover:text-primary-700" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 group-hover:text-primary-700 mb-1">
                    {item.question}
                  </p>
                  <span className="inline-block text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                    {item.category}
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Footer Note */}
      <div className="mt-12 text-center text-sm text-gray-500 max-w-md">
        <p>
          This assistant provides general information based on official Polish sources.
          For specific legal advice, please consult a qualified attorney.
        </p>
      </div>
    </div>
  );
}
