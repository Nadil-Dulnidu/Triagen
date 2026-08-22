import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { QueryProvider } from "@/lib/providers/query-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Triagen — Autonomous AI-Powered PR Reviews & Triage",
  description:
    "Automate pull request triage and first-pass code reviews with AI. Triagen orchestrates multi-agent pipelines with long-term vector memory to detect security flaws, enforce standards, and post inline fixes.",
  keywords: ["Triagen", "code review", "AI", "GitHub", "pull request", "PR triage", "developer tools", "DevSecOps"],
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider appearance={dark}>
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

