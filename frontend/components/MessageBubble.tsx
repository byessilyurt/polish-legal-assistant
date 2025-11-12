'use client';

import { ChatMessage } from '@/types/legal-types';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import SourceCitations from './SourceCitations';
import { User, Bot } from 'lucide-react';
import clsx from 'clsx';

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={clsx(
        'flex w-full mb-6 animate-slide-up',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div className={clsx('flex max-w-[85%] md:max-w-[75%]', isUser ? 'flex-row-reverse' : 'flex-row')}>
        {/* Avatar */}
        <div
          className={clsx(
            'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
            isUser ? 'bg-primary-600 ml-3' : 'bg-gray-200 mr-3'
          )}
        >
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-gray-600" />
          )}
        </div>

        {/* Message Content */}
        <div className="flex flex-col flex-1">
          <div
            className={clsx(
              'rounded-2xl px-4 py-3 shadow-sm',
              isUser
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-900'
            )}
          >
            {isUser ? (
              <p className="text-sm md:text-base whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-sm md:prose-base max-w-none prose-p:my-2 prose-p:leading-relaxed prose-ul:my-2 prose-ol:my-2">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="text-gray-900">{children}</p>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                    ul: ({ children }) => <ul className="list-disc pl-5 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal pl-5 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="text-gray-900">{children}</li>,
                    a: ({ href, children }) => (
                      <a href={href} className="text-primary-600 hover:text-primary-800 underline" target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* Timestamp */}
          <span
            className={clsx(
              'text-xs text-gray-500 mt-1 px-1',
              isUser ? 'text-right' : 'text-left'
            )}
          >
            {format(message.timestamp, 'h:mm a')}
          </span>

          {/* Sources for AI messages */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-2">
              <SourceCitations sources={message.sources} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
