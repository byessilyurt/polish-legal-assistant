# Development Guide

## Adding New Features

### Adding a New Component

1. Create file in `components/` directory:
   ```bash
   touch components/NewComponent.tsx
   ```

2. Use this template:
   ```typescript
   'use client';

   interface NewComponentProps {
     // Define props here
   }

   export default function NewComponent({ }: NewComponentProps) {
     return (
       <div>
         {/* Component JSX */}
       </div>
     );
   }
   ```

3. Import and use in parent component:
   ```typescript
   import NewComponent from '@/components/NewComponent';
   ```

---

### Adding a New Category

1. Update `types/legal-types.ts`:
   ```typescript
   export enum Category {
     // ... existing categories
     NEW_CATEGORY = 'new_category',
   }

   export const CATEGORY_LABELS: Record<Category, string> = {
     // ... existing labels
     [Category.NEW_CATEGORY]: 'New Category',
   };

   export const CATEGORY_COLORS: Record<Category, string> = {
     // ... existing colors
     [Category.NEW_CATEGORY]: 'bg-orange-100 text-orange-700 hover:bg-orange-200',
   };
   ```

2. Category will automatically appear in filter

---

### Adding a New API Endpoint

1. Update `lib/api-client.ts`:
   ```typescript
   export const chatAPI = {
     // ... existing methods

     newEndpoint: async (params: ParamsType): Promise<ResponseType> => {
       try {
         const response = await apiClient.post<ResponseType>('/api/new-endpoint', params);
         return response.data;
       } catch (error) {
         // Handle error
       }
     },
   };
   ```

2. Define types in `types/legal-types.ts`

---

### Adding Dark Mode

1. Install next-themes:
   ```bash
   npm install next-themes
   ```

2. Create theme provider in `app/providers.tsx`:
   ```typescript
   'use client';
   import { ThemeProvider } from 'next-themes';

   export function Providers({ children }: { children: React.ReactNode }) {
     return (
       <ThemeProvider attribute="class" defaultTheme="light">
         {children}
       </ThemeProvider>
     );
   }
   ```

3. Update `app/layout.tsx`:
   ```typescript
   import { Providers } from './providers';

   export default function RootLayout({ children }) {
     return (
       <html lang="en" suppressHydrationWarning>
         <body>
           <Providers>{children}</Providers>
         </body>
       </html>
     );
   }
   ```

4. Add dark mode classes to tailwind.config.js:
   ```javascript
   module.exports = {
     darkMode: 'class',
     // ... rest of config
   }
   ```

5. Create theme toggle component

---

### Adding Chat History Persistence

1. Create localStorage utility in `lib/storage.ts`:
   ```typescript
   const STORAGE_KEY = 'polish-legal-chat-history';

   export const chatStorage = {
     save: (messages: ChatMessage[]) => {
       localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
     },

     load: (): ChatMessage[] => {
       const data = localStorage.getItem(STORAGE_KEY);
       return data ? JSON.parse(data) : [];
     },

     clear: () => {
       localStorage.removeItem(STORAGE_KEY);
     },
   };
   ```

2. Update ChatInterface:
   ```typescript
   useEffect(() => {
     // Load on mount
     const savedMessages = chatStorage.load();
     setMessages(savedMessages);
   }, []);

   useEffect(() => {
     // Save on changes
     chatStorage.save(messages);
   }, [messages]);
   ```

---

### Adding Copy to Clipboard

1. Create utility function:
   ```typescript
   const copyToClipboard = async (text: string) => {
     try {
       await navigator.clipboard.writeText(text);
       // Show success toast
     } catch (error) {
       // Show error toast
     }
   };
   ```

2. Add button to MessageBubble:
   ```typescript
   <button
     onClick={() => copyToClipboard(message.content)}
     className="..."
   >
     <Copy className="w-4 h-4" />
   </button>
   ```

---

### Adding Toast Notifications

1. Install react-hot-toast:
   ```bash
   npm install react-hot-toast
   ```

2. Add Toaster to layout:
   ```typescript
   import { Toaster } from 'react-hot-toast';

   export default function RootLayout({ children }) {
     return (
       <html lang="en">
         <body>
           {children}
           <Toaster position="top-right" />
         </body>
       </html>
     );
   }
   ```

3. Use in components:
   ```typescript
   import toast from 'react-hot-toast';

   toast.success('Message copied!');
   toast.error('Failed to send message');
   ```

---

## Debugging Tips

### React DevTools

1. Install React DevTools browser extension
2. Inspect component hierarchy
3. View props and state
4. Track re-renders

### Logging

Add strategic console logs:
```typescript
console.log('Messages updated:', messages);
console.log('API Response:', response);
console.error('Error occurred:', error);
```

Remove before committing to production.

### Network Debugging

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by XHR/Fetch
4. Inspect request/response

### TypeScript Errors

Run type checking:
```bash
npx tsc --noEmit
```

### Performance Profiling

1. React DevTools Profiler tab
2. Record interaction
3. Analyze render times
4. Optimize slow components

---

## Testing

### Manual Testing Checklist

Before committing:
- [ ] Test on Chrome
- [ ] Test on Firefox
- [ ] Test on Safari (Mac)
- [ ] Test on mobile (Chrome DevTools device mode)
- [ ] Test all user flows
- [ ] Test error scenarios
- [ ] Test edge cases (empty messages, long messages)

### Unit Testing (Future)

