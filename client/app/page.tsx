import Link from "next/link";
import {
  GitPullRequestIcon,
  ShieldCheckIcon,
  CodeIcon,
  TestTubeIcon,
  BrainIcon,
  ZapIcon,
  ArrowRightIcon,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Background gradient effects */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-violet-600/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 lg:px-12">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600">
            <GitPullRequestIcon className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">PullSense</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/sign-in"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Sign In
          </Link>
          <Link
            href="/sign-up"
            className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-violet-700"
          >
            Get Started
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-5xl px-6 pt-20 pb-16 text-center lg:pt-32">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border/50 bg-card/50 px-4 py-1.5 text-sm text-muted-foreground backdrop-blur-sm">
          <ZapIcon className="h-3.5 w-3.5 text-violet-400" />
          Powered by Google ADK multi-agent AI
        </div>

        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
          AI-Powered{" "}
          <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            Pull Request Reviews
          </span>
          <br />
          That Actually Help
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
          PullSense automates your first-pass code reviews by checking security,
          coding style, test coverage, and team conventions — so your team can
          focus on what matters.
        </p>

        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/sign-up"
            className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-6 py-3 text-sm font-medium text-white transition-all hover:bg-violet-700 hover:shadow-lg hover:shadow-violet-600/25"
          >
            <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            Connect with GitHub
          </Link>
          <Link
            href="#features"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-6 py-3 text-sm font-medium transition-colors hover:bg-accent"
          >
            Learn More
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative z-10 mx-auto max-w-6xl px-6 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight">
            Six specialized AI agents working together
          </h2>
          <p className="mt-3 text-muted-foreground">
            Each agent is an expert in its domain, providing focused and actionable
            feedback.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <FeatureCard
            icon={<ShieldCheckIcon className="h-6 w-6 text-red-400" />}
            title="Security Agent"
            description="Detects vulnerabilities, unsafe patterns, and dependency risks before they reach production."
          />
          <FeatureCard
            icon={<CodeIcon className="h-6 w-6 text-blue-400" />}
            title="Style Agent"
            description="Enforces coding conventions, naming standards, and formatting consistency across your codebase."
          />
          <FeatureCard
            icon={<TestTubeIcon className="h-6 w-6 text-green-400" />}
            title="Test Coverage Agent"
            description="Identifies missing tests, coverage gaps, and suggests test cases for new code paths."
          />
          <FeatureCard
            icon={<BrainIcon className="h-6 w-6 text-purple-400" />}
            title="Codebase Context Agent"
            description="Uses RAG to understand your repo's architecture and provide context-aware feedback."
          />
          <FeatureCard
            icon={<ZapIcon className="h-6 w-6 text-yellow-400" />}
            title="Triage Agent"
            description="Intelligently classifies PRs and routes them to the right agents based on the changes."
          />
          <FeatureCard
            icon={<GitPullRequestIcon className="h-6 w-6 text-indigo-400" />}
            title="Aggregator Agent"
            description="Synthesizes all findings into a clear, prioritized review with actionable inline comments."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 py-8 text-center text-sm text-muted-foreground">
        <p>© {new Date().getFullYear()} PullSense. Open Source.</p>
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
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
}
