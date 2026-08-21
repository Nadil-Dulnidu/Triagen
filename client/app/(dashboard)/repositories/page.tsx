"use client";

import { useState } from "react";
import {
  FolderGit2Icon,
  PlusIcon,
  SearchIcon,
  SlidersHorizontalIcon,
  Trash2Icon,
  ShieldIcon,
  PaintbrushIcon,
  TestTubeIcon,
  ZapIcon,
  XIcon,
  GitBranchIcon,
  SparklesIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface RepoItem {
  id: string;
  github_repo_id: number;
  full_name: string;
  name: string;
  default_branch: string;
  language: string;
  is_active: boolean;
  last_review_at: string;
  config: {
    security_agent_enabled: boolean;
    style_agent_enabled: boolean;
    test_coverage_agent_enabled: boolean;
    auto_review_enabled: boolean;
    ignored_paths: string[];
  };
}

const INITIAL_REPOSITORIES: RepoItem[] = [
  {
    id: "r-1",
    github_repo_id: 101,
    full_name: "acme-corp/api-gateway",
    name: "api-gateway",
    default_branch: "main",
    language: "Python",
    is_active: true,
    last_review_at: "10 minutes ago",
    config: {
      security_agent_enabled: true,
      style_agent_enabled: true,
      test_coverage_agent_enabled: true,
      auto_review_enabled: true,
      ignored_paths: ["docs/**", "*.md", "tests/fixtures/**"],
    },
  },
  {
    id: "r-2",
    github_repo_id: 102,
    full_name: "acme-corp/core-service",
    name: "core-service",
    default_branch: "main",
    language: "TypeScript",
    is_active: true,
    last_review_at: "1 hour ago",
    config: {
      security_agent_enabled: true,
      style_agent_enabled: true,
      test_coverage_agent_enabled: true,
      auto_review_enabled: true,
      ignored_paths: ["dist/**", "node_modules/**"],
    },
  },
  {
    id: "r-3",
    github_repo_id: 103,
    full_name: "acme-corp/billing-service",
    name: "billing-service",
    default_branch: "main",
    language: "Go",
    is_active: true,
    last_review_at: "3 hours ago",
    config: {
      security_agent_enabled: true,
      style_agent_enabled: false,
      test_coverage_agent_enabled: true,
      auto_review_enabled: true,
      ignored_paths: ["vendor/**"],
    },
  },
  {
    id: "r-4",
    github_repo_id: 104,
    full_name: "acme-corp/frontend-app",
    name: "frontend-app",
    default_branch: "main",
    language: "TypeScript",
    is_active: true,
    last_review_at: "Yesterday",
    config: {
      security_agent_enabled: true,
      style_agent_enabled: true,
      test_coverage_agent_enabled: false,
      auto_review_enabled: true,
      ignored_paths: [".next/**", "public/**"],
    },
  },
];

const AVAILABLE_GITHUB_REPOS = [
  { id: 201, name: "acme-corp/auth-service", language: "Rust" },
  { id: 202, name: "acme-corp/data-pipeline", language: "Python" },
  { id: 203, name: "acme-corp/infra-terraform", language: "HCL" },
];

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<RepoItem[]>(INITIAL_REPOSITORIES);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRepoForConfig, setSelectedRepoForConfig] = useState<RepoItem | null>(null);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [selectedGithubIds, setSelectedGithubIds] = useState<number[]>([]);

  const filteredRepos = repositories.filter((r) =>
    r.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleAgent = (agentKey: keyof RepoItem["config"]) => {
    if (!selectedRepoForConfig) return;
    const updated = {
      ...selectedRepoForConfig,
      config: {
        ...selectedRepoForConfig.config,
        [agentKey]: !selectedRepoForConfig.config[agentKey],
      },
    };
    setSelectedRepoForConfig(updated);
    setRepositories(repositories.map((r) => (r.id === updated.id ? updated : r)));
  };

  const handleConnectSelected = () => {
    const newlyConnected: RepoItem[] = AVAILABLE_GITHUB_REPOS.filter((gh) =>
      selectedGithubIds.includes(gh.id)
    ).map((gh) => ({
      id: `r-${gh.id}`,
      github_repo_id: gh.id,
      full_name: gh.name,
      name: gh.name.split("/")[1],
      default_branch: "main",
      language: gh.language,
      is_active: true,
      last_review_at: "Never",
      config: {
        security_agent_enabled: true,
        style_agent_enabled: true,
        test_coverage_agent_enabled: true,
        auto_review_enabled: true,
        ignored_paths: [],
      },
    }));

    setRepositories([...repositories, ...newlyConnected]);
    setSelectedGithubIds([]);
    setIsConnectModalOpen(false);
  };

  const handleDisconnect = (repoId: string) => {
    setRepositories(repositories.filter((r) => r.id !== repoId));
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Connected Repositories</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage repository access, review trigger rules, and per-repository AI agent toggles.
          </p>
        </div>

        <Button
          onClick={() => setIsConnectModalOpen(true)}
          className="bg-violet-600 hover:bg-violet-700 text-white gap-2 shadow-lg shadow-violet-950/20"
        >
          <PlusIcon className="h-4 w-4" />
          Connect Repositories
        </Button>
      </div>

      {/* Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search repositories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-card border-border/80"
          />
        </div>
        <span className="text-xs text-muted-foreground font-mono">
          {filteredRepos.length} repositories active
        </span>
      </div>

      {/* Repositories Grid */}
      <div className="grid gap-4">
        {filteredRepos.map((repo) => (
          <div
            key={repo.id}
            className="group flex flex-col justify-between gap-4 rounded-xl border border-border/70 bg-card/60 p-5 transition-all hover:border-violet-500/40 hover:bg-card/90 md:flex-row md:items-center"
          >
            <div className="space-y-2">
              <div className="flex items-center gap-2.5">
                <FolderGit2Icon className="h-5 w-5 text-violet-400" />
                <h3 className="font-semibold text-foreground text-base font-mono">
                  {repo.full_name}
                </h3>
                <Badge variant="outline" className="text-xs font-normal font-mono">
                  <GitBranchIcon className="h-3 w-3 mr-1" />
                  {repo.default_branch}
                </Badge>
                {repo.is_active && (
                  <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-[11px]">
                    Active
                  </Badge>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground font-mono">
                <span>Language: <strong className="text-foreground">{repo.language}</strong></span>
                <span>•</span>
                <span>Last reviewed: <strong className="text-foreground">{repo.last_review_at}</strong></span>
              </div>

              {/* Active Agents Pills */}
              <div className="flex items-center gap-2 pt-1">
                {repo.config.security_agent_enabled && (
                  <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                    <ShieldIcon className="h-3 w-3 text-red-400" />
                    Security
                  </Badge>
                )}
                {repo.config.style_agent_enabled && (
                  <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                    <PaintbrushIcon className="h-3 w-3 text-amber-400" />
                    Style
                  </Badge>
                )}
                {repo.config.test_coverage_agent_enabled && (
                  <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                    <TestTubeIcon className="h-3 w-3 text-emerald-400" />
                    Coverage
                  </Badge>
                )}
                {repo.config.auto_review_enabled && (
                  <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                    <ZapIcon className="h-3 w-3 text-violet-400" />
                    Auto-Review
                  </Badge>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedRepoForConfig(repo)}
                className="gap-1.5 text-xs"
              >
                <SlidersHorizontalIcon className="h-3.5 w-3.5" />
                Configure Agents
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDisconnect(repo.id)}
                className="h-8 w-8 text-muted-foreground hover:text-red-400"
              >
                <Trash2Icon className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Configure AI Agents Modal */}
      {selectedRepoForConfig && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="relative w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div className="flex items-center gap-2">
                <SlidersHorizontalIcon className="h-5 w-5 text-violet-400" />
                <div>
                  <h3 className="font-semibold text-foreground text-sm">Configure AI Agents</h3>
                  <p className="text-xs text-muted-foreground font-mono">
                    {selectedRepoForConfig.full_name}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelectedRepoForConfig(null)}
                className="h-8 w-8 text-muted-foreground"
              >
                <XIcon className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-4 text-xs">
              <p className="text-muted-foreground">
                Enable or disable specialized AI agents during automated pull request reviews.
              </p>

              {/* Toggles */}
              <div className="divide-y divide-border/60 rounded-lg border border-border/80 bg-background/50">
                <div className="flex items-center justify-between p-3">
                  <div className="space-y-0.5">
                    <div className="font-semibold flex items-center gap-1.5 text-foreground">
                      <ShieldIcon className="h-3.5 w-3.5 text-red-400" />
                      Security Agent
                    </div>
                    <p className="text-muted-foreground text-[11px]">
                      Vulnerability scanning, token exposure, and auth flaws.
                    </p>
                  </div>
                  <Button
                    variant={selectedRepoForConfig.config.security_agent_enabled ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => handleToggleAgent("security_agent_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config.security_agent_enabled ? "Enabled" : "Disabled"}
                  </Button>
                </div>

                <div className="flex items-center justify-between p-3">
                  <div className="space-y-0.5">
                    <div className="font-semibold flex items-center gap-1.5 text-foreground">
                      <PaintbrushIcon className="h-3.5 w-3.5 text-amber-400" />
                      Style & Clean Code Agent
                    </div>
                    <p className="text-muted-foreground text-[11px]">
                      Maintainability, naming conventions, and idiomatic patterns.
                    </p>
                  </div>
                  <Button
                    variant={selectedRepoForConfig.config.style_agent_enabled ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => handleToggleAgent("style_agent_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config.style_agent_enabled ? "Enabled" : "Disabled"}
                  </Button>
                </div>

                <div className="flex items-center justify-between p-3">
                  <div className="space-y-0.5">
                    <div className="font-semibold flex items-center gap-1.5 text-foreground">
                      <TestTubeIcon className="h-3.5 w-3.5 text-emerald-400" />
                      Test Coverage Agent
                    </div>
                    <p className="text-muted-foreground text-[11px]">
                      Missing unit tests, mock coverage, and edge cases.
                    </p>
                  </div>
                  <Button
                    variant={selectedRepoForConfig.config.test_coverage_agent_enabled ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => handleToggleAgent("test_coverage_agent_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config.test_coverage_agent_enabled ? "Enabled" : "Disabled"}
                  </Button>
                </div>

                <div className="flex items-center justify-between p-3">
                  <div className="space-y-0.5">
                    <div className="font-semibold flex items-center gap-1.5 text-foreground">
                      <ZapIcon className="h-3.5 w-3.5 text-violet-400" />
                      Automated Review on PR Open
                    </div>
                    <p className="text-muted-foreground text-[11px]">
                      Automatically initiate review when a PR is created or updated.
                    </p>
                  </div>
                  <Button
                    variant={selectedRepoForConfig.config.auto_review_enabled ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => handleToggleAgent("auto_review_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config.auto_review_enabled ? "Active" : "Manual Only"}
                  </Button>
                </div>
              </div>

              {/* Ignored Paths */}
              <div className="space-y-1.5 pt-2">
                <label className="font-medium text-foreground">Ignored File Patterns (Glob)</label>
                <Input
                  value={selectedRepoForConfig.config.ignored_paths.join(", ")}
                  onChange={(e) => {
                    const paths = e.target.value.split(",").map((s) => s.trim()).filter(Boolean);
                    const updated = {
                      ...selectedRepoForConfig,
                      config: { ...selectedRepoForConfig.config, ignored_paths: paths },
                    };
                    setSelectedRepoForConfig(updated);
                    setRepositories(repositories.map((r) => (r.id === updated.id ? updated : r)));
                  }}
                  placeholder="e.g. docs/**, *.lock, dist/**"
                  className="font-mono text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/80">
              <Button size="sm" onClick={() => setSelectedRepoForConfig(null)} className="bg-violet-600 hover:bg-violet-700 text-white">
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Connect Repositories Modal */}
      {isConnectModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="relative w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div className="flex items-center gap-2">
                <SparklesIcon className="h-5 w-5 text-violet-400" />
                <h3 className="font-semibold text-foreground text-sm">Connect GitHub Repositories</h3>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsConnectModalOpen(false)}
                className="h-8 w-8 text-muted-foreground"
              >
                <XIcon className="h-4 w-4" />
              </Button>
            </div>

            <p className="text-xs text-muted-foreground">
              Select repositories from your GitHub App installation to enable automated multi-agent code reviews.
            </p>

            <div className="divide-y divide-border/60 rounded-lg border border-border/80 bg-background/50 text-xs">
              {AVAILABLE_GITHUB_REPOS.map((gh) => {
                const isSelected = selectedGithubIds.includes(gh.id);
                return (
                  <div
                    key={gh.id}
                    onClick={() => {
                      if (isSelected) {
                        setSelectedGithubIds(selectedGithubIds.filter((id) => id !== gh.id));
                      } else {
                        setSelectedGithubIds([...selectedGithubIds, gh.id]);
                      }
                    }}
                    className={`flex items-center justify-between p-3 cursor-pointer transition-colors ${
                      isSelected ? "bg-violet-950/20" : "hover:bg-accent/40"
                    }`}
                  >
                    <div>
                      <p className="font-mono font-medium text-foreground">{gh.name}</p>
                      <span className="text-[11px] text-muted-foreground">{gh.language}</span>
                    </div>
                    <Button variant={isSelected ? "secondary" : "outline"} size="sm" className="text-xs h-7">
                      {isSelected ? "Selected" : "Select"}
                    </Button>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/80">
              <Button variant="outline" size="sm" onClick={() => setIsConnectModalOpen(false)}>
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleConnectSelected}
                disabled={selectedGithubIds.length === 0}
                className="bg-violet-600 hover:bg-violet-700 text-white"
              >
                Connect {selectedGithubIds.length} Repositories
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
