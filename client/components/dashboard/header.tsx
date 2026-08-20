"use client";

import { BellIcon, SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function DashboardHeader({ title }: { title?: string }) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border/80 bg-background/50 px-6 backdrop-blur-md">
      <div className="flex items-center gap-4">
        {title && <h2 className="text-xl font-semibold">{title}</h2>}
      </div>

      <div className="flex items-center gap-3">
        <div className="relative w-64 md:w-80">
          <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search reviews, repos, authors..."
            className="h-9 pl-9 bg-accent/30 border-border/60 text-sm focus-visible:ring-violet-500"
          />
        </div>

        <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
          <BellIcon className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-violet-500" />
        </Button>
      </div>
    </header>
  );
}
