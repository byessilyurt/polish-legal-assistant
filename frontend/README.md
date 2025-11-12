# Polish Legal Assistant - Frontend

A modern, Grok-style chat interface for the Polish Legal Assistant. Built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Modern Chat Interface**: Grok-inspired design with smooth animations and clean aesthetics
- **Category Filtering**: Filter conversations by Immigration, Employment, Healthcare, Banking, Traffic, and Police
- **Source Citations**: Every AI response includes clickable citations to verified Polish government sources
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop devices
- **Real-time Messaging**: Instant responses with loading indicators and typing animations
- **Error Handling**: Graceful error recovery with retry functionality
- **Markdown Support**: Rich text formatting in AI responses
- **Welcome Screen**: Guided onboarding with sample questions to get started

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Lucide React (icons)
- **Markdown**: React Markdown
- **HTTP Client**: Axios
- **Date Formatting**: date-fns

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx           # Main chat page
│   ├── layout.tsx         # Root layout with metadata
│   └── globals.css        # Global styles and Tailwind
├── components/
│   ├── ChatInterface.tsx      # Main chat component with message handling
│   ├── MessageBubble.tsx      # Individual message display with markdown
│   ├── SourceCitations.tsx    # Collapsible source citations
│   ├── CategoryFilter.tsx     # Category selection pills
│   ├── WelcomeScreen.tsx      # Initial welcome screen
│   └── LoadingIndicator.tsx   # Typing animation
├── lib/
│   └── api-client.ts      # Backend API integration with error handling
├── types/
│   └── legal-types.ts     # TypeScript interfaces and enums
├── public/
│   └── (static assets)
├── tailwind.config.js     # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
├── next.config.js         # Next.js configuration
└── package.json           # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running (default: http://localhost:8000)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create environment file:

```bash
cp .env.example .env.local
```

3. Update `.env.local` with your backend API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Component Overview

### ChatInterface

The main chat component that manages:
- Message state and history
- API communication
- Loading states
- Error handling
- Auto-scrolling to latest messages

### MessageBubble

Displays individual messages with:
- User messages (blue, right-aligned)
- AI messages (gray, left-aligned with avatar)
- Markdown rendering for formatted responses
- Timestamps
- Source citations (for AI messages)

### SourceCitations

Shows verified sources for AI responses:
- Collapsible list of sources
- Organization name and document title
- Verification date
- Clickable links to original sources

### CategoryFilter

Filter conversations by category:
- Pill-style buttons
- Visual indication of selected category
- All Categories, Immigration, Employment, Healthcare, Banking, Traffic, Police

### WelcomeScreen

Initial landing page with:
- Branding and introduction
- Sample questions as clickable cards
- Category indicators
- Legal disclaimer

## API Integration

The frontend communicates with the backend via REST API:

### Endpoint: POST /api/chat

**Request:**
```typescript
{
  message: string;
  category?: 'immigration' | 'employment' | 'healthcare' | 'banking' | 'traffic' | 'police';
  conversation_history?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}
```

**Response:**
```typescript
{
  response: string;
  sources: Array<{
    organization: string;
    title: string;
    url: string;
    verified_date: string;
    relevance_score?: number;
  }>;
  category?: string;
  confidence?: number;
}
```

## Styling Guidelines

The design follows a professional, clean aesthetic inspired by Grok:

### Color Palette

- **Primary Blue**: `#1e40af` - Main brand color, buttons, links
- **Secondary Blue**: `#3b82f6` - Hover states, accents
- **Accent Red**: `#dc2626` - Important notices, Polish flag accent
- **Background**: `#ffffff` (white) and `#f9fafb` (light gray)
- **Text**: `#1f2937` (dark gray)

### Typography

- Font: Inter (Google Fonts)
- Heading sizes: 4xl-5xl for hero, lg-xl for sections
- Body text: sm-base
- Micro text (timestamps, disclaimers): xs

### Spacing

- Generous whitespace between messages (mb-6)
- Consistent padding: px-4 py-3 for messages
- Rounded corners: rounded-2xl for messages, rounded-lg for buttons

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support (Enter to send, Shift+Enter for new line)
- Color contrast meets WCAG AA standards
- Focus indicators on all interactive elements

## Performance Optimizations

- Client-side rendering for interactive components
- Auto-resizing textarea
- Efficient re-renders with proper React keys
- Lazy loading for markdown components
- Optimized images and assets

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API Connection Issues

If you see "No response from server" errors:

1. Verify the backend is running: `curl http://localhost:8000/health`
2. Check the `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure CORS is properly configured on the backend

### Build Errors

If you encounter TypeScript errors:

```bash
npm run lint
```

Clear Next.js cache:

```bash
rm -rf .next
npm run build
```

### Styling Issues

If Tailwind styles aren't applying:

1. Restart the dev server
2. Clear browser cache
3. Verify `tailwind.config.js` content paths

## Future Enhancements

Potential features to add:

- [ ] Dark mode toggle
- [ ] Copy response to clipboard
- [ ] Share conversation link
- [ ] Download conversation as PDF
- [ ] Polish language UI option
- [ ] Voice input support
- [ ] Multi-file upload for document analysis
- [ ] Chat history persistence (localStorage/backend)

## Contributing

When adding new features:

1. Follow the existing component structure
2. Maintain TypeScript strict mode
3. Use Tailwind utility classes (avoid custom CSS)
4. Test on mobile and desktop
5. Update this README with new features

## License

Proprietary - Polish Legal Assistant Project

## Support

For issues or questions, contact the development team.
