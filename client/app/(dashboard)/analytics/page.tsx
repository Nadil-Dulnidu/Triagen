import { BarChart3Icon } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Track review throughput, agent accuracy, token consumption, and developer insights.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-muted-foreground mb-4">
          <BarChart3Icon className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold">Analytics will appear here</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          As reviews are performed across your repositories, historical metrics and trends will be computed automatically.
        </p>
      </div>
    </div>
  );
}
