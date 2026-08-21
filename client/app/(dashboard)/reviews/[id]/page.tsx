"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeftIcon,
  ShieldAlertIcon,
  AlertTriangleIcon,
  LightbulbIcon,
  ClockIcon,
  ZapIcon,
  BrainIcon,
  CheckCircle2Icon,
  SparklesIcon,
  ExternalLinkIcon,
  RefreshCwIcon,
  GitBranchIcon,
  FileCodeIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ReviewFinding {
  id: string;
  agent_name: string;
  severity: "critical" | "warning" | "suggestion" | "info";
  category: string;
  file_path: string;
  start_line: number;
  end_line?: number;
  title: string;
  description: string;
  suggestion?: string;
  code_snippet?: string;
}

interface AgentTelemetry {
  agent_name: string;
  model_used: string;
  duration_ms: number;
  input_tokens: number;
  output_tokens: number;
  status: string;
}

// Sample review detailed data for visual demonstration
const SAMPLE_REVIEW = {
  id: "rev-101",
  pr_number: 42,
  title: "Implement JWT verification middleware & session validation",
  repo: "acme-corp/api-gateway",
  base_branch: "main",
  head_branch: "feature/jwt-auth",
  author: "sarah-dev",
  head_sha: "7f8b9e1",
  status: "completed",
  triage_classification: "critical",
  risk_score: 8,
  summary:
    "This pull request introduces a new JWT verification layer for protected HTTP endpoints. While the general architectural structure follows clean separation of concerns, the implementation contains a critical security vulnerability: token signature verification is disabled (`verify=False`), allowing arbitrary token forgery. Additionally, sensitive token payloads are exposed to application debug logs.",
  duration_ms: 2450,
  total_tokens: 3420,
  created_at: "10 minutes ago",
  findings: [
    {
      id: "f-1",
      agent_name: "security",
      severity: "critical",
      category: "auth_vulnerability",
      file_path: "src/middleware/auth.py",
      start_line: 34,
      end_line: 36,
      title: "JWT Signature Verification Disabled in Production Path",
      description:
        "The JWT decoding method is invoked with `verify_signature=False`. This permits any client to construct an arbitrary unsigned token containing claims such as `role: admin` or custom tenant IDs without detection.",
      suggestion:
        "Always enforce signature validation against the cached JWKS public keys or HMAC secret. Ensure algorithm restrictions are explicitly specified (e.g. `algorithms=['RS256']`).",
      code_snippet:
        "- decoded = jwt.decode(token, options={'verify_signature': False})\n+ decoded = jwt.decode(token, key=jwks_client.get_signing_key_from_jwt(token).key, algorithms=['RS256'])",
    },
    {
      id: "f-2",
      agent_name: "security",
      severity: "warning",
      category: "data_exposure",
      file_path: "src/middleware/auth.py",
      start_line: 52,
      end_line: 54,
      title: "Full Raw Authorization Header Emitted to Application Logs",
      description:
        "Logging the entire Bearer token header in debug mode risks leaking valid user credentials into log indexing systems (e.g. Datadog / CloudWatch), which are accessible to wider engineering teams.",
      suggestion:
        "Sanitize or redact the token value prior to logging. Log only the token subject or request ID.",
      code_snippet:
        "- logger.debug('auth_token_received', raw_header=auth_header)\n+ logger.debug('auth_token_verified', user_id=decoded.get('sub'))",
    },
    {
      id: "f-3",
      agent_name: "style",
      severity: "suggestion",
      category: "error_handling",
      file_path: "src/middleware/auth.py",
      start_line: 68,
      end_line: 75,
      title: "Generic Exception Handler Masks Underlying Cryptography Failures",
      description:
        "Catching `Exception` broadly prevents distinguishing between expired tokens, invalid signatures, and internal server faults, leading to confusing 500 error responses for expired clients.",
      suggestion:
        "Catch specific exceptions (`jwt.ExpiredSignatureError`, `jwt.InvalidTokenError`) and map them directly to 401 Unauthorized responses.",
    },
  ] as ReviewFinding[],
  agent_runs: [
    {
      agent_name: "Triage Agent",
      model_used: "gemini-2.5-flash",
      duration_ms: 380,
      input_tokens: 650,
      output_tokens: 120,
      status: "completed",
    },
    {
      agent_name: "Security Agent",
      model_used: "gemini-2.5-flash",
      duration_ms: 1120,
      input_tokens: 1450,
      output_tokens: 430,
      status: "completed",
    },
    {
      agent_name: "Style Agent",
      model_used: "gemini-2.5-flash",
      duration_ms: 890,
      input_tokens: 1200,
      output_tokens: 310,
      status: "completed",
    },
    {
      agent_name: "Aggregator Agent",
      model_used: "gemini-2.5-pro",
      duration_ms: 960,
      input_tokens: 1980,
      output_tokens: 520,
      status: "completed",
    },
  ] as AgentTelemetry[],
};

