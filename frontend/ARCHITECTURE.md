# Architecture Overview

## Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER (Client)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      app/page.tsx (Home)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  State:                                                   │  │
│  │  - hasStartedChat: boolean                               │  │
│  │  - selectedCategory: Category                            │  │
│  │  - initialQuestion: string | null                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                    ┌─────────┴─────────┐                       │
│                    ▼                   ▼                        │
│         ┌──────────────────┐  ┌──────────────────┐            │
│         │  WelcomeScreen   │  │  ChatInterface   │            │
│         │  (Initial View)  │  │  (Active Chat)   │            │
│         └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    components/ChatInterface.tsx                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  State:                                                   │  │
│  │  - messages: ChatMessage[]                               │  │
│  │  - inputValue: string                                    │  │
│  │  - isLoading: boolean                                    │  │
│  │  - error: string | null                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                    ┌─────────┴─────────┐                       │
│                    ▼                   ▼                        │
│         ┌──────────────────┐  ┌──────────────────┐            │
│         │  MessageBubble   │  │ LoadingIndicator │            │
│         │  (User/AI msg)   │  │  (Typing dots)   │            │
│         └──────────────────┘  └──────────────────┘            │
│                 │                                               │
│                 ▼                                               │
│         ┌──────────────────┐                                   │
│         │ SourceCitations  │                                   │
│         │ (AI sources)     │                                   │
│         └──────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      lib/api-client.ts                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  chatAPI.sendMessage()                                    │  │
│  │  - Request validation                                     │  │
│  │  - Error handling                                         │  │
│  │  - Timeout management                                     │  │
│  │  - Response parsing                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                        │
│                   http://localhost:8000/api/chat                │
│                                                                 │
│  Flow:                                                          │
│  1. Receive user message                                       │
│  2. Retrieve relevant documents (RAG)                          │
│  3. Generate response with GPT-4                               │
│  4. Return response + sources                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Sending a Message

```
User types message
       │
       ▼
[ChatInterface]
   ├─> Add user message to state
   ├─> Set isLoading = true
   └─> Call chatAPI.sendMessage()
              │
              ▼
       [api-client.ts]
          ├─> Prepare request (message, category, history)
          ├─> POST to /api/chat
          └─> Wait for response
                    │
                    ▼ (Backend processing...)
                    │
                    ▼
              [api-client.ts]
          ├─> Receive response
          ├─> Parse JSON
          └─> Return { response, sources }
              │
              ▼
       [ChatInterface]
   ├─> Add assistant message to state
   ├─> Set isLoading = false
   └─> Auto-scroll to bottom
              │
              ▼
       [MessageBubble]
   ├─> Render AI message
   ├─> Parse markdown
   └─> Display sources
```

---

## Component Hierarchy

```
app/page.tsx (Root)
│
├─── Header
│    ├─── Logo (🇵🇱)
│    ├─── Title
│    └─── New Chat Button
│
├─── CategoryFilter (conditional)
│    └─── Category Pills × 7
│
├─── Main Content
│    │
│    ├─── WelcomeScreen (initial)
│    │    ├─── Hero Section
│    │    │    ├─── Logo + Icon
│    │    │    ├─── Title
│    │    │    └─── Subtitle
│    │    │
│    │    ├─── Sample Questions Grid
│    │    │    ├─── Question Card
│    │    │    ├─── Question Card
│    │    │    ├─── Question Card
│    │    │    └─── Question Card
│    │    │
│    │    └─── Disclaimer
│    │
│    └─── ChatInterface (active)
│         │
│         ├─── Messages Container
│         │    └─── MessageBubble (repeated)
│         │         ├─── Avatar
│         │         ├─── Content
│         │         │    └─── ReactMarkdown (AI only)
│         │         ├─── Timestamp
│         │         └─── SourceCitations (AI only)
│         │              └─── Source Card × N
│         │
│         ├─── LoadingIndicator (conditional)
│         │
│         ├─── Error Banner (conditional)
│         │    ├─── Error Message
│         │    └─── Retry Button
│         │
│         └─── Input Area
│              ├─── Textarea
│              ├─── Send Button
│              └─── Helper Text
│
└─── Footer
     └─── Disclaimer Text
```

---

## State Management

### Global State (app/page.tsx)
```typescript
hasStartedChat: boolean     // Toggle welcome/chat view
selectedCategory: Category  // Current category filter
initialQuestion: string     // Question from welcome screen
```

