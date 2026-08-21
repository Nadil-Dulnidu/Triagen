"use client";

import { SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";

export function DashboardHeader({ title }: { title?: string }) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border/80 bg-background/50 px-4 md:px-6 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <SidebarTrigger className="h-8 w-8 text-muted-foreground hover:text-foreground" />
        <Separator orientation="vertical" className="h-4 hidden sm:block" />
        {title && <h2 className="text-lg md:text-xl font-semibold tracking-tight">{title}</h2>}
      </div>

      <div className="flex items-center gap-3">
        <div className="relative w-56 sm:w-72 md:w-80">
          <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search reviews, repos, authors..."
            className="h-9 pl-9 bg-accent/30 border-border/60 text-sm focus-visible:ring-violet-500 rounded-lg"
          />
        </div>
      </div>
    </header>
  );
}

