import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Polish Legal Assistant | Immigration, Employment & Healthcare Help',
  description: 'Get help with Polish legal matters, immigration, employment, healthcare, and daily life in Poland. Powered by OpenAI GPT-4 with verified government sources.',
  keywords: 'Poland, legal, immigration, visa, employment, healthcare, NFZ, residence permit, work permit',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
