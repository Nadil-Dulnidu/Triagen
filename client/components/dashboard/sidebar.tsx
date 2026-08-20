"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboardIcon,
  GitPullRequestIcon,
  FolderGit2Icon,
  BarChart3Icon,
  BrainIcon,
  SettingsIcon,
  ShieldCheckIcon,
} from "lucide-react";
import { OrganizationSwitcher, UserButton } from "@clerk/nextjs";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboardIcon },
  { name: "Repositories", href: "/repositories", icon: FolderGit2Icon },
  { name: "Reviews", href: "/reviews", icon: GitPullRequestIcon },
  { name: "Analytics", href: "/analytics", icon: BarChart3Icon },
  { name: "Memory", href: "/memory", icon: BrainIcon },
  { name: "Settings", href: "/settings", icon: SettingsIcon },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-border bg-card/60 backdrop-blur-md">
      {/* Brand & Organization */}
      <div className="flex flex-col gap-3 border-b border-border p-4">
        <Link href="/dashboard" className="flex items-center gap-2.5 px-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-600 shadow-md shadow-violet-600/30">
            <ShieldCheckIcon className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold text-lg tracking-tight">PullSense</span>
        </Link>
        <div className="pt-1">
          <OrganizationSwitcher
            appearance={{
              elements: {
                rootBox: "w-full",
                organizationSwitcherTrigger:
                  "w-full justify-between bg-accent/40 hover:bg-accent/80 border border-border/60 rounded-lg px-3 py-2 text-sm text-foreground",
              },
            }}
          />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-3">
        {navigation.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-violet-600/15 text-violet-400 font-semibold"
                  : "text-muted-foreground hover:bg-accent/60 hover:text-foreground"
              )}
            >
              <Icon
                className={cn(
                  "h-4 w-4",
                  isActive ? "text-violet-400" : "text-muted-foreground"
                )}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User profile footer */}
      <div className="flex items-center justify-between border-t border-border p-4">
        <div className="flex items-center gap-3">
          <UserButton
            appearance={{
              elements: {
                userButtonAvatarBox: "h-8 w-8",
              },
            }}
          />
          <div className="flex flex-col text-xs">
            <span className="font-medium text-foreground">My Account</span>
            <span className="text-muted-foreground">Manage profile</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
