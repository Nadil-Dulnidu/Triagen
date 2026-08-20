import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/lib/providers/query-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PullSense — AI-Powered PR Reviews",
  description:
    "Automate your first-pass code reviews with AI. PullSense uses multi-agent workflows to check security, style, test coverage, and team conventions.",
  keywords: ["code review", "AI", "GitHub", "pull request", "developer tools"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en" className={`${inter.variable} dark`} suppressHydrationWarning>
        <body className="min-h-screen bg-background font-sans antialiased">
          <QueryProvider>
            <TooltipProvider>{children}</TooltipProvider>
          </QueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
