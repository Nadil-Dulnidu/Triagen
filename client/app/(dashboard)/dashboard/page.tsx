export default function DashboardPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Welcome to PullSense. An overview of your AI-powered code reviews.
        </p>
      </div>

      {/* Overview cards will be added here */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <DashboardCard
          title="Total Reviews"
          value="—"
          description="Reviews completed"
        />
        <DashboardCard
          title="Active Repositories"
          value="—"
          description="Connected repos"
        />
        <DashboardCard
          title="Findings"
          value="—"
          description="Issues identified"
        />
        <DashboardCard
          title="Avg. Review Time"
          value="—"
          description="Processing time"
        />
      </div>
    </div>
  );
}

function DashboardCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
