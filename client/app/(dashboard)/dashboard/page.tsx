"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
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
  RefreshCwIcon,
  SparkleIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type AnalyticsOverview,
  type RepositoryResponse,
  type ReviewResponse,
} from "@/lib/api";

export default function DashboardPage() {
  const { getToken } = useAuth();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [recentReviews, setRecentReviews] = useState<ReviewResponse[]>([]);
  const [repositories, setRepositories] = useState<RepositoryResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function fetchDashboard() {
      try {
        const token = await getToken();
        const [overviewData, reviewsData, reposData] = await Promise.all([
          api.getOverview(token).catch(() => null),
          api.getReviews(5, 0, token).catch(() => []),
          api.getRepositories(token).catch(() => []),
        ]);
        if (isMounted) {
          setOverview(overviewData);
          setRecentReviews(reviewsData);
          setRepositories(reposData);
        }
      } catch (err) {
        console.error("Failed to load dashboard telemetry:", err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchDashboard();

    return () => {
      isMounted = false;
    };
  }, [getToken]);

  const handleSeedDemoData = async () => {
    try {
      setIsSeeding(true);
      const token = await getToken();
      await api.seedDemoData(token);
      const [overviewData, reviewsData, reposData] = await Promise.all([
        api.getOverview(token).catch(() => null),
        api.getReviews(5, 0, token).catch(() => []),
        api.getRepositories(token).catch(() => []),
      ]);
      setOverview(overviewData);
      setRecentReviews(reviewsData);
      setRepositories(reposData);
    } catch (err) {
      console.error("Failed to seed demo data:", err);
    } finally {
      setIsSeeding(false);
    }
  };

  const totalReviews = overview?.total_reviews ?? recentReviews.length;
  const hoursSaved = overview?.developer_hours_saved ?? (totalReviews * 0.5);
  const criticalCount = overview?.critical_vulnerabilities_prevented ?? 0;
  const avgLatency = overview?.avg_review_latency_seconds
    ? `${overview.avg_review_latency_seconds}s`
    : "—";

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Banner */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Organization Overview</h1>
            <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 gap-1 text-xs">
              <CheckCircle2Icon className="h-3 w-3" />
              All 6 AI Review Agents Active
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time code review telemetry, vulnerability prevention, and developer throughput.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {totalReviews === 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSeedDemoData}
              disabled={isSeeding}
              className="gap-2 text-xs border-violet-500/40 text-violet-300 hover:bg-violet-950/20"
            >
              <SparkleIcon className={`h-3.5 w-3.5 ${isSeeding ? "animate-spin" : ""}`} />
              {isSeeding ? "Seeding Demo Data..." : "Seed Demo Reviews"}
            </Button>
          )}

          <Link href="/repositories">
            <Button variant="outline" size="sm" className="gap-2 text-xs">
              <FolderGit2Icon className="h-4 w-4" />
              Manage Repos
            </Button>
          </Link>
          <Link href="/reviews">
            <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-white gap-2 text-xs shadow-sm">
              <GitPullRequestIcon className="h-4 w-4" />
              View Reviews
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
            <span className="text-3xl font-bold">{totalReviews}</span>
            {totalReviews > 0 && (
              <span className="text-xs text-emerald-400 font-medium">+18% MoM</span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">Automated PR checks completed</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Developer Time Saved</span>
            <ClockIcon className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{hoursSaved}h</span>
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
            <span className="text-3xl font-bold">{criticalCount}</span>
            <span className="text-xs text-red-400 font-medium">Security &amp; Auth</span>
          </div>
          <p className="text-xs text-muted-foreground">Caught before production merge</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Avg Review Latency</span>
            <ZapIcon className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{avgLatency}</span>
            <span className="text-xs text-muted-foreground">Flash + Pro</span>
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

          {isLoading ? (
            <div className="flex items-center justify-center p-12 text-sm text-muted-foreground border border-dashed rounded-xl">
              <RefreshCwIcon className="h-4 w-4 animate-spin mr-2" />
              Loading real review activity...
            </div>
          ) : recentReviews.length > 0 ? (
            <div className="grid gap-3">
              {recentReviews.map((review) => (
                <Link
                  key={review.id}
                  href={`/reviews/${review.id}`}
                  className="group flex flex-col justify-between gap-3 rounded-xl border border-border/70 bg-card/60 p-4 transition-all hover:border-violet-500/40 hover:bg-card/90"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-muted-foreground">
                        {review.pull_request?.repository?.full_name || "Repository PR"}
                      </span>
                      <Badge variant="outline" className="text-xs font-mono">
                        #{review.pull_request?.number || 1}
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground font-mono">
                      {new Date(review.created_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>

                  <h3 className="font-semibold text-foreground text-sm group-hover:text-violet-400 transition-colors">
                    {review.pull_request?.title || "Pull Request Review"}
                  </h3>

                  <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/40 text-xs">
                    <span className="text-muted-foreground">
                      Author: <strong className="text-foreground">{review.pull_request?.author || "Developer"}</strong>
                    </span>

                    <div className="flex items-center gap-2">
                      {review.critical_count > 0 && (
                        <Badge className="bg-red-500/15 text-red-400 border-red-500/30 gap-1 text-[11px]">
                          <ShieldAlertIcon className="h-3 w-3" />
                          {review.critical_count} critical
                        </Badge>
                      )}
                      {review.warning_count > 0 && (
                        <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1 text-[11px]">
                          <AlertTriangleIcon className="h-3 w-3" />
                          {review.warning_count} warnings
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
          ) : (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
              <GitPullRequestIcon className="h-8 w-8 text-muted-foreground mb-3" />
              <h3 className="text-base font-semibold">No PR reviews yet</h3>
              <p className="mt-1 max-w-sm text-xs text-muted-foreground">
                Connect a GitHub repository or open a pull request to trigger your first automated AI review.
              </p>
              <div className="mt-4 flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleSeedDemoData}
                  disabled={isSeeding}
                  className="text-xs"
                >
                  <SparkleIcon className="h-3.5 w-3.5 mr-1" />
                  Seed Demo PR Reviews
                </Button>
                <Link href="/repositories">
                  <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-white text-xs">
                    Connect Repository
                  </Button>
                </Link>
              </div>
            </div>
          )}
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

            {repositories.length > 0 ? (
              <div className="divide-y divide-border/40 text-xs font-mono">
                {repositories.slice(0, 5).map((r) => (
                  <div key={r.id} className="py-2.5 flex items-center justify-between">
                    <div>
                      <p className="font-sans font-medium text-foreground truncate max-w-[160px]">
                        {r.name}
                      </p>
                      <span className="text-[11px] text-muted-foreground">
                        {r.language || "Repository"}
                      </span>
                    </div>
                    <Badge variant="secondary" className="text-[10px] bg-accent/60">
                      {r.is_active ? "Active" : "Paused"}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground py-2">
                No repositories connected yet.
              </p>
            )}

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
              PullSense enforces custom architectural guidelines, security policies, and team habits on every PR review.
            </p>
            <Link href="/memory" className="block pt-1">
              <Button size="sm" variant="secondary" className="w-full text-xs bg-violet-900/40 hover:bg-violet-900/60 text-violet-200">
                View &amp; Edit Rules
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
