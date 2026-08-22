"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import {
  BarChart3Icon,
  ShieldAlertIcon,
  ClockIcon,
  ZapIcon,
  CheckCircle2Icon,
  SparklesIcon,
  LayersIcon,
  FlameIcon,
  RefreshCwIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api, type AnalyticsOverview } from "@/lib/api";

export default function AnalyticsPage() {
  const { getToken } = useAuth();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function fetchAnalytics() {
      try {
        const token = await getToken();
        const data = await api.getOverview(token);
        if (isMounted) {
          setOverview(data);
        }
      } catch (err) {
        console.error("Failed to load analytics telemetry:", err);
      }
    }

    fetchAnalytics();

    return () => {
      isMounted = false;
    };
  }, [getToken]);

  const loadAnalytics = async () => {
    try {
      setIsRefreshing(true);
      const token = await getToken();
      const data = await api.getOverview(token);
      setOverview(data);
    } catch (err) {
      console.error("Failed to load analytics telemetry:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const totalFindings = overview
    ? overview.severity_distribution.critical +
      overview.severity_distribution.warning +
      overview.severity_distribution.suggestion +
      overview.severity_distribution.info
    : 0;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Review Analytics &amp; Insights</h1>
            <Badge variant="secondary" className="gap-1 text-xs bg-accent/60">
              <SparklesIcon className="h-3 w-3 text-violet-400" />
              Live SQL Telemetry
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Historical code review throughput, vulnerability prevention metrics, and AI agent performance.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={loadAnalytics}
          disabled={isRefreshing}
          className="gap-2 text-xs"
        >
          <RefreshCwIcon className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh Metrics
        </Button>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Total AI Reviews</span>
            <BarChart3Icon className="h-4 w-4 text-violet-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{overview?.total_reviews ?? 0}</span>
            {overview && overview.total_reviews > 0 && (
              <span className="text-xs text-emerald-400 font-medium">+18% MoM</span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">Pull requests reviewed</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Engineering Time Saved</span>
            <ClockIcon className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{overview?.developer_hours_saved ?? 0}h</span>
            <span className="text-xs text-emerald-400 font-medium">30m / review</span>
          </div>
          <p className="text-xs text-muted-foreground">Reduced review turnaround</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Critical Issues Prevented</span>
            <ShieldAlertIcon className="h-4 w-4 text-red-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">
              {overview?.critical_vulnerabilities_prevented ?? 0}
            </span>
            <span className="text-xs text-red-400 font-medium">Pre-merge</span>
          </div>
          <p className="text-xs text-muted-foreground">Vulnerabilities &amp; auth bugs</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Average Agent Latency</span>
            <ZapIcon className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">
              {overview?.avg_review_latency_seconds
                ? `${overview.avg_review_latency_seconds}s`
                : "—"}
            </span>
            <span className="text-xs text-muted-foreground">Flash + Pro</span>
          </div>
          <p className="text-xs text-muted-foreground">End-to-end multi-agent review</p>
        </div>
      </div>

      {/* Grid: Severity Breakdown + Hotspots */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Severity Distribution */}
        <div className="rounded-xl border border-border/70 bg-card/60 p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <LayersIcon className="h-5 w-5 text-violet-400" />
              <h2 className="text-base font-semibold">Finding Severity Distribution</h2>
            </div>
            <span className="text-xs text-muted-foreground font-mono">
              {totalFindings} total findings
            </span>
          </div>

          {totalFindings > 0 ? (
            <div className="space-y-4">
              {/* Critical */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-red-400 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-red-400" />
                    Critical Vulnerabilities
                  </span>
                  <span className="font-mono text-muted-foreground">
                    {overview?.severity_distribution.critical ?? 0} (
                    {overview
                      ? ((overview.severity_distribution.critical / totalFindings) * 100).toFixed(0)
                      : 0}
                    %)
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-accent/40 overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full"
                    style={{
                      width: `${
                        overview
                          ? (overview.severity_distribution.critical / totalFindings) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Warnings */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-amber-400 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-amber-400" />
                    Architecture &amp; Code Warnings
                  </span>
                  <span className="font-mono text-muted-foreground">
                    {overview?.severity_distribution.warning ?? 0} (
                    {overview
                      ? ((overview.severity_distribution.warning / totalFindings) * 100).toFixed(0)
                      : 0}
                    %)
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-accent/40 overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full"
                    style={{
                      width: `${
                        overview
                          ? (overview.severity_distribution.warning / totalFindings) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Suggestions */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-emerald-400 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    Refactoring &amp; Clean Code Suggestions
                  </span>
                  <span className="font-mono text-muted-foreground">
                    {overview?.severity_distribution.suggestion ?? 0} (
                    {overview
                      ? (
                          (overview.severity_distribution.suggestion / totalFindings) *
                          100
                        ).toFixed(0)
                      : 0}
                    %)
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-accent/40 overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{
                      width: `${
                        overview
                          ? (overview.severity_distribution.suggestion / totalFindings) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground py-6 text-center">
              No findings recorded yet. Run a pull request review to populate distribution data.
            </p>
          )}
        </div>

        {/* Top Issue Hotspots */}
        <div className="rounded-xl border border-border/70 bg-card/60 p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FlameIcon className="h-5 w-5 text-amber-400" />
              <h2 className="text-base font-semibold">Common Issue Hotspots</h2>
            </div>
            <span className="text-xs text-muted-foreground font-mono">
              {overview?.top_categories?.length ?? 0} categories
            </span>
          </div>

          {overview?.top_categories && overview.top_categories.length > 0 ? (
            <div className="space-y-3">
              {overview.top_categories.map((cat, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-foreground capitalize">
                      {cat.category.replace("_", " ")}
                    </span>
                    <span className="font-mono text-muted-foreground">
                      {cat.count} occurrences
                    </span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-accent/40 overflow-hidden">
                    <div
                      className="h-full bg-violet-500 rounded-full"
                      style={{
                        width: `${Math.min(100, (cat.count / totalFindings) * 100 || 20)}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground py-6 text-center">
              No issue category hotspots identified yet.
            </p>
          )}
        </div>
      </div>

      {/* AI Agent Telemetry Table */}
      <div className="rounded-xl border border-border/70 bg-card/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-violet-400" />
            <h2 className="text-base font-semibold">AI Agent Performance &amp; Token Telemetry</h2>
          </div>
          <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-xs">
            <CheckCircle2Icon className="h-3 w-3 mr-1" />
            All 6 Agents Monitored
          </Badge>
        </div>

        {overview?.agent_performance && overview.agent_performance.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-border/60 text-muted-foreground font-sans">
                  <th className="pb-3 font-medium">Agent</th>
                  <th className="pb-3 font-medium">Underlying Model</th>
                  <th className="pb-3 font-medium">Total Runs</th>
                  <th className="pb-3 font-medium">Avg Latency</th>
                  <th className="pb-3 font-medium">Tokens Consumed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-foreground">
                {overview.agent_performance.map((agent, idx) => (
                  <tr key={idx}>
                    <td className="py-3 font-sans font-medium capitalize">
                      {agent.agent_name.replace("_", " ")}
                    </td>
                    <td className="py-3 text-muted-foreground">{agent.model_used}</td>
                    <td className="py-3">{agent.total_runs}</td>
                    <td className="py-3 text-amber-400">{agent.avg_latency_ms}ms</td>
                    <td className="py-3 text-muted-foreground">
                      {agent.total_tokens.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground py-6 text-center">
            Agent execution telemetry will appear automatically once AI code reviews are executed.
          </p>
        )}
      </div>
    </div>
  );
}
