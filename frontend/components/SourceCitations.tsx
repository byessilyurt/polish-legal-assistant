'use client';

import { useState } from 'react';
import { Source } from '@/types/legal-types';
import { ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { format } from 'date-fns';

interface SourceCitationsProps {
  sources: Source[];
}

export default function SourceCitations({ sources }: SourceCitationsProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!sources || sources.length === 0) {
    return null;
  }

  const formatDate = (dateString: string) => {
    try {
      if (!dateString) return 'Date unavailable';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return dateString; // Return as-is if invalid
      return format(date, 'MMM d, yyyy');
    } catch {
      return dateString || 'Date unavailable';
    }
  };

  return (
    <div className="mt-4 border-t border-gray-200 pt-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
      >
        {isExpanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
        <span>Sources ({sources.length})</span>
      </button>

      {isExpanded && (
        <div className="mt-3 space-y-2 animate-fade-in">
          {sources.map((source, index) => (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group block p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors duration-200"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium bg-blue-200 text-blue-700 rounded-full">
                      {index + 1}
                    </span>
                    <h4 className="text-sm font-semibold text-gray-900 truncate">
                      {source.organization}
                    </h4>
                  </div>
                  <p className="mt-1 text-sm text-gray-700 line-clamp-2">
                    {source.title}
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    Verified: {formatDate(source.verified_date)}
                  </p>
                </div>
                <ExternalLink className="ml-3 w-4 h-4 text-blue-600 group-hover:text-blue-800 flex-shrink-0" />
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