### Local State (ChatInterface)
```typescript
messages: ChatMessage[]     // Conversation history
inputValue: string          // Current textarea content
isLoading: boolean         // API call in progress
error: string | null       // Error message
```

---

## Type System Architecture

```
types/legal-types.ts
│
├─── Enums
│    └─── Category (ALL, IMMIGRATION, EMPLOYMENT, ...)
│
├─── Interfaces
│    ├─── ChatMessage
│    │    ├─── id: string
│    │    ├─── role: 'user' | 'assistant'
│    │    ├─── content: string
│    │    ├─── sources?: Source[]
│    │    ├─── timestamp: Date
│    │    └─── category?: Category
│    │
│    ├─── Source
│    │    ├─── organization: string
│    │    ├─── title: string
│    │    ├─── url: string
│    │    ├─── verified_date: string
│    │    └─── relevance_score?: number
│    │
│    ├─── ChatRequest
│    │    ├─── message: string
│    │    ├─── category?: Category
│    │    └─── conversation_history?: Array<...>
│    │
│    └─── ChatResponse
│         ├─── response: string
│         ├─── sources: Source[]
│         ├─── category?: Category
│         └─── confidence?: number
│
└─── Mappings
     ├─── CATEGORY_LABELS: Record<Category, string>
     └─── CATEGORY_COLORS: Record<Category, string>
```

---

## Styling Architecture

```
Tailwind CSS Configuration
│
├─── Colors
│    ├─── primary (blue scale 50-900)
│    ├─── accent.red
│    └─── polish.white/red
│
├─── Animations
│    ├─── fade-in (0.3s)
│    ├─── slide-up (0.3s)
│    └─── bounce (default)
│
└─── Responsive Breakpoints
     ├─── sm: 640px
     ├─── md: 768px
     ├─── lg: 1024px
     └─── xl: 1280px

Global Styles (app/globals.css)
│
├─── Base Styles
│    ├─── body: bg-gray-50 text-gray-900
│    └─── borders: gray-200
│
└─── Custom Components
     └─── scrollbar-thin
```

---

## API Architecture

```
Frontend                    Backend
(Next.js)                   (FastAPI)
    │                           │
    │  POST /api/chat           │
    ├──────────────────────────>│
    │                           │
    │  {                        │ 1. Parse request
    │    message,               │ 2. Validate inputs
    │    category,              │ 3. Search documents (Pinecone)
    │    history                │ 4. Build context
    │  }                        │ 5. Call OpenAI GPT-4
    │                           │ 6. Generate response
    │                           │ 7. Extract sources
    │                           │
    │<─────────────────────────-│
    │  {                        │
    │    response,              │
    │    sources: [...]         │
    │  }                        │
    │                           │
```

### Error Handling Flow

```
API Call Failed
     │
     ▼
Is it AxiosError?
     │
     ├─── YES ──> Has response?
     │            │
     │            ├─── YES ──> Show server error message
     │            │
     │            └─── NO ──> Show "No response from server"
     │
     └─── NO ──> Show "Unexpected error"
          │
          ▼
Display error banner
     │
     ▼
Show retry button
     │
     ▼
User clicks retry
     │
     ▼
Resend last user message
```

---

## Rendering Strategy

### Server-Side Rendering (SSR)
- `app/layout.tsx` - Root layout with metadata
- Metadata tags rendered on server
- Initial HTML sent to browser

### Client-Side Rendering (CSR)
- All components marked with `'use client'`
- React hydration on mount
- Dynamic interactions (typing, clicking, API calls)

### Why CSR?
- Real-time chat interactions
- WebSocket potential (future)
- Complex state management
- API calls from browser

---

## Build Process

```
npm run build
     │
     ▼
Next.js Compiler
     │
     ├─── TypeScript → JavaScript
     ├─── Tailwind CSS → Optimized CSS
     ├─── Code splitting by route
     ├─── Image optimization
     └─── Bundle minification
           │
           ▼
      .next/ directory
           │
           ├─── server/ (Node.js server)
           ├─── static/ (JS, CSS, assets)
           └─── standalone/ (production files)
                 │
                 ▼
           npm start (Production)
```

---

## Security Architecture

