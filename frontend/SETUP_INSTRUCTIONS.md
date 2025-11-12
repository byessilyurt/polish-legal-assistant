# Setup Instructions

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` if your backend runs on a different port:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Verify Setup

The application should load with:
- Welcome screen showing the Polish flag logo
- "Polish Legal Assistant" title
- Four sample question cards
- Clean, modern interface

## Test the Chat

1. Click on any sample question or type your own
2. The chat interface should appear
3. Category filter pills should show at the top
4. Messages should display with proper formatting

## Backend Connection

The frontend expects the backend API at `http://localhost:8000` by default.

**Test backend connection:**
```bash
curl http://localhost:8000/health
```

If the backend is not running, you'll see connection errors in the chat.

## Common Issues

### Port 3000 already in use
```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or run on a different port
npm run dev -- -p 3001
```

### TypeScript errors
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### Tailwind styles not loading
```bash
# Restart dev server
# Clear browser cache
# Hard refresh (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
```

## Production Build

```bash
# Build for production
npm run build

# Test production build locally
npm start
```

## File Structure Check

Verify all files are created:

```
frontend/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── CategoryFilter.tsx
│   ├── ChatInterface.tsx
│   ├── LoadingIndicator.tsx
│   ├── MessageBubble.tsx
│   ├── SourceCitations.tsx
│   └── WelcomeScreen.tsx
├── lib/
│   └── api-client.ts
├── types/
│   └── legal-types.ts
├── public/
│   └── polish-flag.svg
├── .env.local
├── .env.example
├── .gitignore
├── next.config.js
├── package.json
├── postcss.config.js
├── README.md
├── tailwind.config.js
└── tsconfig.json
```

## Development Workflow

1. Make changes to components
2. Changes auto-reload in browser
3. Check browser console for errors
4. Test on mobile viewport (Chrome DevTools)

## Next Steps

- Ensure backend is running at http://localhost:8000
- Test all category filters
- Try sample questions
- Test markdown formatting in responses
- Verify source citations appear and are clickable
- Test responsive design on mobile

## Support

If you encounter issues:
1. Check browser console for errors
2. Check terminal for build errors
3. Verify backend API is accessible
4. Review the main README.md for detailed documentation
