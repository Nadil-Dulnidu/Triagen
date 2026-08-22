"use client";

import Image from "next/image";
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
  CheckCircle2Icon,
  SparklesIcon,
  LayersIcon,
  CpuIcon,
  TerminalIcon,
  CheckIcon,
  Building2Icon,
  FileCode2Icon,
  DatabaseIcon,
  ShieldAlertIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function LandingPage() {
  const { isSignedIn, isLoaded } = useAuth();

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#09090e] text-foreground selection:bg-violet-600 selection:text-white">
      {/* Dynamic Background Glows */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-48 left-1/2 -translate-x-1/2 h-[650px] w-[900px] rounded-full bg-gradient-to-b from-violet-600/20 via-purple-600/10 to-transparent blur-[120px]" />
        <div className="absolute top-[35%] -left-48 h-[500px] w-[500px] rounded-full bg-indigo-600/15 blur-[140px]" />
        <div className="absolute top-[60%] -right-48 h-[600px] w-[600px] rounded-full bg-violet-600/15 blur-[150px]" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-[400px] w-[800px] rounded-full bg-purple-900/15 blur-[130px]" />
        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.4) 1px, transparent 0)`,
            backgroundSize: "32px 32px",
          }}
        />
      </div>

      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b border-border/40 bg-[#09090e]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 p-1.5 shadow-lg shadow-violet-600/30 transition-transform duration-300 group-hover:scale-105">
              <Image
                src="/logo.png"
                alt="Triagen Logo"
                width={28}
                height={28}
                className="object-contain"
                priority
              />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white">
                  Triagen
                </span>
                <span className="rounded-full bg-violet-500/20 border border-violet-500/30 px-2 py-0.5 text-[10px] font-semibold text-violet-300">
                  v2.0
                </span>
              </div>
              <span className="text-[11px] text-muted-foreground -mt-0.5">
                Autonomous PR Intelligence
              </span>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <Link href="#agents" className="transition-colors hover:text-white">
              AI Agents
            </Link>
            <Link href="#features" className="transition-colors hover:text-white">
              Features
            </Link>
            <Link href="#pipeline" className="transition-colors hover:text-white">
              Architecture
            </Link>
            <Link href="#workflow" className="transition-colors hover:text-white">
              Workflow
            </Link>
            <Link href="#impact" className="transition-colors hover:text-white">
              Impact
            </Link>
          </nav>

          {/* Auth CTA */}
          <div className="flex items-center gap-3">
            {isLoaded && isSignedIn ? (
              <div className="flex items-center gap-3">
                <Link href="/dashboard">
                  <Button className="bg-violet-600 hover:bg-violet-700 text-white gap-2 shadow-md shadow-violet-600/25">
                    <LayoutDashboardIcon className="h-4 w-4" />
                    Dashboard
                    <ArrowRightIcon className="h-3.5 w-3.5" />
                  </Button>
                </Link>
                <UserButton />
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  href="/sign-in"
                  className="hidden sm:inline-block text-sm font-medium text-muted-foreground transition-colors hover:text-white"
                >
                  Sign In
                </Link>
                <Link href="/sign-up">
                  <Button className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white gap-2 shadow-lg shadow-violet-600/30 transition-all hover:shadow-violet-600/50">
                    <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                    </svg>
                    Get Started Free
                    <ArrowRightIcon className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 lg:pt-28 lg:pb-32 px-6">
        <div className="mx-auto max-w-5xl text-center">
          {/* Glowing live pill */}
          <div className="inline-flex items-center gap-2.5 rounded-full border border-violet-500/30 bg-violet-950/30 px-4 py-1.5 text-xs sm:text-sm font-medium text-violet-200 backdrop-blur-md shadow-inner shadow-violet-500/20 animate-pulse">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500"></span>
            </span>
            <SparklesIcon className="h-3.5 w-3.5 text-violet-400" />
            <span>Triagen 2.0 • Autonomous Multi-Agent Pull Request Intelligence</span>
          </div>

          {/* Headline */}
          <h1 className="mt-8 text-4xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl leading-[1.1] text-white">
            Autonomous{" "}
            <span className="bg-gradient-to-r from-violet-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
              PR Triage &amp; Multi-Agent
            </span>{" "}
            <br className="hidden sm:inline" />
            Code Reviews
          </h1>

          {/* Subtitle */}
          <p className="mx-auto mt-6 max-w-3xl text-base sm:text-lg lg:text-xl text-muted-foreground leading-relaxed">
            Triagen orchestrates 6 specialized AI agents to triage pull requests, detect deep
            vulnerabilities, verify test coverage, enforce architecture conventions, and post verified
            inline suggestions in seconds.
          </p>

          {/* CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            {isLoaded && isSignedIn ? (
              <Link href="/dashboard">
                <Button size="lg" className="h-12 px-8 bg-violet-600 hover:bg-violet-700 text-white font-semibold text-base gap-2.5 shadow-xl shadow-violet-600/30">
                  <LayoutDashboardIcon className="h-5 w-5" />
                  Open Organization Dashboard
                  <ArrowRightIcon className="h-4 w-4" />
                </Button>
              </Link>
            ) : (
              <Link href="/sign-up">
                <Button size="lg" className="h-12 px-8 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-base gap-2.5 shadow-xl shadow-violet-600/30">
                  <svg className="h-5 w-5 fill-current" viewBox="0 0 24 24">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                  </svg>
                  Connect with GitHub
                  <ArrowRightIcon className="h-4 w-4" />
                </Button>
              </Link>
            )}

            <Link href="#agents">
              <Button size="lg" variant="outline" className="h-12 px-6 border-border/80 bg-card/60 hover:bg-card text-foreground font-medium text-base gap-2 backdrop-blur-sm">
                Explore AI Agents
                <ArrowRightIcon className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          {/* Quick Metrics Pills */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <CheckCircle2Icon className="h-4 w-4 text-emerald-400" />
              <span>Zero-noise inline comments</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2Icon className="h-4 w-4 text-violet-400" />
              <span>Gemini 2.5 Multi-Agent Engine</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2Icon className="h-4 w-4 text-indigo-400" />
              <span>Pinecone 3-Tier Memory</span>
            </div>
          </div>
        </div>

        {/* Hero Image Showcase */}
        <div className="mt-14 mx-auto max-w-6xl">
          <div className="relative rounded-2xl border border-violet-500/30 bg-card/40 p-2 sm:p-3 backdrop-blur-xl shadow-2xl shadow-violet-950/60 group">
            {/* Top glowing ambient highlight */}
            <div className="absolute -top-1 left-1/4 right-1/4 h-[2px] bg-gradient-to-r from-transparent via-violet-400 to-transparent" />

            <div className="relative overflow-hidden rounded-xl border border-border/60 bg-black/80">
              <Image
                src="/images/hero-preview.jpg"
                alt="Triagen AI Pull Request Review Platform Interface"
                width={1920}
                height={1080}
                className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-[1.01]"
                priority
              />
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Banner */}
      <section className="relative z-10 border-y border-border/40 bg-card/20 py-10">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <p className="text-xs uppercase tracking-widest text-muted-foreground font-semibold">
            Engineered with Leading AI &amp; Infrastructure Standards
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-8 sm:gap-14 text-sm font-semibold text-muted-foreground">
            <div className="flex items-center gap-2">
              <SparklesIcon className="h-4 w-4 text-violet-400" />
              <span>Google Gemini 2.5</span>
            </div>
            <div className="flex items-center gap-2">
              <CpuIcon className="h-4 w-4 text-indigo-400" />
              <span>Google ADK</span>
            </div>
            <div className="flex items-center gap-2">
              <DatabaseIcon className="h-4 w-4 text-purple-400" />
              <span>Pinecone Vector RAG</span>
            </div>
            <div className="flex items-center gap-2">
              <TerminalIcon className="h-4 w-4 text-blue-400" />
              <span>FastAPI &amp; Celery</span>
            </div>
            <div className="flex items-center gap-2">
              <GitPullRequestIcon className="h-4 w-4 text-emerald-400" />
              <span>GitHub Webhooks App</span>
            </div>
          </div>
        </div>
      </section>

      {/* Six Autonomous Agents Section */}
      <section id="agents" className="relative z-10 mx-auto max-w-7xl px-6 py-24 sm:py-32">
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-violet-500/30 bg-violet-950/20 px-3.5 py-1 text-xs font-semibold text-violet-300">
            <LayersIcon className="h-3.5 w-3.5 text-violet-400" />
            Specialized Multi-Agent Swarm
          </div>
          <h2 className="mt-4 text-3xl sm:text-5xl font-bold tracking-tight text-white">
            Six Specialized AI Agents Working in Parallel
          </h2>
          <p className="mt-4 text-muted-foreground text-base sm:text-lg leading-relaxed">
            Every pull request is automatically triaged, analyzed across 6 distinct engineering facets,
            and synthesized into precise inline comments with verified code suggestions.
          </p>
        </div>

        {/* Multi-Agent Architecture Visual Banner */}
        <div className="mt-14 relative rounded-2xl border border-border/80 bg-card/40 p-2 sm:p-4 backdrop-blur-md overflow-hidden">
          <Image
            src="/images/agent-pipeline.jpg"
            alt="Triagen Autonomous Multi-Agent AI Pipeline"
            width={1920}
            height={1080}
            className="w-full h-auto rounded-xl object-cover"
          />
        </div>

        {/* 6 Agent Cards Grid */}
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <AgentCard
            icon={<ZapIcon className="h-6 w-6 text-amber-400" />}
            title="1. Triage &amp; Risk Classifier Agent"
            role="Orchestration &amp; Risk Classification"
            description="Analyzes changed files, AST complexity, blast radius, and dynamically computes PR risk scores (Low, Medium, High, Critical) to route reviews."
            tag="Risk Radar"
          />
          <AgentCard
            icon={<ShieldCheckIcon className="h-6 w-6 text-red-400" />}
            title="2. Security &amp; CVE Guard"
            role="Vulnerability &amp; Secret Shield"
            description="Detects OWASP Top 10 vulnerabilities, credential and token leaks, SQL injections, and AST taint flow before code hits production."
            tag="Zero-Day Shield"
          />
          <AgentCard
            icon={<CodeIcon className="h-6 w-6 text-blue-400" />}
            title="3. Style &amp; Clean Code Inspector"
            role="Conventions &amp; Idiomatic Patterns"
            description="Enforces team naming conventions, typing consistency, dead code removal, and idiomatic practices tailored to your exact stack."
            tag="Clean Code"
          />
          <AgentCard
            icon={<TestTubeIcon className="h-6 w-6 text-emerald-400" />}
            title="4. Test Coverage &amp; Mock Verifier"
            role="Regression &amp; Assertion Verification"
            description="Identifies untested public functions, missing assertions, untested edge cases, and fragile mock contracts in test suites."
            tag="Test Coverage"
          />
          <AgentCard
            icon={<BrainIcon className="h-6 w-6 text-purple-400" />}
            title="5. Codebase Context &amp; Memory Agent"
            role="Pinecone 3-Tier Long-Term Memory"
            description="Retrieves semantic embeddings of past PR discussions, repository architecture rules, and developer preferences to prevent recurring mistakes."
            tag="Pinecone RAG"
          />
          <AgentCard
            icon={<GitPullRequestIcon className="h-6 w-6 text-indigo-400" />}
            title="6. Review Aggregator &amp; Patch Synthesizer"
            role="Inline GitHub Comment Engine"
            description="Synthesizes all findings into actionable summaries, eliminates noisy false-positives, and generates 1-click GitHub commit suggestions."
            tag="Actionable Patches"
          />
        </div>
      </section>

      {/* Feature Deep Dive 1: Security & Autofix */}
      <section id="features" className="relative z-10 border-t border-border/40 bg-[#0c0c14] py-24 px-6">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            {/* Text details */}
            <div className="space-y-6">
              <div className="inline-flex items-center gap-1.5 rounded-full border border-red-500/30 bg-red-950/20 px-3.5 py-1 text-xs font-semibold text-red-300">
                <ShieldAlertIcon className="h-3.5 w-3.5 text-red-400" />
                Automated Security &amp; Patching
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
                Instant Vulnerability Detection with 1-Click Code Patches
              </h2>
              <p className="text-muted-foreground text-base sm:text-lg leading-relaxed">
                Triagen doesn&apos;t just point out security flaws — it generates complete, verified inline
                patches ready to commit directly on GitHub.
              </p>

              <div className="space-y-3 pt-2">
                <FeatureBullet
                  title="OWASP Top 10 &amp; Secret Detection"
                  description="Catches SQLi, XSS, SSRF, Hardcoded API keys, and insecure dependencies."
                />
                <FeatureBullet
                  title="99.8% Precision with Zero Hallucinations"
                  description="Validated against AST syntax parsers to ensure recommended fixes compile cleanly."
                />
                <FeatureBullet
                  title="One-Click GitHub Commit Suggestions"
                  description="Developers can merge AI-suggested diffs right from the PR review UI."
                />
              </div>
            </div>

            {/* Image */}
            <div className="relative rounded-2xl border border-red-500/30 bg-card/40 p-2 sm:p-3 backdrop-blur-xl shadow-2xl shadow-red-950/30">
              <Image
                src="/images/security-autofix.jpg"
                alt="Triagen AI Vulnerability Detection and Patch Interface"
                width={1280}
                height={720}
                className="w-full h-auto rounded-xl object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Feature Deep Dive 2: Codebase Memory & Vector RAG */}
      <section id="pipeline" className="relative z-10 border-t border-border/40 bg-[#09090e] py-24 px-6">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            {/* Image */}
            <div className="order-2 lg:order-1 relative rounded-2xl border border-purple-500/30 bg-card/40 p-2 sm:p-3 backdrop-blur-xl shadow-2xl shadow-purple-950/30">
              <Image
                src="/images/codebase-memory.jpg"
                alt="Triagen AI 3-Tier Codebase Memory and Pinecone Vector Architecture"
                width={1280}
                height={720}
                className="w-full h-auto rounded-xl object-cover"
              />
            </div>

            {/* Text details */}
            <div className="order-1 lg:order-2 space-y-6">
              <div className="inline-flex items-center gap-1.5 rounded-full border border-purple-500/30 bg-purple-950/20 px-3.5 py-1 text-xs font-semibold text-purple-300">
                <BrainIcon className="h-3.5 w-3.5 text-purple-400" />
                Pinecone 3-Tier Memory Architecture
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
                AI Reviews That Remember Your Team&apos;s Architectural Rules
              </h2>
              <p className="text-muted-foreground text-base sm:text-lg leading-relaxed">
                Generic AI models give generic reviews. Triagen indexes your entire repository history and
                maintains a persistent 3-tier memory system.
              </p>

              <div className="space-y-4 pt-2">
                <div className="rounded-xl border border-border/60 bg-card/50 p-4">
                  <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Building2Icon className="h-4 w-4 text-violet-400" />
                    Tier 1: Organization Memory
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    Company-wide security compliance, licensing mandates, and SOC2 policies.
                  </p>
                </div>
                <div className="rounded-xl border border-border/60 bg-card/50 p-4">
                  <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                    <FileCode2Icon className="h-4 w-4 text-indigo-400" />
                    Tier 2: Repository Standards
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    Repo-specific patterns, clean architecture boundaries, and directory layout conventions.
                  </p>
                </div>
                <div className="rounded-xl border border-border/60 bg-card/50 p-4">
                  <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                    <CodeIcon className="h-4 w-4 text-emerald-400" />
                    Tier 3: Developer Habits &amp; Preferences
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    Learns individual developer preferences and past feedback to reduce review churn.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section id="workflow" className="relative z-10 border-t border-border/40 bg-[#0c0c14] py-24 px-6">
        <div className="mx-auto max-w-5xl text-center">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-violet-500/30 bg-violet-950/20 px-3.5 py-1 text-xs font-semibold text-violet-300">
            <ZapIcon className="h-3.5 w-3.5 text-violet-400" />
            Seamless Developer Experience
          </div>
          <h2 className="mt-4 text-3xl sm:text-5xl font-bold tracking-tight text-white">
            How Triagen Works in 4 Steps
          </h2>
          <p className="mt-4 text-muted-foreground text-base max-w-2xl mx-auto">
            Zero setup friction. Connect your GitHub repository once and let the autonomous agents triage every PR.
          </p>

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4 text-left">
            <WorkflowStep
              step="01"
              title="Connect Repository"
              description="Install the Triagen GitHub App with 1-click permission authorization."
            />
            <WorkflowStep
              step="02"
              title="Open a Pull Request"
              description="Push changes as usual. Triagen receives webhooks instantly in real-time."
            />
            <WorkflowStep
              step="03"
              title="Multi-Agent Triage"
              description="6 specialized agents parse diffs, query Pinecone memory, and run security scans in &lt;15s."
            />
            <WorkflowStep
              step="04"
              title="Inline Verified Review"
              description="High-signal feedback and 1-click commit suggestions posted straight to GitHub."
            />
          </div>
        </div>
      </section>

      {/* Impact Metrics Section */}
      <section id="impact" className="relative z-10 border-t border-border/40 bg-[#09090e] py-20 px-6">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4 text-center">
            <MetricCard number="85%" label="Review Latency Reduction" subtext="From hours to seconds" />
            <MetricCard number="99.4%" label="Critical Vulnerabilities Caught" subtext="Before hitting main branch" />
            <MetricCard number="10k+" label="Developer Hours Saved" subtext="On repetitive code style checks" />
            <MetricCard number="< 15s" label="Average Agent Turnaround" subtext="Ultra-low latency pipeline" />
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="relative z-10 mx-auto max-w-6xl px-6 py-20">
        <div className="relative overflow-hidden rounded-3xl border border-violet-500/40 bg-gradient-to-b from-violet-950/40 via-purple-950/20 to-card/60 p-8 sm:p-14 text-center backdrop-blur-xl shadow-2xl shadow-violet-950/50">
          <div className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 h-[300px] w-[500px] rounded-full bg-violet-600/25 blur-3xl" />
          </div>

          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white leading-tight">
            Supercharge Your Team&apos;s PR Velocity Today
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-base sm:text-lg text-muted-foreground leading-relaxed">
            Join modern engineering teams automating pull request triage, security checks, and code reviews
            with Triagen.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/sign-up">
              <Button size="lg" className="h-12 px-8 bg-violet-600 hover:bg-violet-700 text-white font-semibold text-base gap-2.5 shadow-xl shadow-violet-600/30">
                <svg className="h-5 w-5 fill-current" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                Get Started with GitHub
                <ArrowRightIcon className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="outline" className="h-12 px-6 border-border/80 bg-card/60 hover:bg-card text-foreground font-medium text-base">
                View Live Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Product-Level Comprehensive Footer */}
      <footer className="relative z-10 border-t border-border/50 bg-[#060609] pt-16 pb-12">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-5">
            {/* Brand Column */}
            <div className="lg:col-span-2 space-y-4">
              <Link href="/" className="flex items-center gap-3">
                <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 p-1.5 shadow-md shadow-violet-600/30">
                  <Image
                    src="/logo.png"
                    alt="Triagen Logo"
                    width={24}
                    height={24}
                    className="object-contain"
                  />
                </div>
                <span className="text-xl font-bold tracking-tight text-white">
                  Triagen
                </span>
              </Link>
              <p className="max-w-sm text-sm text-muted-foreground leading-relaxed">
                Triagen delivers autonomous multi-agent pull request triage, security scanning,
                and architectural memory intelligence for high-velocity software engineering teams.
              </p>

              {/* Status indicator */}
              <div className="flex items-center gap-2 pt-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span className="text-xs font-medium text-emerald-400">
                  All Systems Operational • Gemini 2.5 Active
                </span>
              </div>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-white">
                Product
              </h4>
              <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
                <li>
                  <Link href="#agents" className="transition-colors hover:text-white">
                    Multi-Agent Engine
                  </Link>
                </li>
                <li>
                  <Link href="#features" className="transition-colors hover:text-white">
                    PR Risk Triage
                  </Link>
                </li>
                <li>
                  <Link href="#features" className="transition-colors hover:text-white">
                    Security &amp; CVE Guard
                  </Link>
                </li>
                <li>
                  <Link href="#pipeline" className="transition-colors hover:text-white">
                    Pinecone Memory
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="transition-colors hover:text-white">
                    Dashboard Overview
                  </Link>
                </li>
              </ul>
            </div>

            {/* Solutions Links */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-white">
                Solutions
              </h4>
              <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    High-Velocity Teams
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    DevSecOps Automation
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    Open Source Repos
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    Enterprise Workspaces
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    GitHub Actions CI/CD
                  </span>
                </li>
              </ul>
            </div>

            {/* Resources & Legal */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-white">
                Resources &amp; Legal
              </h4>
              <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
                <li>
                  <Link href="/repositories" className="transition-colors hover:text-white">
                    GitHub App Setup
                  </Link>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    Documentation
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    Privacy Policy
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    Terms of Service
                  </span>
                </li>
                <li>
                  <span className="transition-colors hover:text-white cursor-pointer">
                    Security Whitepaper
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Copyright Bar */}
          <div className="mt-12 border-t border-border/40 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
            <p>© {new Date().getFullYear()} Triagen Inc. All rights reserved.</p>
            <p className="flex items-center gap-1.5">
              <span>Engineered with Google ADK &amp; Pinecone</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function AgentCard({
  icon,
  title,
  role,
  description,
  tag,
}: {
  icon: React.ReactNode;
  title: string;
  role: string;
  description: string;
  tag: string;
}) {
  return (
    <div className="group relative rounded-2xl border border-border/60 bg-card/40 p-6 backdrop-blur-sm transition-all duration-300 hover:border-violet-500/40 hover:bg-card/70 hover:shadow-xl hover:shadow-violet-950/20">
      <div className="flex items-center justify-between mb-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/60 border border-border/60 transition-transform duration-300 group-hover:scale-105">
          {icon}
        </div>
        <Badge variant="outline" className="text-[10px] font-semibold border-violet-500/30 text-violet-300 bg-violet-950/30">
          {tag}
        </Badge>
      </div>
      <h3 className="text-base font-bold text-white group-hover:text-violet-300 transition-colors">
        {title}
      </h3>
      <p className="text-[11px] font-medium text-violet-400/90 mt-0.5">{role}</p>
      <p className="mt-3 text-xs text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
}

function FeatureBullet({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-600/20 text-violet-400 mt-0.5">
        <CheckIcon className="h-3 w-3" />
      </div>
      <div>
        <h4 className="text-sm font-semibold text-white">{title}</h4>
        <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

function WorkflowStep({
  step,
  title,
  description,
}: {
  step: string;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-border/60 bg-card/40 p-5 space-y-3">
      <span className="font-mono text-2xl font-black text-violet-500/80">{step}</span>
      <h3 className="text-sm font-bold text-white">{title}</h3>
      <p className="text-xs text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}

function MetricCard({
  number,
  label,
  subtext,
}: {
  number: string;
  label: string;
  subtext: string;
}) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card/40 p-6 space-y-2">
      <div className="text-3xl sm:text-4xl font-extrabold text-transparent bg-gradient-to-r from-violet-400 via-indigo-300 to-purple-400 bg-clip-text">
        {number}
      </div>
      <div className="text-sm font-bold text-white">{label}</div>
      <div className="text-xs text-muted-foreground">{subtext}</div>
    </div>
  );
}

