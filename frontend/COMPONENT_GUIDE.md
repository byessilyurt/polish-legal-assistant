# Component Architecture Guide

## Component Hierarchy

```
app/page.tsx (Home)
├── Header
│   ├── Logo + Title
│   └── "New Chat" Button (conditional)
├── CategoryFilter (conditional - shown during chat)
│   └── Category Pills
├── Main Content
│   ├── WelcomeScreen (initial state)
│   │   ├── Hero Section
│   │   ├── Sample Questions Grid
│   │   └── Disclaimer
│   └── ChatInterface (active chat state)
│       ├── Messages Container
│       │   └── MessageBubble (repeated)
│       │       ├── Avatar
│       │       ├── Message Content (Markdown)
│       │       ├── Timestamp
│       │       └── SourceCitations (AI messages only)
│       ├── LoadingIndicator (conditional)
│       ├── Error Banner (conditional)
│       └── Input Area
│           ├── Textarea
│           ├── Send Button
│           └── Helper Text
└── Footer
```

## Component Details

### 1. app/page.tsx
**Purpose:** Main orchestrator for the entire application

**State:**
- `hasStartedChat`: Boolean to toggle between welcome and chat views
- `selectedCategory`: Currently selected category filter
- `initialQuestion`: Question clicked from welcome screen

**Key Functions:**
- `handleQuestionClick()`: Transitions from welcome to chat
- `handleCategoryChange()`: Updates category filter
- `handleNewChat()`: Resets to welcome screen

---

### 2. WelcomeScreen
**Location:** `components/WelcomeScreen.tsx`

**Props:**
- `onQuestionClick: (question: string) => void`

**Features:**
- Polish flag logo with message icon
- Animated hero section
- 4 clickable sample question cards
- Legal disclaimer text

**Styling:**
- Centered layout
- Fade-in animation
- Hover effects on cards
- Responsive grid (1 column mobile, 2 columns desktop)

---

### 3. CategoryFilter
**Location:** `components/CategoryFilter.tsx`

**Props:**
- `selectedCategory: Category`
- `onSelectCategory: (category: Category) => void`

**Features:**
- 7 category pills (All, Immigration, Employment, Healthcare, Banking, Traffic, Police)
- Visual indication of selected category (ring border)
- Color-coded by category
- Horizontal scrollable on mobile

**Styling:**
- Pill-shaped buttons
- Color-coded backgrounds
- Scale animation on hover
- Ring indicator for active category

---

### 4. ChatInterface
**Location:** `components/ChatInterface.tsx`

**Props:**
- `initialCategory?: Category`

**State:**
- `messages`: Array of ChatMessage objects
- `inputValue`: Current textarea value
- `isLoading`: Loading state during API calls
- `error`: Error message if API fails
- `selectedCategory`: Current category context

**Key Functions:**
- `handleSendMessage()`: Sends message to API and updates state
- `handleKeyDown()`: Handles Enter key to send
- `handleRetry()`: Resends last message after error
- `scrollToBottom()`: Auto-scrolls to latest message

**Features:**
- Auto-resizing textarea (expands with content)
- Conversation history passed to API (last 10 messages)
- Error handling with retry button
- Loading indicator while waiting for response
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)

---

### 5. MessageBubble
**Location:** `components/MessageBubble.tsx`

**Props:**
- `message: ChatMessage`

**Features:**
- Differentiates user vs AI messages
- User: Blue background, right-aligned, user icon
- AI: Gray background, left-aligned, bot icon
- Markdown rendering for AI responses
- Timestamp in human-readable format
- Source citations for AI messages

**Styling:**
- Rounded bubbles (rounded-2xl)
- Slide-up animation on appearance
- Max width 85% mobile, 75% desktop
- Prose styling for markdown content

---

### 6. SourceCitations
**Location:** `components/SourceCitations.tsx`

**Props:**
- `sources: Source[]`

**Features:**
- Collapsible list (default: expanded)
- Numbered citations
- Shows organization, title, verification date
- Clickable links with external link icon
- Hover effects

**Styling:**
- Blue background cards
- Smooth expand/collapse animation
- Truncated text with line-clamp
- External link icon on hover

---

### 7. LoadingIndicator
**Location:** `components/LoadingIndicator.tsx`

**Features:**
- Three bouncing dots animation
- "Thinking..." text
- Gray color scheme

**Styling:**
- Staggered animation delays
- Small, subtle design
- Matches AI message alignment

---

## Data Flow

### Sending a Message

1. User types in textarea (ChatInterface)
2. User clicks send or presses Enter
3. ChatInterface adds user message to state
4. ChatInterface calls `chatAPI.sendMessage()`
5. API client sends POST to `/api/chat`
6. Backend processes with GPT-4 + RAG
7. Response received with answer + sources
8. ChatInterface adds assistant message to state
9. MessageBubble renders with SourceCitations

### Error Handling

1. API call fails (network/server error)
2. ChatInterface catches error
3. Error banner appears with message
4. "Retry" button offered
5. User clicks retry
6. Last user message resent

### Category Filtering

