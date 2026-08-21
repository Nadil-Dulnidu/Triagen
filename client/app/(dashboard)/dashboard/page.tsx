"use client";

import Link from "next/link";
import {
  GitPullRequestIcon,
  ShieldAlertIcon,
  ClockIcon,
  ZapIcon,
  FolderGit2Icon,
  SparklesIcon,
  ArrowUpRightIcon,
  CheckCircle2Icon,
  AlertTriangleIcon,
  PlusIcon,
  BrainIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// Showcase data for demonstration
const OVERVIEW_METRICS = {
  total_reviews: 142,
  hours_saved: 71.0,
  critical_prevented: 18,
  active_repos: 6,
  avg_latency: "2.3s",
};

const RECENT_REVIEWS = [
  {
    id: "rev-101",
    pr_number: 42,
    title: "Implement JWT verification middleware & session validation",
    repo: "acme-corp/api-gateway",
    author: "sarah-dev",
    status: "completed",
    critical_count: 1,
    warning_count: 2,
    suggestion_count: 3,
    created_at: "10m ago",
  },
  {
    id: "rev-102",
    pr_number: 18,
    title: "Refactor database connection pool and retry policies",
    repo: "acme-corp/core-service",
    author: "alex-chen",
    status: "completed",
    critical_count: 0,
    warning_count: 1,
    suggestion_count: 4,
    created_at: "1h ago",
  },
  {
    id: "rev-103",
    pr_number: 89,
    title: "Add Stripe webhook signature verification and checkout flow",
    repo: "acme-corp/billing-service",
    author: "jordan-m",
    status: "completed",
    critical_count: 2,
    warning_count: 1,
    suggestion_count: 1,
    created_at: "3h ago",
  },
];

const CONNECTED_REPOS_PREVIEW = [
  { name: "acme-corp/api-gateway", language: "Python", reviews: 48, status: "Active" },
  { name: "acme-corp/core-service", language: "TypeScript", reviews: 36, status: "Active" },
  { name: "acme-corp/billing-service", language: "Go", reviews: 29, status: "Active" },
  { name: "acme-corp/frontend-app", language: "React", reviews: 29, status: "Active" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Banner */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Organization Overview</h1>
            <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 gap-1 text-xs">
              <CheckCircle2Icon className="h-3 w-3" />
              All 6 AI Agents Active
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time code review telemetry, vulnerability prevention, and developer throughput.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/repositories">
            <Button variant="outline" size="sm" className="gap-2">
              <FolderGit2Icon className="h-4 w-4" />
              Manage Repos
            </Button>
          </Link>
          <Link href="/reviews">
            <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-white gap-2">
              <GitPullRequestIcon className="h-4 w-4" />
              View All Reviews
            </Button>
          </Link>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Total AI Reviews</span>
            <GitPullRequestIcon className="h-4 w-4 text-violet-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{OVERVIEW_METRICS.total_reviews}</span>
            <span className="text-xs text-emerald-400 font-medium">+24% this month</span>
          </div>
          <p className="text-xs text-muted-foreground">Automated PR checks completed</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Developer Time Saved</span>
            <ClockIcon className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{OVERVIEW_METRICS.hours_saved}h</span>
            <span className="text-xs text-emerald-400 font-medium">~30m / review</span>
          </div>
          <p className="text-xs text-muted-foreground">Eliminating first-pass review overhead</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Critical Issues Blocked</span>
            <ShieldAlertIcon className="h-4 w-4 text-red-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{OVERVIEW_METRICS.critical_prevented}</span>
            <span className="text-xs text-red-400 font-medium">Security & Auth</span>
          </div>
          <p className="text-xs text-muted-foreground">Caught before production deployment</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Avg Review Latency</span>
            <ZapIcon className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{OVERVIEW_METRICS.avg_latency}</span>
            <span className="text-xs text-muted-foreground">Gemini 2.5 Flash + Pro</span>
          </div>
          <p className="text-xs text-muted-foreground">Multi-agent parallel execution</p>
        </div>
      </div>

      {/* Main Grid: Recent Reviews + Quick Repos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Activity Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <SparklesIcon className="h-5 w-5 text-violet-400" />
              <h2 className="text-lg font-bold tracking-tight">Recent AI Reviews</h2>
            </div>
            <Link
              href="/reviews"
              className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1 font-medium"
            >
              View all
              <ArrowUpRightIcon className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="grid gap-3">
            {RECENT_REVIEWS.map((review) => (
              <Link
                key={review.id}
                href={`/reviews/${review.id}`}
                className="group flex flex-col justify-between gap-3 rounded-xl border border-border/70 bg-card/60 p-4 transition-all hover:border-violet-500/40 hover:bg-card/90"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground">{review.repo}</span>
                    <Badge variant="outline" className="text-xs font-mono">
                      #{review.pr_number}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground font-mono">{review.created_at}</span>
                </div>

                <h3 className="font-semibold text-foreground text-sm group-hover:text-violet-400 transition-colors">
                  {review.title}
                </h3>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/40 text-xs">
                  <span className="text-muted-foreground">
                    Author: <strong className="text-foreground">{review.author}</strong>
                  </span>

                  <div className="flex items-center gap-2">
                    {review.critical_count > 0 && (
                      <Badge className="bg-red-500/15 text-red-400 border-red-500/30 gap-1 text-[11px]">
                        <ShieldAlertIcon className="h-3 w-3" />
                        {review.critical_count}
                      </Badge>
                    )}
                    {review.warning_count > 0 && (
                      <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1 text-[11px]">
                        <AlertTriangleIcon className="h-3 w-3" />
                        {review.warning_count}
                      </Badge>
                    )}
                    {review.suggestion_count > 0 && (
                      <Badge variant="outline" className="text-muted-foreground text-[11px]">
                        {review.suggestion_count} suggestions
                      </Badge>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Quick Repos & Memory Card */}
        <div className="space-y-6">
          {/* Active Repositories */}
          <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FolderGit2Icon className="h-4 w-4 text-violet-400" />
                <h3 className="text-sm font-semibold">Connected Repositories</h3>
              </div>
              <Link
                href="/repositories"
                className="text-xs text-violet-400 hover:text-violet-300 font-medium"
              >
                Manage
              </Link>
            </div>

            <div className="divide-y divide-border/40 text-xs font-mono">
              {CONNECTED_REPOS_PREVIEW.map((r, idx) => (
                <div key={idx} className="py-2.5 flex items-center justify-between">
                  <div>
                    <p className="font-sans font-medium text-foreground truncate max-w-[160px]">
                      {r.name.split("/")[1]}
                    </p>
                    <span className="text-[11px] text-muted-foreground">{r.language}</span>
                  </div>
                  <Badge variant="secondary" className="text-[10px] bg-accent/60">
                    {r.reviews} reviews
                  </Badge>
                </div>
              ))}
            </div>

            <Link href="/repositories" className="block w-full">
              <Button variant="outline" size="sm" className="w-full text-xs gap-1.5 mt-2">
                <PlusIcon className="h-3.5 w-3.5" />
                Connect New Repository
              </Button>
            </Link>
          </div>

          {/* Persistent Memory Card */}
          <div className="rounded-xl border border-violet-500/30 bg-violet-950/20 p-5 space-y-3">
            <div className="flex items-center gap-2">
              <BrainIcon className="h-4 w-4 text-violet-400" />
              <h3 className="text-sm font-semibold text-foreground">Active Team Memory</h3>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              PullSense is enforcing <strong>6 architectural rules & conventions</strong> across all active PR reviews.
            </p>
            <Link href="/memory" className="block pt-1">
              <Button size="sm" variant="secondary" className="w-full text-xs bg-violet-900/40 hover:bg-violet-900/60 text-violet-200">
                View & Edit Rules
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
