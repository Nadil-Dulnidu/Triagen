"use client";

import Link from "next/link";
import { useState } from "react";
import {
  GitPullRequestIcon,
  SearchIcon,
  ShieldAlertIcon,
  ClockIcon,
  ZapIcon,
  CheckCircle2Icon,
  AlertTriangleIcon,
  SparklesIcon,
  RefreshCwIcon,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// Example mock reviews for showcase and testing
const INITIAL_REVIEWS = [
  {
    id: "rev-101",
    pr_number: 42,
    title: "Implement JWT verification middleware & session validation",
    repo: "acme-corp/api-gateway",
    author: "sarah-dev",
    status: "completed",
    triage_classification: "critical",
    critical_count: 1,
    warning_count: 2,
    suggestion_count: 3,
    duration_ms: 2450,
    created_at: "10 minutes ago",
  },
  {
    id: "rev-102",
    pr_number: 18,
    title: "Refactor database connection pool and retry policies",
    repo: "acme-corp/core-service",
    author: "alex-chen",
    status: "completed",
    triage_classification: "medium",
    critical_count: 0,
    warning_count: 1,
    suggestion_count: 4,
    duration_ms: 1890,
    created_at: "1 hour ago",
  },
  {
    id: "rev-103",
    pr_number: 89,
    title: "Add Stripe webhook signature verification and checkout flow",
    repo: "acme-corp/billing-service",
    author: "jordan-m",
    status: "triaging",
    triage_classification: "large",
    critical_count: 0,
    warning_count: 0,
    suggestion_count: 0,
    duration_ms: 0,
    created_at: "Just now",
  },
];

export default function ReviewsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredReviews = INITIAL_REVIEWS.filter((rev) => {
    const matchesSearch =
      rev.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rev.repo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rev.author.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || rev.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Code Reviews</h1>
          <p className="text-sm text-muted-foreground">
            Automated multi-agent inspection history across your organization&apos;s repositories.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <RefreshCwIcon className="h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:w-80">
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by title, repo, or author..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 bg-card border-border/80"
          />
        </div>

        <div className="flex items-center gap-2">
          {["all", "completed", "triaging", "failed"].map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setStatusFilter(status)}
              className="capitalize text-xs"
            >
              {status}
            </Button>
          ))}
        </div>
      </div>

      {/* Reviews List */}
      <div className="grid gap-4">
        {filteredReviews.map((review) => {
          const isProcessing =
            review.status === "triaging" || review.status === "reviewing";

          return (
            <Link
              key={review.id}
              href={`/reviews/${review.id}`}
              className="group flex flex-col justify-between gap-4 rounded-xl border border-border/70 bg-card/60 p-5 transition-all hover:border-violet-500/50 hover:bg-card/90 hover:shadow-lg hover:shadow-violet-950/20 md:flex-row md:items-center"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-mono text-muted-foreground">
                    {review.repo}
                  </span>
                  <Badge variant="outline" className="text-xs font-mono font-normal">
                    #{review.pr_number}
                  </Badge>
                  {review.triage_classification && (
                    <Badge
                      variant="secondary"
                      className="text-xs capitalize bg-accent/60"
                    >
                      {review.triage_classification}
                    </Badge>
                  )}
                </div>

                <h3 className="font-semibold text-foreground group-hover:text-violet-400 transition-colors">
                  {review.title}
                </h3>

                <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                  <span>Author: <strong className="text-foreground">{review.author}</strong></span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <ClockIcon className="h-3.5 w-3.5" />
                    {review.created_at}
                  </span>
                  {review.duration_ms > 0 && (
                    <>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <ZapIcon className="h-3.5 w-3.5 text-amber-400" />
                        {(review.duration_ms / 1000).toFixed(1)}s
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Status & Severity Badges */}
              <div className="flex flex-wrap items-center gap-3">
                {isProcessing ? (
                  <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1.5 py-1 px-3">
                    <SparklesIcon className="h-3.5 w-3.5 animate-spin" />
                    Agents Analyzing...
                  </Badge>
                ) : (
                  <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 gap-1.5 py-1 px-3">
                    <CheckCircle2Icon className="h-3.5 w-3.5" />
                    Reviewed
                  </Badge>
                )}

                {review.critical_count > 0 && (
                  <Badge className="bg-red-500/15 text-red-400 border-red-500/30 gap-1">
                    <ShieldAlertIcon className="h-3 w-3" />
                    {review.critical_count} Critical
                  </Badge>
                )}

                {review.warning_count > 0 && (
                  <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1">
                    <AlertTriangleIcon className="h-3 w-3" />
                    {review.warning_count} Warning
                  </Badge>
                )}

                {review.suggestion_count > 0 && (
                  <Badge variant="outline" className="text-muted-foreground gap-1">
                    {review.suggestion_count} Suggestions
                  </Badge>
                )}
              </div>
            </Link>
          );
        })}

        {filteredReviews.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
            <GitPullRequestIcon className="h-10 w-10 text-muted-foreground mb-3" />
            <h3 className="text-base font-semibold">No reviews found</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Try adjusting your search query or status filter.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