1. User selects category (CategoryFilter)
2. `onSelectCategory()` called in page.tsx
3. State updated
4. Visual indication on pill
5. Next message includes category in API request

---

## Styling System

### Tailwind Configuration

**Custom Colors:**
- `primary`: Blue scale (50-900)
- `accent.red`: Polish flag red
- `polish.white/red`: Exact flag colors

**Custom Animations:**
- `fade-in`: 0.3s opacity transition
- `slide-up`: 0.3s upward movement
- Bounce (default Tailwind) for loading dots

**Responsive Breakpoints:**
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

---

## Type System

### Core Types (types/legal-types.ts)

```typescript
enum Category {
  ALL, IMMIGRATION, EMPLOYMENT, HEALTHCARE,
  BANKING, TRAFFIC, POLICE
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
  category?: Category;
}

interface Source {
  organization: string;
  title: string;
  url: string;
  verified_date: string;
  relevance_score?: number;
}

interface ChatRequest {
  message: string;
  category?: Category;
  conversation_history?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

interface ChatResponse {
  response: string;
  sources: Source[];
  category?: Category;
  confidence?: number;
}
```

---

## API Integration

### Endpoint: POST /api/chat

**Request:**
```json
{
  "message": "How do I get a residence permit?",
  "category": "immigration",
  "conversation_history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

**Response:**
```json
{
  "response": "To get a residence permit in Poland...",
  "sources": [
    {
      "organization": "Office for Foreigners",
      "title": "Residence Permit Application Guide",
      "url": "https://...",
      "verified_date": "2025-11-11"
    }
  ],
  "category": "immigration",
  "confidence": 0.95
}
```

**Error Handling:**
- Network errors: "No response from server..."
- Server errors: Shows `detail` from API
- Timeout: 60 second limit
- Retry mechanism available

---

## State Management

Currently using React useState (no Redux/Zustand):

**app/page.tsx:**
- Chat vs Welcome screen state
- Selected category
- Initial question

**ChatInterface:**
- Messages array
- Input value
- Loading state
- Error state

**Future Considerations:**
- Add Context API for theme (dark mode)
- Consider localStorage for chat persistence
- May need state management library for advanced features

---

## Performance Optimizations

1. **Auto-scrolling:** Only triggers on message changes
2. **Textarea resize:** Efficient height calculation
3. **React keys:** Proper keys on message list
4. **Lazy rendering:** Markdown only renders for AI messages
5. **Debouncing:** Could add for textarea (future)

---

## Accessibility

- Semantic HTML (header, main, footer)
- ARIA labels on buttons
- Keyboard navigation (Enter, Shift+Enter)
- Focus indicators
- Color contrast WCAG AA
- Screen reader friendly text

---

## Testing Checklist

### Visual Testing
- [ ] Welcome screen loads correctly
- [ ] Sample questions are clickable
- [ ] Chat interface appears after question click
- [ ] Category pills display and are clickable
- [ ] Messages appear with correct styling
- [ ] Loading indicator shows during API call
- [ ] Error banner appears on failure
- [ ] Source citations are collapsible
- [ ] Responsive on mobile (320px+)
- [ ] Responsive on tablet (768px+)
- [ ] Responsive on desktop (1024px+)

### Functional Testing
- [ ] Sending message works
- [ ] Enter key sends message
- [ ] Shift+Enter creates new line
- [ ] Category filter updates messages
- [ ] New Chat button resets interface
- [ ] Retry button resends message
- [ ] Source links open in new tab
- [ ] Auto-scroll to bottom works
- [ ] Textarea auto-resizes
- [ ] Messages display markdown correctly

### Integration Testing
- [ ] API connection successful
- [ ] Conversation history sent correctly
- [ ] Sources display from API response
- [ ] Category included in request
- [ ] Error messages from API shown
- [ ] Network errors handled gracefully

---

## Future Enhancements

### Priority 1
- Chat history persistence (localStorage)
- Copy message to clipboard
- Dark mode toggle

### Priority 2
- Share conversation link
- Download conversation as PDF
- Voice input support

### Priority 3
- Polish language UI
- Multi-file upload
- Real-time typing indicators
- Read receipts

---

## Troubleshooting

### Messages not appearing
- Check browser console for errors
- Verify API response format
- Check message array in React DevTools

### Styles not applying
- Restart dev server
- Clear .next cache
- Hard refresh browser

### API errors
- Verify backend is running
- Check CORS configuration
- Test endpoint with curl
- Review network tab in DevTools

### TypeScript errors
- Run `npm run lint`
- Check imports
- Verify type definitions

---

## Code Standards

### File Naming
- Components: PascalCase (MessageBubble.tsx)
- Utilities: camelCase (api-client.ts)
- Types: kebab-case (legal-types.ts)

### Component Structure
1. Imports
2. Interface/Props definition
3. Component function
4. Helper functions
5. Export

### Styling
- Use Tailwind utilities
- Avoid custom CSS
- Group related classes
- Mobile-first responsive

### TypeScript
- Strict mode enabled
- No implicit any
- Define interfaces for props
- Use enums for fixed values
