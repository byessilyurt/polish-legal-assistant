# Quick Reference

## Project Overview
**Polish Legal Assistant** - Modern chat interface for Polish legal information
**Stack:** Next.js 14 + TypeScript + Tailwind CSS

---

## Essential Commands

```bash
# First time setup
npm install
cp .env.example .env.local

# Development
npm run dev          # http://localhost:3000

# Production
npm run build
npm start

# Quality checks
npm run lint
npx tsc --noEmit
```

---

## File Locations

| What | Where |
|------|-------|
| Main page | `app/page.tsx` |
| Root layout | `app/layout.tsx` |
| Global styles | `app/globals.css` |
| Chat UI | `components/ChatInterface.tsx` |
| API calls | `lib/api-client.ts` |
| Types | `types/legal-types.ts` |
| Config | `tailwind.config.js`, `tsconfig.json` |

---

## Key Components

```
WelcomeScreen      → Initial landing page
ChatInterface      → Main chat logic & state
MessageBubble      → Individual messages
SourceCitations    → Expandable source links
CategoryFilter     → Category selection pills
LoadingIndicator   → Typing animation
```

---

## Color Palette

```css
Primary Blue:  #1e40af
Light Blue:    #3b82f6
Accent Red:    #dc2626
Background:    #f9fafb
Text:          #1f2937
```

---

## API Endpoint

```
POST http://localhost:8000/api/chat

Request:
{
  "message": "string",
  "category": "immigration" | "employment" | ...,
  "conversation_history": [...]
}

Response:
{
  "response": "string",
  "sources": [...],
  "category": "string",
  "confidence": number
}
```

---

## Common Tasks

### Add a new category
1. Update `Category` enum in `types/legal-types.ts`
2. Add label to `CATEGORY_LABELS`
3. Add color to `CATEGORY_COLORS`

### Change API URL
Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://new-url:8000
```

### Add a new component
```typescript
// components/NewComponent.tsx
'use client';

interface Props {
  // props
}

export default function NewComponent({}: Props) {
  return <div>...</div>;
}
```

### Update styling
Use Tailwind classes:
```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Content
</div>
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send message |
| Shift+Enter | New line |

---

## Project Structure

```
frontend/
├── app/              # Next.js pages
├── components/       # React components
├── lib/             # Utilities (API client)
├── types/           # TypeScript types
├── public/          # Static assets
└── docs/            # Documentation
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| Styles not loading | Restart dev server, clear cache |
| API errors | Check backend is running |
| TypeScript errors | `rm -rf .next && npm run build` |
| Module not found | `rm -rf node_modules && npm install` |

---

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Testing Checklist

- [ ] Welcome screen loads
- [ ] Sample questions work
- [ ] Chat interface appears
- [ ] Messages send/receive
- [ ] Categories filter properly
- [ ] Sources display correctly
- [ ] Error handling works
- [ ] Responsive on mobile
- [ ] Links open in new tab

---

## Documentation

- `README.md` - Main documentation
- `SETUP_INSTRUCTIONS.md` - First-time setup
- `COMPONENT_GUIDE.md` - Component details
- `DEVELOPMENT_GUIDE.md` - Advanced development
- `QUICK_REFERENCE.md` - This file

---

## Dependencies

**Core:**
- next@14.1.0
- react@18.2.0
- typescript@5.3.3

**Styling:**
- tailwindcss@3.4.1
- autoprefixer@10.4.17
- postcss@8.4.33

**Utilities:**
- axios@1.6.5
- react-markdown@9.0.1
- lucide-react@0.312.0
- date-fns@3.2.0

---

## Support Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind Docs](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React Docs](https://react.dev)

---

## Contact

For issues or questions, contact the development team.

---

**Last Updated:** 2025-11-11
**Version:** 0.1.0
**License:** Proprietary
