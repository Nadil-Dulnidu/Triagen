import { GitPullRequestIcon } from "lucide-react";

export default function ReviewsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reviews</h1>
        <p className="text-sm text-muted-foreground">
          View history, AI findings, and agent execution breakdown for all PR reviews.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-muted-foreground mb-4">
          <GitPullRequestIcon className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold">No reviews yet</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          When a PR is opened or updated on a connected repository, PullSense will automatically run reviews and display findings here.
        </p>
      </div>
    </div>
  );
}
