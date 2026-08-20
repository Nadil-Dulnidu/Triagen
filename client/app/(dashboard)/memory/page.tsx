import { BrainIcon, PlusIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function MemoryPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Memory</h1>
          <p className="text-sm text-muted-foreground">
            Manage organization policies, repository conventions, and developer preferences remembered by the AI.
          </p>
        </div>
        <Button className="bg-violet-600 hover:bg-violet-700 text-white gap-2">
          <PlusIcon className="h-4 w-4" />
          Add Memory Rule
        </Button>
      </div>

      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-muted-foreground mb-4">
          <BrainIcon className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold">No custom memory rules configured</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Define coding standards or architectural guidelines that the AI agents should always enforce during reviews.
        </p>
      </div>
    </div>
  );
}
