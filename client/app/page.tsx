"use client";

import Link from "next/link";
import { useAuth, UserButton } from "@clerk/nextjs";
import {
  GitPullRequestIcon,
  ShieldCheckIcon,
  CodeIcon,
  TestTubeIcon,
  BrainIcon,
  ZapIcon,
  ArrowRightIcon,
  LayoutDashboardIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  const { isSignedIn, isLoaded } = useAuth();

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Background gradient effects */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-violet-600/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 lg:px-12 border-b border-border/40 backdrop-blur-md">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600 shadow-md shadow-violet-600/30">
            <GitPullRequestIcon className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
            PullSense
          </span>
        </Link>

        <div className="flex items-center gap-4">
          {isLoaded && isSignedIn ? (
            <>
              <Link href="/dashboard">
                <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-white gap-2 shadow-sm">
                  <LayoutDashboardIcon className="h-4 w-4" />
                  Go to Dashboard
                  <ArrowRightIcon className="h-3.5 w-3.5" />
                </Button>
              </Link>
              <UserButton />
            </>
          ) : (
            <>
              <Link
                href="/sign-in"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-violet-700 shadow-sm"
              >
                Get Started
                <ArrowRightIcon className="h-4 w-4" />
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-5xl px-6 pt-20 pb-16 text-center lg:pt-28">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-950/20 px-4 py-1.5 text-sm text-violet-300 backdrop-blur-sm shadow-inner">
          <ZapIcon className="h-3.5 w-3.5 text-violet-400" />
          Powered by Google ADK &amp; Gemini 2.5 Multi-Agent Review Pipeline
        </div>

        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl leading-[1.15]">
          Autonomous{" "}
          <span className="bg-gradient-to-r from-violet-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            Pull Request Reviews
          </span>
          <br />
          Built for High-Velocity Teams
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-base sm:text-lg text-muted-foreground leading-relaxed">
          PullSense automates first-pass code reviews by checking security vulnerabilities,
          architectural conventions, missing unit tests, and style rules — returning comprehensive
          inline feedback in seconds.
        </p>

        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          {isLoaded && isSignedIn ? (
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-6 py-3 text-sm font-medium text-white transition-all hover:bg-violet-700 hover:shadow-lg hover:shadow-violet-600/25"
            >
              <LayoutDashboardIcon className="h-4 w-4" />
              Open Organization Dashboard
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
          ) : (
            <Link
              href="/sign-up"
              className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-6 py-3 text-sm font-medium text-white transition-all hover:bg-violet-700 hover:shadow-lg hover:shadow-violet-600/25"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              Get Started with GitHub
            </Link>
          )}

          <Link
            href="#features"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-card/60 px-6 py-3 text-sm font-medium transition-colors hover:bg-accent"
          >
            Explore AI Agents
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative z-10 mx-auto max-w-6xl px-6 py-16">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight">
            Six Specialized AI Agents Working in Parallel
          </h2>
          <p className="mt-3 text-muted-foreground text-sm max-w-xl mx-auto">
            Each agent is dedicated to a distinct code quality facet, backed by Pinecone RAG vectors and 3-tier team memory.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <FeatureCard
            icon={<ShieldCheckIcon className="h-6 w-6 text-red-400" />}
            title="Security Agent"
            description="Detects OWASP vulnerabilities, token leaks, and injection risks before they reach production."
          />
          <FeatureCard
            icon={<CodeIcon className="h-6 w-6 text-blue-400" />}
            title="Style &amp; Clean Code Agent"
            description="Enforces coding standards, naming conventions, and idiomatic practices tailored to your stack."
          />
          <FeatureCard
            icon={<TestTubeIcon className="h-6 w-6 text-emerald-400" />}
            title="Test Coverage Agent"
            description="Identifies untested public endpoints, missing assertions, and fragile mock contracts."
          />
          <FeatureCard
            icon={<BrainIcon className="h-6 w-6 text-purple-400" />}
            title="Codebase Context Agent"
            description="Leverages Pinecone RAG vectors and team architecture memory to prevent anti-patterns."
          />
          <FeatureCard
            icon={<ZapIcon className="h-6 w-6 text-amber-400" />}
            title="Triage Agent"
            description="Intelligently classifies PR risk and routes reviews to specialized agents with dynamic temperature."
          />
          <FeatureCard
            icon={<GitPullRequestIcon className="h-6 w-6 text-indigo-400" />}
            title="Aggregator Agent"
            description="Synthesizes findings into unified markdown summaries with precise GitHub inline comments."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 py-8 text-center text-sm text-muted-foreground">
        <p>© {new Date().getFullYear()} PullSense. AI-Powered Code Reviews.</p>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="group rounded-xl border border-border/50 bg-card/50 p-6 backdrop-blur-sm transition-all hover:border-violet-600/30 hover:bg-card/80 hover:shadow-lg hover:shadow-violet-600/5">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-accent">
        {icon}
      </div>
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
}
