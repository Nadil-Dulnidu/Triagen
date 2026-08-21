"use client";

import {
  BarChart3Icon,
  ShieldAlertIcon,
  ClockIcon,
  ZapIcon,
  CheckCircle2Icon,
  SparklesIcon,
  LayersIcon,
  FlameIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

const ANALYTICS_DATA = {
  total_reviews: 142,
  developer_hours_saved: 71.0,
  critical_prevented: 18,
  avg_latency: "2.3s",
  severity_distribution: {
    critical: 18,
    warning: 45,
    suggestion: 128,
  },
  top_categories: [
    { name: "Auth & JWT Verification", count: 24, severity: "critical", percent: 32 },
    { name: "Uncovered Unit Tests & Mocks", count: 19, severity: "warning", percent: 25 },
    { name: "Clean Architecture Violations", count: 14, severity: "warning", percent: 18 },
    { name: "Sensitive Data Log Leaks", count: 11, severity: "critical", percent: 14 },
    { name: "Generic Exception Handling", count: 8, severity: "suggestion", percent: 11 },
  ],
  agent_performance: [
    { agent: "Triage Agent", model: "gemini-2.5-flash", avg_latency: "380ms", tokens: "92k", accuracy: "99.4%" },
    { agent: "Security Agent", model: "gemini-2.5-flash", avg_latency: "1.1s", tokens: "210k", accuracy: "98.8%" },
    { agent: "Style Agent", model: "gemini-2.5-flash", avg_latency: "890ms", tokens: "175k", accuracy: "97.5%" },
    { agent: "Test Coverage Agent", model: "gemini-2.5-flash", avg_latency: "1.0s", tokens: "190k", accuracy: "98.2%" },
    { agent: "Codebase Context Agent", model: "gemini-2.5-flash", avg_latency: "1.2s", tokens: "240k", accuracy: "96.9%" },
    { agent: "Aggregator Agent", model: "gemini-2.5-pro", avg_latency: "960ms", tokens: "310k", accuracy: "99.1%" },
  ],
};

export default function AnalyticsPage() {
  const totalFindings =
    ANALYTICS_DATA.severity_distribution.critical +
    ANALYTICS_DATA.severity_distribution.warning +
    ANALYTICS_DATA.severity_distribution.suggestion;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Review Analytics & Insights</h1>
            <Badge variant="secondary" className="gap-1 text-xs bg-accent/60">
              <SparklesIcon className="h-3 w-3 text-violet-400" />
              Live Telemetry
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Historical code review throughput, vulnerability prevention metrics, and AI agent performance.
          </p>
        </div>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Total AI Reviews</span>
            <BarChart3Icon className="h-4 w-4 text-violet-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{ANALYTICS_DATA.total_reviews}</span>
            <span className="text-xs text-emerald-400 font-medium">+18% MoM</span>
          </div>
          <p className="text-xs text-muted-foreground">Pull requests reviewed</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Engineering Time Saved</span>
            <ClockIcon className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{ANALYTICS_DATA.developer_hours_saved}h</span>
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
            <span className="text-3xl font-bold">{ANALYTICS_DATA.critical_prevented}</span>
            <span className="text-xs text-red-400 font-medium">Pre-merge</span>
          </div>
          <p className="text-xs text-muted-foreground">Vulnerabilities & auth bugs</p>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground text-xs font-medium uppercase tracking-wider">
            <span>Average Agent Latency</span>
            <ZapIcon className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">{ANALYTICS_DATA.avg_latency}</span>
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
            <span className="text-xs text-muted-foreground font-mono">{totalFindings} total findings</span>
          </div>

          <div className="space-y-4">
            {/* Critical */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-red-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-red-400" />
                  Critical Vulnerabilities
                </span>
                <span className="font-mono text-muted-foreground">
                  {ANALYTICS_DATA.severity_distribution.critical} (
                  {((ANALYTICS_DATA.severity_distribution.critical / totalFindings) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-accent/40 overflow-hidden">
                <div
                  className="h-full bg-red-500 rounded-full"
                  style={{
                    width: `${(ANALYTICS_DATA.severity_distribution.critical / totalFindings) * 100}%`,
                  }}
                />
              </div>
            </div>

            {/* Warnings */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-amber-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-amber-400" />
                  Architecture & Code Warnings
                </span>
                <span className="font-mono text-muted-foreground">
                  {ANALYTICS_DATA.severity_distribution.warning} (
                  {((ANALYTICS_DATA.severity_distribution.warning / totalFindings) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-accent/40 overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full"
                  style={{
                    width: `${(ANALYTICS_DATA.severity_distribution.warning / totalFindings) * 100}%`,
                  }}
                />
              </div>
            </div>

            {/* Suggestions */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-emerald-400 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  Refactoring & Clean Code Suggestions
                </span>
                <span className="font-mono text-muted-foreground">
                  {ANALYTICS_DATA.severity_distribution.suggestion} (
                  {((ANALYTICS_DATA.severity_distribution.suggestion / totalFindings) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-accent/40 overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full"
                  style={{
                    width: `${(ANALYTICS_DATA.severity_distribution.suggestion / totalFindings) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Top Issue Hotspots */}
        <div className="rounded-xl border border-border/70 bg-card/60 p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FlameIcon className="h-5 w-5 text-amber-400" />
              <h2 className="text-base font-semibold">Common Issue Hotspots</h2>
            </div>
            <span className="text-xs text-muted-foreground font-mono">Top 5 categories</span>
          </div>

          <div className="space-y-3">
            {ANALYTICS_DATA.top_categories.map((cat, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">{cat.name}</span>
                  <span className="font-mono text-muted-foreground">{cat.count} occurrences</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-accent/40 overflow-hidden">
                  <div
                    className="h-full bg-violet-500 rounded-full"
                    style={{ width: `${cat.percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Agent Telemetry Table */}
      <div className="rounded-xl border border-border/70 bg-card/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-violet-400" />
            <h2 className="text-base font-semibold">AI Agent Performance & Token Telemetry</h2>
          </div>
          <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-xs">
            <CheckCircle2Icon className="h-3 w-3 mr-1" />
            All Agents Healthy
          </Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-border/60 text-muted-foreground font-sans">
                <th className="pb-3 font-medium">Agent</th>
                <th className="pb-3 font-medium">Underlying Model</th>
                <th className="pb-3 font-medium">Avg Latency</th>
                <th className="pb-3 font-medium">Tokens Consumed</th>
                <th className="pb-3 font-medium">Accuracy Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-foreground">
              {ANALYTICS_DATA.agent_performance.map((agent, idx) => (
                <tr key={idx}>
                  <td className="py-3 font-sans font-medium">{agent.agent}</td>
                  <td className="py-3 text-muted-foreground">{agent.model}</td>
                  <td className="py-3 text-amber-400">{agent.avg_latency}</td>
                  <td className="py-3 text-muted-foreground">{agent.tokens}</td>
                  <td className="py-3 text-emerald-400">{agent.accuracy}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