export default function ReviewDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const reviewId = resolvedParams.id;
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [streamStatus, setStreamStatus] = useState<string>("Review Completed");
  const [isLive, setIsLive] = useState<boolean>(false);

  // Set up SSE listener for live review progress
  useEffect(() => {
    const sseUrl = `http://localhost:8000/api/v1/reviews/${reviewId}/stream`;
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
      eventSource.addEventListener("review.aggregating", () => {
        setStreamStatus("Aggregator Agent synthesizing & prioritizing findings...");
      });
      eventSource.addEventListener("review.completed", () => {
        setStreamStatus("Review Completed & Posted to GitHub");
        setIsLive(false);
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
  }, [reviewId]);

  const review = SAMPLE_REVIEW;

  const filteredFindings = review.findings.filter((f) => {
    if (selectedSeverity === "all") return true;
    return f.severity === selectedSeverity;
  });

  const criticalCount = review.findings.filter((f) => f.severity === "critical").length;
  const warningCount = review.findings.filter((f) => f.severity === "warning").length;
  const suggestionCount = review.findings.filter((f) => f.severity === "suggestion").length;

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
              <span className="text-xs font-mono text-muted-foreground">{review.repo}</span>
              <Badge variant="outline" className="text-xs font-mono">#{review.pr_number}</Badge>
              {isLive && (
                <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/40 gap-1.5 animate-pulse">
                  <SparklesIcon className="h-3 w-3" />
                  Live SSE
                </Badge>
              )}
            </div>
            <h1 className="text-xl font-bold tracking-tight mt-0.5">{review.title}</h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2 text-xs">
            <RefreshCwIcon className="h-3.5 w-3.5" />
            Re-run Review
          </Button>
          <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-white gap-2 text-xs">
            <ExternalLinkIcon className="h-3.5 w-3.5" />
            View on GitHub
          </Button>
        </div>
      </div>

      {/* Live Progress Banner (if active) */}
      {isLive && (
        <div className="rounded-xl border border-violet-500/30 bg-violet-950/20 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SparklesIcon className="h-5 w-5 text-violet-400 animate-spin" />
            <div>
              <span className="text-sm font-semibold text-foreground">Multi-Agent Review in Progress</span>
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
              {review.triage_classification}
            </Badge>
            <span className="text-xs font-mono text-muted-foreground">Risk {review.risk_score}/10</span>
          </div>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Branches</span>
          <div className="flex items-center gap-1.5 text-xs font-mono text-foreground truncate">
            <GitBranchIcon className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
            <span className="text-violet-400">{review.base_branch}</span>
            <span>←</span>
            <span>{review.head_branch}</span>
          </div>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Execution Latency</span>
          <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
            <ZapIcon className="h-3.5 w-3.5 text-amber-400" />
            <span>{(review.duration_ms / 1000).toFixed(2)}s</span>
            <span className="text-muted-foreground font-normal">({review.total_tokens.toLocaleString()} tokens)</span>
          </div>
        </div>

        <div className="rounded-xl border border-border/70 bg-card/60 p-4 space-y-1">
          <span className="text-xs text-muted-foreground">Author & Status</span>
          <div className="flex items-center gap-2 text-xs font-medium text-foreground">
            <span>{review.author}</span>
            <span>•</span>
            <span className="flex items-center gap-1 text-emerald-400">
              <CheckCircle2Icon className="h-3.5 w-3.5" />
              Completed
            </span>
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
          {review.summary}
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
              Synthesized by Gemini Pro from Security & Style agent inspections.
            </p>
          </div>

          <div className="flex items-center gap-1.5">
            {[
              { label: "All", value: "all", count: review.findings.length },
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
          {filteredFindings.map((finding) => {
            const isCritical = finding.severity === "critical";
            const isWarning = finding.severity === "warning";

            return (
              <div
                key={finding.id}
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
                    <span className="text-xs text-muted-foreground">
                      via <strong className="text-foreground capitalize">{finding.agent_name}</strong> agent
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs font-mono text-muted-foreground">
                    <FileCodeIcon className="h-3.5 w-3.5" />
                    <span>{finding.file_path}:{finding.start_line}</span>
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

                {/* Code Snippet Diff */}
                {finding.code_snippet && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-mono text-muted-foreground">Diff Suggestion:</span>
                    <pre className="rounded-lg bg-black/50 p-3 text-xs font-mono text-emerald-400 overflow-x-auto border border-border/40">
                      <code>{finding.code_snippet}</code>
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Agent Telemetry Breakdown */}
      <div className="rounded-xl border border-border/70 bg-card/40 p-5 space-y-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <ClockIcon className="h-4 w-4 text-violet-400" />
          Agent Execution & Token Telemetry
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border/60 text-muted-foreground">
                <th className="pb-2 font-medium">Agent</th>
                <th className="pb-2 font-medium">Model</th>
                <th className="pb-2 font-medium">Duration</th>
                <th className="pb-2 font-medium">Input Tokens</th>
                <th className="pb-2 font-medium">Output Tokens</th>
                <th className="pb-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 font-mono">
              {review.agent_runs.map((run, idx) => (
                <tr key={idx} className="text-foreground">
                  <td className="py-2.5 font-sans font-medium">{run.agent_name}</td>
                  <td className="py-2.5 text-muted-foreground">{run.model_used}</td>
                  <td className="py-2.5">{run.duration_ms}ms</td>
                  <td className="py-2.5 text-muted-foreground">{run.input_tokens.toLocaleString()}</td>
                  <td className="py-2.5 text-muted-foreground">{run.output_tokens.toLocaleString()}</td>
                  <td className="py-2.5">
                    <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-[10px] capitalize">
                      {run.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
