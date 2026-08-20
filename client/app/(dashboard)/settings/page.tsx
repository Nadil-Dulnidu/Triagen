export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Configure organization preferences, webhook secrets, rate limits, and API keys.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-card p-6">
        <h3 className="text-base font-semibold">General Settings</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Organization configuration and automated review defaults.
        </p>
      </div>
    </div>
  );
}