Install Jest and React Testing Library:
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

Example test:
```typescript
import { render, screen } from '@testing-library/react';
import MessageBubble from './MessageBubble';

test('renders user message', () => {
  const message = {
    id: '1',
    role: 'user',
    content: 'Test message',
    timestamp: new Date(),
  };

  render(<MessageBubble message={message} />);
  expect(screen.getByText('Test message')).toBeInTheDocument();
});
```

---

## Performance Optimization

### Code Splitting

Next.js automatically code splits by route. For component-level splitting:

```typescript
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingIndicator />,
});
```

### Image Optimization

Use Next.js Image component:
```typescript
import Image from 'next/image';

<Image
  src="/polish-flag.svg"
  alt="Polish flag"
  width={40}
  height={40}
/>
```

### Memoization

For expensive calculations:
```typescript
import { useMemo } from 'react';

const sortedMessages = useMemo(
  () => messages.sort((a, b) => a.timestamp - b.timestamp),
  [messages]
);
```

For preventing re-renders:
```typescript
import { memo } from 'react';

const MessageBubble = memo(({ message }) => {
  // Component code
});

export default MessageBubble;
```

---

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

### Self-Hosted

1. Build:
   ```bash
   npm run build
   ```

2. Start:
   ```bash
   npm start
   ```

3. Use PM2 for production:
   ```bash
   npm install -g pm2
   pm2 start npm --name "polish-legal-frontend" -- start
   ```

### Docker

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t polish-legal-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000 polish-legal-frontend
```

---

## Environment Variables

### Development (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

Note: All `NEXT_PUBLIC_*` variables are exposed to the browser.

---

## Git Workflow

### Branch Naming
- `feature/add-dark-mode`
- `fix/message-bubble-styling`
- `refactor/api-client`

### Commit Messages
- `feat: Add dark mode toggle`
- `fix: Correct message timestamp formatting`
- `refactor: Extract API client logic`
- `docs: Update README with deployment guide`

### Pull Requests
1. Create feature branch
2. Make changes
3. Test thoroughly
4. Push to GitHub
5. Create PR with description
6. Request review
7. Merge to main

---

## Code Style

### Prettier Configuration

Create `.prettierrc`:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

Install:
```bash
npm install --save-dev prettier
```

Format:
```bash
npx prettier --write .
```

### ESLint

Already configured via `eslint-config-next`. Run:
```bash
npm run lint
```

Fix auto-fixable issues:
```bash
npm run lint -- --fix
```

---

## Useful Commands

```bash
# Development
npm run dev              # Start dev server
npm run build           # Build for production
npm start               # Start production server
npm run lint            # Run ESLint

# Package Management
npm install <package>    # Add dependency
npm update              # Update dependencies
npm outdated            # Check outdated packages

# Cleaning
rm -rf .next            # Clear Next.js cache
rm -rf node_modules     # Remove dependencies
npm ci                  # Clean install

# TypeScript
npx tsc --noEmit        # Type check without building
```

---

## Resources

### Documentation
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs)

### Tools
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)
- [ES7+ React Snippets](https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets)

### Community
- [Next.js Discord](https://nextjs.org/discord)
- [Reactiflux Discord](https://www.reactiflux.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/next.js)

---

## FAQ

### Q: How do I add a new page?
A: Create a new file in the `app/` directory. For example, `app/about/page.tsx` creates `/about` route.

### Q: How do I make API calls server-side?
A: Use Server Components or Route Handlers. Create `app/api/route-name/route.ts`.

### Q: How do I handle authentication?
A: Consider NextAuth.js or implement custom JWT-based auth with cookies.

### Q: How do I optimize bundle size?
A: Use dynamic imports, tree-shaking, and analyze bundle with `@next/bundle-analyzer`.

### Q: How do I add SEO?
A: Update metadata in `app/layout.tsx` and individual pages.

---

## Troubleshooting Common Issues

### "Module not found" errors
```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript "Cannot find module" errors
```bash
# Restart TypeScript server in VS Code
# Cmd+Shift+P -> "TypeScript: Restart TS Server"
```

### Hydration errors
- Ensure server and client render the same content
- Don't use `Date.now()` or `Math.random()` in components
- Use `suppressHydrationWarning` on `<html>` tag

### Slow build times
- Check for circular dependencies
- Use `next build --profile` to analyze
- Consider upgrading Node.js version

---

## Best Practices

1. **Component Composition**: Break large components into smaller ones
2. **Type Safety**: Always define TypeScript types
3. **Error Boundaries**: Implement error boundaries for production
4. **Accessibility**: Test with screen readers
5. **Performance**: Monitor Core Web Vitals
6. **Security**: Sanitize user input, use HTTPS
7. **SEO**: Add proper meta tags and structured data
8. **Testing**: Write tests for critical paths
9. **Documentation**: Comment complex logic
10. **Version Control**: Commit frequently with clear messages

---

## Next Steps

Ready to extend the application? Here are some ideas:

1. **Add file upload** for document analysis
2. **Implement chat export** as PDF
3. **Create admin dashboard** for managing sources
4. **Add analytics** to track popular questions
5. **Build mobile app** with React Native (share components)
6. **Add real-time features** with WebSockets
7. **Implement A/B testing** for UI variations
8. **Create API documentation** with Swagger
9. **Add multi-language support** (i18n)
10. **Build Chrome extension** for quick access

Happy coding!
