"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import {
  ArrowLeftIcon,
  ShieldAlertIcon,
  AlertTriangleIcon,
  LightbulbIcon,
  ZapIcon,
  BrainIcon,
  CheckCircle2Icon,
  SparklesIcon,
  RefreshCwIcon,
  FileCodeIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api, type ReviewResponse } from "@/lib/api";

export default function ReviewDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const reviewId = resolvedParams.id;
  const { getToken } = useAuth();

  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [streamStatus, setStreamStatus] = useState<string>("Review Completed");
  const [isLive, setIsLive] = useState<boolean>(false);

  const loadReview = useCallback(async () => {
    try {
      setIsLoading(true);
      const token = await getToken();
      const data = await api.getReview(reviewId, token);
      setReview(data);
    } catch (err) {
      console.error("Failed to load review:", err);
    } finally {
      setIsLoading(false);
    }
  }, [reviewId, getToken]);

  useEffect(() => {
    let isMounted = true;

    async function fetchReview() {
      try {
        const token = await getToken();
        const data = await api.getReview(reviewId, token);
        if (isMounted) {
          setReview(data);
        }
      } catch (err) {
        console.error("Failed to load review:", err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchReview();

    return () => {
      isMounted = false;
    };
  }, [reviewId, getToken]);

  // Set up SSE listener for live review progress
  useEffect(() => {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const sseUrl = `${apiBase}/api/v1/reviews/${reviewId}/stream`;
    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(sseUrl);
      eventSource.addEventListener("connected", () => {
        setIsLive(true);
      });
      eventSource.addEventListener("review.triaging", () => {
        setStreamStatus("Triage Agent analyzing PR risk & size...");
      });
      eventSource.addEventListener("agent.security.started", () => {
        setStreamStatus("Security Agent checking for vulnerabilities & secrets...");
      });
      eventSource.addEventListener("agent.style.started", () => {
        setStreamStatus("Style Agent inspecting maintainability & conventions...");
      });
      eventSource.addEventListener("agent.test_coverage.started", () => {
        setStreamStatus("Test Coverage Agent checking unit test contracts...");
      });
      eventSource.addEventListener("agent.codebase_context.started", () => {
        setStreamStatus("Codebase Context Agent checking RAG architecture consistency...");
      });
      eventSource.addEventListener("review.aggregating", () => {
        setStreamStatus("Aggregator Agent synthesizing & prioritizing findings...");
      });
      eventSource.addEventListener("review.completed", () => {
        setStreamStatus("Review Completed & Posted to GitHub");
        setIsLive(false);
        loadReview();
        eventSource?.close();
      });
      eventSource.onerror = () => {
        setIsLive(false);
        eventSource?.close();
      };
    } catch (err) {
      console.warn("SSE connection error:", err);
    }

    return () => {
      eventSource?.close();
    };
  }, [reviewId, loadReview]);

  const findings = review?.findings || [];
  const filteredFindings = findings.filter((f) => {
    if (selectedSeverity === "all") return true;
    return f.severity === selectedSeverity;
  });

  const criticalCount = findings.filter((f) => f.severity === "critical").length;
  const warningCount = findings.filter((f) => f.severity === "warning").length;
  const suggestionCount = findings.filter((f) => f.severity === "suggestion").length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-sm text-muted-foreground">
        <RefreshCwIcon className="h-5 w-5 animate-spin mr-2" />
        Loading review findings...
      </div>
    );
  }

  if (!review) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <h2 className="text-lg font-semibold">Review Not Found</h2>
        <p className="text-sm text-muted-foreground">
          The requested review ID could not be found in the database.
        </p>
        <Link href="/reviews">
          <Button variant="outline" size="sm">
            Back to Reviews
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/reviews"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border/80 bg-card hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeftIcon className="h-4 w-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-muted-foreground">
                {review.pull_request?.repository?.full_name || "Repository"}
              </span>
              <Badge variant="outline" className="text-xs font-mono">
                #{review.pull_request?.number || 1}
              </Badge>
              {isLive && (
                <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/40 gap-1.5 animate-pulse">
                  <SparklesIcon className="h-3 w-3" />
                  Live SSE
                </Badge>
              )}
            </div>
            <h1 className="text-xl font-bold tracking-tight mt-0.5">
              {review.pull_request?.title || "Pull Request Review"}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadReview}
            className="gap-2 text-xs"
          >
            <RefreshCwIcon className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Live Progress Banner (if active) */}
      {isLive && (
        <div className="rounded-xl border border-violet-500/30 bg-violet-950/20 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SparklesIcon className="h-5 w-5 text-violet-400 animate-spin" />
            <div>
              <span className="text-sm font-semibold text-foreground">
                Multi-Agent Review in Progress
              </span>
              <p className="text-xs text-muted-foreground">{streamStatus}</p>
            </div>
          </div>
        </div>
      )}

      {/* PR Metadata Card */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Classification</span>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="capitalize text-xs font-medium">
              {review.risk_level} risk
            </Badge>
          </div>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Status</span>
          <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
            <CheckCircle2Icon className="h-3.5 w-3.5 text-emerald-400" />
            <span className="capitalize">{review.status}</span>
          </div>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Execution Latency</span>
          <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
            <ZapIcon className="h-3.5 w-3.5 text-amber-400" />
            <span>
              {review.duration_ms ? `${(review.duration_ms / 1000).toFixed(2)}s` : "—"}
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Author</span>
          <div className="flex items-center gap-2 text-xs font-medium text-foreground">
            <span>{review.pull_request?.author || "Developer"}</span>
          </div>
        </div>
      </div>

      {/* Executive Summary Card */}
      <div className="rounded-xl border border-border/80 bg-card p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BrainIcon className="h-5 w-5 text-violet-400" />
            <h2 className="text-base font-semibold">AI Executive Review Summary</h2>
          </div>

          <div className="flex items-center gap-2">
            <Badge className="bg-red-500/15 text-red-400 border-red-500/30">
              {criticalCount} Critical
            </Badge>
            <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30">
              {warningCount} Warnings
            </Badge>
            <Badge variant="outline" className="text-muted-foreground">
              {suggestionCount} Suggestions
            </Badge>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-muted-foreground">
          {review.summary || "Review completed without aggregated summary notes."}
        </p>
      </div>

      {/* Findings Section */}
      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight">
              Detailed Findings ({filteredFindings.length})
            </h2>
            <p className="text-xs text-muted-foreground">
              Synthesized by Gemini Pro from Multi-Agent Review inspections.
            </p>
          </div>

          <div className="flex items-center gap-1.5">
            {[
              { label: "All", value: "all", count: findings.length },
              { label: "Critical", value: "critical", count: criticalCount },
              { label: "Warnings", value: "warning", count: warningCount },
              { label: "Suggestions", value: "suggestion", count: suggestionCount },
            ].map((tab) => (
              <Button
                key={tab.value}
                variant={selectedSeverity === tab.value ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setSelectedSeverity(tab.value)}
                className="text-xs gap-1.5"
              >
                {tab.label}
                <span className="text-[10px] opacity-70">({tab.count})</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Findings List */}
        <div className="grid gap-4">
          {filteredFindings.map((finding, idx) => {
            const isCritical = finding.severity === "critical";
            const isWarning = finding.severity === "warning";

            return (
              <div
                key={finding.id || idx}
                className={`rounded-xl border p-5 space-y-3 transition-all ${
                  isCritical
                    ? "border-red-500/40 bg-red-950/10"
                    : isWarning
                    ? "border-amber-500/40 bg-amber-950/10"
                    : "border-border/70 bg-card/60"
                }`}
              >
                {/* Finding Header */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {isCritical ? (
                      <Badge className="bg-red-500/20 text-red-400 border-red-500/40 gap-1 text-xs">
                        <ShieldAlertIcon className="h-3.5 w-3.5" />
                        Critical
                      </Badge>
                    ) : isWarning ? (
                      <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/40 gap-1 text-xs">
                        <AlertTriangleIcon className="h-3.5 w-3.5" />
                        Warning
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-muted-foreground gap-1 text-xs">
                        <LightbulbIcon className="h-3.5 w-3.5 text-emerald-400" />
                        Suggestion
                      </Badge>
                    )}

                    <Badge variant="secondary" className="font-mono text-[11px] bg-accent/60">
                      {finding.category}
                    </Badge>
                    {finding.agent_name && (
                      <span className="text-xs text-muted-foreground">
                        via <strong className="text-foreground capitalize">{finding.agent_name}</strong> agent
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-1.5 text-xs font-mono text-muted-foreground">
                    <FileCodeIcon className="h-3.5 w-3.5" />
                    <span>
                      {finding.file_path}:{finding.start_line}
                    </span>
                  </div>
                </div>

                {/* Finding Title & Description */}
                <div>
                  <h3 className="font-semibold text-foreground text-sm">{finding.title}</h3>
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                    {finding.description}
                  </p>
                </div>

                {/* Actionable Suggestion */}
                {finding.suggestion && (
                  <div className="rounded-lg bg-accent/30 p-3 border border-border/50 space-y-1">
                    <span className="text-xs font-semibold text-violet-400 flex items-center gap-1">
                      <LightbulbIcon className="h-3.5 w-3.5" />
                      Recommended Fix:
                    </span>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {finding.suggestion}
                    </p>
                  </div>
                )}
              </div>
            );
          })}

          {filteredFindings.length === 0 && (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-8 text-center text-muted-foreground text-xs">
              No findings matching the selected severity filter.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
