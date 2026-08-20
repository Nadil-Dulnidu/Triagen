import { FolderGit2Icon, PlusIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function RepositoriesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Repositories</h1>
          <p className="text-sm text-muted-foreground">
            Manage your connected GitHub repositories and AI review configurations.
          </p>
        </div>
        <Button className="bg-violet-600 hover:bg-violet-700 text-white gap-2">
          <PlusIcon className="h-4 w-4" />
          Connect Repository
        </Button>
      </div>

      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-muted-foreground mb-4">
          <FolderGit2Icon className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold">No repositories connected yet</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Install the PullSense GitHub App to start automated AI code reviews on your pull requests.
        </p>
        <Button variant="outline" className="mt-6">
          Install GitHub App
        </Button>
      </div>
    </div>
  );
}
