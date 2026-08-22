"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
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
  SparkleIcon,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api, type ReviewResponse } from "@/lib/api";

export default function ReviewsPage() {
  const { getToken } = useAuth();
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  useEffect(() => {
    let isMounted = true;

    async function fetchReviews() {
      try {
        const token = await getToken();
        const data = await api.getReviews(50, 0, token);
        if (isMounted) {
          setReviews(data);
        }
      } catch (err) {
        console.error("Failed to load reviews:", err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    fetchReviews();

    return () => {
      isMounted = false;
    };
  }, [getToken]);

  const loadReviews = async () => {
    try {
      setIsRefreshing(true);
      const token = await getToken();
      const data = await api.getReviews(50, 0, token);
      setReviews(data);
    } catch (err) {
      console.error("Failed to load reviews:", err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleSeedDemoData = async () => {
    try {
      setIsSeeding(true);
      const token = await getToken();
      await api.seedDemoData(token);
      await loadReviews();
    } catch (err) {
      console.error("Failed to seed demo data:", err);
    } finally {
      setIsSeeding(false);
    }
  };

  const filteredReviews = reviews.filter((rev) => {
    const title = rev.pull_request?.title || "";
    const repo = rev.pull_request?.repository?.full_name || "";
    const author = rev.pull_request?.author || "";

    const matchesSearch =
      title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      repo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      author.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || rev.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">AI Code Reviews</h1>
            <Badge variant="secondary" className="gap-1 text-xs bg-accent/60">
              <SparklesIcon className="h-3 w-3 text-violet-400" />
              Live Feed
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Automated multi-agent inspection history across your organization&apos;s repositories.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {reviews.length === 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSeedDemoData}
              disabled={isSeeding}
              className="gap-2 text-xs border-violet-500/40 text-violet-300 hover:bg-violet-950/20"
            >
              <SparkleIcon className={`h-3.5 w-3.5 ${isSeeding ? "animate-spin" : ""}`} />
              {isSeeding ? "Seeding..." : "Seed Demo Reviews"}
            </Button>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={loadReviews}
            disabled={isRefreshing}
            className="gap-2 text-xs"
          >
            <RefreshCwIcon className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
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
            className="pl-9 bg-card border-border/80 text-xs"
          />
        </div>

        <div className="flex items-center gap-2">
          {["all", "completed", "in_progress", "pending", "failed"].map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setStatusFilter(status)}
              className="capitalize text-xs"
            >
              {status.replace("_", " ")}
            </Button>
          ))}
        </div>
      </div>

      {/* Reviews List */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-sm text-muted-foreground">
          <RefreshCwIcon className="h-5 w-5 animate-spin mr-2" />
          Loading reviews from database...
        </div>
      ) : filteredReviews.length > 0 ? (
        <div className="grid gap-4">
          {filteredReviews.map((review) => {
            const isProcessing =
              review.status === "in_progress" || review.status === "pending";

            return (
              <Link
                key={review.id}
                href={`/reviews/${review.id}`}
                className="group flex flex-col justify-between gap-4 rounded-xl border border-border/70 bg-card/60 p-5 transition-all hover:border-violet-500/50 hover:bg-card/90 hover:shadow-lg hover:shadow-violet-950/20 md:flex-row md:items-center"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-mono text-muted-foreground">
                      {review.pull_request?.repository?.full_name || "Repository"}
                    </span>
                    <Badge variant="outline" className="text-xs font-mono font-normal">
                      #{review.pull_request?.number || 1}
                    </Badge>
                    <Badge
                      variant="secondary"
                      className="text-xs capitalize bg-accent/60"
                    >
                      {review.risk_level} risk
                    </Badge>
                  </div>

                  <h3 className="font-semibold text-foreground group-hover:text-violet-400 transition-colors text-sm">
                    {review.pull_request?.title || "Pull Request Review"}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground font-mono">
                    <span>
                      Author:{" "}
                      <strong className="text-foreground">
                        {review.pull_request?.author || "Developer"}
                      </strong>
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <ClockIcon className="h-3.5 w-3.5" />
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                    {review.duration_ms && review.duration_ms > 0 ? (
                      <>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <ZapIcon className="h-3.5 w-3.5 text-amber-400" />
                          {(review.duration_ms / 1000).toFixed(1)}s
                        </span>
                      </>
                    ) : null}
                  </div>
                </div>

                {/* Status & Severity Badges */}
                <div className="flex flex-wrap items-center gap-2">
                  {isProcessing ? (
                    <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1.5 py-1 px-3 text-xs">
                      <SparklesIcon className="h-3.5 w-3.5 animate-spin" />
                      Analyzing...
                    </Badge>
                  ) : (
                    <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 gap-1.5 py-1 px-3 text-xs">
                      <CheckCircle2Icon className="h-3.5 w-3.5" />
                      Reviewed
                    </Badge>
                  )}

                  {review.critical_count > 0 && (
                    <Badge className="bg-red-500/15 text-red-400 border-red-500/30 gap-1 text-xs">
                      <ShieldAlertIcon className="h-3 w-3" />
                      {review.critical_count}
                    </Badge>
                  )}

                  {review.warning_count > 0 && (
                    <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1 text-xs">
                      <AlertTriangleIcon className="h-3 w-3" />
                      {review.warning_count}
                    </Badge>
                  )}

                  {review.suggestion_count > 0 && (
                    <Badge variant="outline" className="text-muted-foreground text-xs">
                      {review.suggestion_count} suggestions
                    </Badge>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
          <GitPullRequestIcon className="h-10 w-10 text-muted-foreground mb-3" />
          <h3 className="text-base font-semibold">No reviews found</h3>
          <p className="mt-1 text-xs text-muted-foreground max-w-sm">
            Once a pull request is opened or updated in a connected repository, the AI multi-agent review pipeline will automatically analyze the diff.
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
                Manage Repositories
              </Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
