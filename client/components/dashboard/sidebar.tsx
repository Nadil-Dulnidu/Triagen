"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboardIcon, GitPullRequestIcon, FolderGit2Icon, BarChart3Icon, BrainIcon, SettingsIcon, Building2Icon } from "lucide-react";
import { OrganizationSwitcher, UserButton, useUser, useOrganization } from "@clerk/nextjs";
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail, useSidebar } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
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
  const { user } = useUser();
  const { organization } = useOrganization();
  const { state } = useSidebar();

  const userDisplayName = user?.fullName || user?.username || (user?.firstName ? `${user.firstName} ${user.lastName || ""}`.trim() : null) || "Developer";

  const userEmail = user?.primaryEmailAddress?.emailAddress || user?.emailAddresses?.[0]?.emailAddress || "";

  const orgDisplayName = organization?.name || "Personal Workspace";

  return (
    <Sidebar collapsible="icon" className="border-r border-border/80 bg-sidebar">
      {/* Brand Header */}
      <SidebarHeader className="border-b border-border/60 p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              render={<Link href="/dashboard" />}
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground hover:bg-sidebar-accent/60"
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 p-1 shadow-md shadow-violet-600/30 text-sidebar-primary-foreground shrink-0">
                <Image
                  src="/logo.png"
                  alt="Triagen Logo"
                  width={22}
                  height={22}
                  className="object-contain"
                  priority
                />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
                <div className="flex items-center gap-1.5">
                  <span className="truncate font-bold text-base tracking-tight text-foreground">
                    Triagen
                  </span>
                  <Badge
                    variant="outline"
                    className="h-4 border-violet-500/40 bg-violet-950/40 px-1 text-[9px] font-semibold text-violet-300"
                  >
                    AI
                  </Badge>
                </div>
                <span className="truncate text-[10px] text-muted-foreground">
                  Autonomous PR Triage
                </span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      {/* Navigation */}
      <SidebarContent className="p-2">
        <SidebarMenu className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <SidebarMenuItem key={item.name}>
                <SidebarMenuButton
                  render={<Link href={item.href} />}
                  isActive={isActive}
                  tooltip={item.name}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all",
                    isActive ? "bg-violet-600/15 text-violet-400 font-semibold shadow-xs" : "text-muted-foreground hover:bg-sidebar-accent/70 hover:text-sidebar-accent-foreground",
                  )}
                >
                  <Icon className={cn("h-4 w-4 shrink-0", isActive ? "text-violet-400" : "text-muted-foreground")} />
                  <span className="group-data-[collapsible=icon]:hidden">{item.name}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarContent>

      {/* Footer: Organization Switcher above User Profile */}
      <SidebarFooter className="border-t border-border/60 p-3 space-y-3 bg-sidebar/50">
        {/* Organization Switcher Section */}
        <div className="w-full flex flex-col gap-1.5 group-data-[collapsible=icon]:items-center">
          <div className="w-full">
            <OrganizationSwitcher
              hidePersonal={false}
              afterCreateOrganizationUrl="/dashboard"
              afterLeaveOrganizationUrl="/dashboard"
              afterSelectOrganizationUrl="/dashboard"
              appearance={{
                elements: {
                  rootBox: "w-full flex group-data-[collapsible=icon]:justify-center",
                  organizationSwitcherTrigger:
                    "w-full justify-between bg-sidebar-accent/60 hover:bg-sidebar-accent border border-border/60 rounded-lg px-2.5 py-1.5 text-xs text-foreground font-medium transition-colors shadow-2xs group-data-[collapsible=icon]:size-8! group-data-[collapsible=icon]:p-0! group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:border-none group-data-[collapsible=icon]:bg-transparent",
                  organizationPreview: "flex items-center gap-2 overflow-hidden",
                  organizationPreviewAvatarBox: "size-6 shrink-0 rounded-md ring-1 ring-violet-500/20 group-data-[collapsible=icon]:size-6",
                  organizationPreviewTextContainer: "group-data-[collapsible=icon]:hidden text-left flex-1 min-w-0",
                  organizationPreviewMainIdentifier: "text-xs font-medium text-foreground truncate group-data-[collapsible=icon]:hidden",
                  organizationPreviewSecondaryIdentifier: "text-[10px] text-muted-foreground truncate group-data-[collapsible=icon]:hidden",
                  organizationSwitcherTriggerIcon: "group-data-[collapsible=icon]:hidden h-4 w-4 shrink-0 text-muted-foreground ml-auto",
                },
              }}
            />
          </div>
        </div>

        <Separator className="opacity-60 group-data-[collapsible=icon]:hidden" />

        {/* User Profile Section */}
        <div className="flex items-center gap-3 px-1 py-1 rounded-lg hover:bg-sidebar-accent/40 transition-colors group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:p-0">
          <div className="shrink-0 flex items-center justify-center">
            <UserButton
              appearance={{
                elements: {
                  userButtonAvatarBox: "h-8 w-8 ring-1 ring-violet-500/30 shadow-xs",
                },
              }}
            />
          </div>
          <div className="flex flex-col min-w-0 flex-1 overflow-hidden group-data-[collapsible=icon]:hidden">
            <span className="truncate text-xs font-semibold text-foreground leading-tight">{userDisplayName}</span>
            <span className="truncate text-[11px] text-muted-foreground leading-tight" title={userEmail}>
              {userEmail}
            </span>
          </div>
        </div>
      </SidebarFooter>

      {/* Resize / Collapse Handle */}
      <SidebarRail />
    </Sidebar>
  );
}