### Frontend Security
```
User Input Validation
     │
     ├─── Trim whitespace
     ├─── Check length limits
     └─── No script injection (React escapes by default)

API Communication
     │
     ├─── HTTPS only in production
     ├─── Content-Type: application/json
     └─── CORS headers from backend

Environment Variables
     │
     ├─── NEXT_PUBLIC_* exposed to browser (safe)
     └─── No secrets in frontend code
```

### Backend Responsibilities (not in this codebase)
- Authentication
- Rate limiting
- Input sanitization
- SQL injection prevention
- API key management

---

## Performance Optimizations

```
Component Level
     │
     ├─── React.memo for MessageBubble (future)
     ├─── useMemo for expensive calculations
     └─── useCallback for event handlers

Build Level
     │
     ├─── Code splitting (automatic by Next.js)
     ├─── Tree shaking unused code
     ├─── Minification
     └─── Image optimization

Runtime Level
     │
     ├─── Auto-scroll only on message changes
     ├─── Textarea auto-resize (efficient)
     └─── Proper React keys prevent re-renders
```

---

## Deployment Architecture

```
Development
     │
     └─── npm run dev
          │
          └─── localhost:3000 (hot reload)

Production (Vercel)
     │
     ├─── Git push to GitHub
     ├─── Automatic build trigger
     ├─── Edge network deployment
     └─── https://your-app.vercel.app

Production (Self-Hosted)
     │
     ├─── npm run build
     ├─── npm start (or PM2)
     └─── Nginx reverse proxy
          │
          └─── SSL certificate (Let's Encrypt)
               │
               └─── https://yourdomain.com

Production (Docker)
     │
     ├─── docker build
     ├─── docker run
     └─── Container orchestration (K8s, ECS)
```

---

## Scalability Considerations

### Current Architecture (MVP)
- Single Next.js instance
- Direct API calls to backend
- No caching
- No CDN
- Suitable for: < 1000 concurrent users

### Future Scaling
```
Load Balancer
     │
     ├─── Next.js Instance 1
     ├─── Next.js Instance 2
     └─── Next.js Instance N
          │
          ├─── Redis Cache (API responses)
          └─── CDN (Static assets)
               │
               └─── Backend API Cluster
```

---

## Testing Architecture (Future)

```
Unit Tests
     │
     ├─── Component rendering
     ├─── Utility functions
     └─── Type checking

Integration Tests
     │
     ├─── User flows
     ├─── API integration
     └─── State management

E2E Tests
     │
     ├─── Playwright/Cypress
     ├─── Full user journeys
     └─── Cross-browser testing
```

---

## Monitoring & Analytics (Future)

```
Error Tracking
     │
     └─── Sentry, Rollbar

Performance Monitoring
     │
     └─── Vercel Analytics, Lighthouse

User Analytics
     │
     └─── PostHog, Mixpanel

Logging
     │
     └─── CloudWatch, Datadog
```

---

## Maintenance Plan

### Daily
- Monitor error logs
- Check API response times

### Weekly
- Review dependency updates
- Check security advisories

### Monthly
- Update dependencies
- Review performance metrics
- Analyze user feedback

### Quarterly
- Major feature releases
- Architecture review
- Security audit

---

## Key Design Decisions

### Why Next.js?
- Built-in routing
- Excellent TypeScript support
- Great developer experience
- Easy deployment (Vercel)
- Active ecosystem

### Why Tailwind CSS?
- Rapid prototyping
- Consistent design system
- Small bundle size (purged)
- No naming conflicts
- Great with TypeScript

### Why TypeScript?
- Type safety
- Better IDE support
- Fewer runtime errors
- Self-documenting code
- Refactoring confidence

### Why Axios over Fetch?
- Better error handling
- Request/response interceptors
- Timeout support
- Progress tracking (future file uploads)
- Familiar API

---

## Future Architecture Enhancements

1. **State Management**
   - Add Context API for theme
   - Consider Zustand for complex state

2. **Real-time Updates**
   - WebSocket connection
   - Server-sent events
   - Live typing indicators

3. **Offline Support**
   - Service workers
   - IndexedDB caching
   - Progressive Web App (PWA)

4. **Advanced Features**
   - Voice input (Web Speech API)
   - File uploads (document analysis)
   - Multi-language support (i18n)
   - A/B testing framework

5. **Developer Experience**
   - Storybook for component library
   - Visual regression testing
   - Automated code reviews
   - CI/CD pipeline

---

**Architecture Version:** 1.0
**Last Updated:** 2025-11-11
**Author:** Polish Legal Assistant Development Team
