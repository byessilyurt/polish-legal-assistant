export enum Category {
  ALL = 'all',
  IMMIGRATION = 'immigration',
  EMPLOYMENT = 'employment',
  HEALTHCARE = 'healthcare',
  BANKING = 'banking',
  TRAFFIC = 'traffic',
  POLICE = 'police',
}

export interface Source {
  organization: string;
  title: string;
  url: string;
  verified_date: string;
  relevance_score?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
  category?: Category;
}

export interface ChatRequest {
  query: string;
  category?: Category;
  conversation_history?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  category?: Category | null;
  confidence?: number;
}

export interface LegalDocument {
  id: string;
  title: string;
  organization: string;
  content: string;
  url: string;
  category: Category;
  verified_date: string;
  last_updated: string;
}

export const CATEGORY_LABELS: Record<Category, string> = {
  [Category.ALL]: 'All Categories',
  [Category.IMMIGRATION]: 'Immigration',
  [Category.EMPLOYMENT]: 'Employment',
  [Category.HEALTHCARE]: 'Healthcare',
  [Category.BANKING]: 'Banking',
  [Category.TRAFFIC]: 'Traffic',
  [Category.POLICE]: 'Police',
};

export const CATEGORY_COLORS: Record<Category, string> = {
  [Category.ALL]: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
  [Category.IMMIGRATION]: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
  [Category.EMPLOYMENT]: 'bg-green-100 text-green-700 hover:bg-green-200',
  [Category.HEALTHCARE]: 'bg-red-100 text-red-700 hover:bg-red-200',
  [Category.BANKING]: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
  [Category.TRAFFIC]: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200',
  [Category.POLICE]: 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200',
};
