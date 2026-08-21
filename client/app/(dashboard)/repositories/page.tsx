"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
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
  BookOpenIcon,
  ExternalLinkIcon,
  KeyIcon,
  RefreshCwIcon,
  AlertCircleIcon,
  CheckCircle2Icon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api, type GitHubAvailableRepo, type RepositoryConfig, type RepositoryResponse } from "@/lib/api";

export default function RepositoriesPage() {
  const { getToken } = useAuth();
  const [repositories, setRepositories] = useState<RepositoryResponse[]>([]);
  const [availableGithubRepos, setAvailableGithubRepos] = useState<GitHubAvailableRepo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRepoForConfig, setSelectedRepoForConfig] = useState<RepositoryResponse | null>(null);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [isGuideModalOpen, setIsGuideModalOpen] = useState(false);
  const [selectedGithubIds, setSelectedGithubIds] = useState<number[]>([]);
  const githubAppName = process.env.NEXT_PUBLIC_GITHUB_APP_NAME || "pullsense-ai";

  useEffect(() => {
    let isMounted = true;

    async function fetchRepos() {
      try {
        const token = await getToken();
        const [repos, available] = await Promise.all([
          api.getRepositories(token).catch(() => []),
          api.getGitHubAvailableRepos(token).catch(() => []),
        ]);
        if (isMounted) {
          setRepositories(repos);
          setAvailableGithubRepos(available);
        }
      } catch (err) {
        console.error("Failed to fetch repositories:", err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    fetchRepos();

    return () => {
      isMounted = false;
    };
  }, [getToken]);

  const loadData = async () => {
    try {
      setIsRefreshing(true);
      const token = await getToken();
      const [repos, available] = await Promise.all([
        api.getRepositories(token).catch(() => []),
        api.getGitHubAvailableRepos(token).catch(() => []),
      ]);
      setRepositories(repos);
      setAvailableGithubRepos(available);
    } catch (err) {
      console.error("Failed to fetch repositories:", err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const filteredRepos = repositories.filter((r) =>
    r.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleAgent = async (agentKey: keyof RepositoryConfig) => {
    if (!selectedRepoForConfig) return;
    const currentVal = selectedRepoForConfig.config?.[agentKey] ?? true;
    const updatedVal = !currentVal;

    const newConfig: Partial<RepositoryConfig> = {
      [agentKey]: updatedVal,
    };

    try {
      const token = await getToken();
      const updatedConfig = await api.updateRepoConfig(
        selectedRepoForConfig.id,
        newConfig,
        token
      );

      const updatedRepo = {
        ...selectedRepoForConfig,
        config: updatedConfig,
      };

      setSelectedRepoForConfig(updatedRepo);
      setRepositories(
        repositories.map((r) => (r.id === updatedRepo.id ? updatedRepo : r))
      );
    } catch (err) {
      console.error("Failed to update config:", err);
    }
  };

  const handleConnectSelected = async () => {
    if (selectedGithubIds.length === 0) return;
    try {
      const token = await getToken();
      await api.connectGitHubRepos(selectedGithubIds, token);
      setSelectedGithubIds([]);
      setIsConnectModalOpen(false);
      await loadData();
    } catch (err) {
      console.error("Failed to connect repositories:", err);
    }
  };

  const handleDisconnect = async (repoId: string) => {
    try {
      const token = await getToken();
      await api.disconnectRepository(repoId, token);
      setRepositories(repositories.filter((r) => r.id !== repoId));
    } catch (err) {
      console.error("Failed to disconnect repository:", err);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Connected Repositories</h1>
            <Badge variant="secondary" className="gap-1 text-xs bg-accent/60">
              <SparklesIcon className="h-3 w-3 text-violet-400" />
              Live GitHub App Sync
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Manage repository access, review trigger rules, and per-repository AI agent toggles.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsGuideModalOpen(true)}
            className="gap-2"
          >
            <BookOpenIcon className="h-4 w-4 text-violet-400" />
            GitHub App Setup Guide
          </Button>

          <Button
            onClick={() => setIsConnectModalOpen(true)}
            className="bg-violet-600 hover:bg-violet-700 text-white gap-2 shadow-lg shadow-violet-950/20"
          >
            <PlusIcon className="h-4 w-4" />
            Connect Repositories
          </Button>
        </div>
      </div>

      {/* Search & Refresh Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:w-80">
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search repositories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-card border-border/80 text-xs"
          />
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground font-mono">
            {filteredRepos.length} connected repositories
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={loadData}
            disabled={isRefreshing}
            className="h-8 px-2.5 text-xs text-muted-foreground"
          >
            <RefreshCwIcon
              className={`h-3.5 w-3.5 mr-1.5 ${isRefreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </div>

      {/* Repositories List */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-sm text-muted-foreground">
          <RefreshCwIcon className="h-5 w-5 animate-spin mr-2" />
          Loading repositories from database...
        </div>
      ) : filteredRepos.length > 0 ? (
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
                  <span>
                    Language:{" "}
                    <strong className="text-foreground">
                      {repo.language || "Multi-language"}
                    </strong>
                  </span>
                  <span>•</span>
                  <span>
                    Last reviewed:{" "}
                    <strong className="text-foreground">
                      {repo.last_review_at
                        ? new Date(repo.last_review_at).toLocaleDateString()
                        : "Awaiting PR"}
                    </strong>
                  </span>
                </div>

                {/* Active Agents Pills */}
                <div className="flex items-center gap-2 pt-1">
                  {repo.config?.security_agent_enabled !== false && (
                    <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                      <ShieldIcon className="h-3 w-3 text-red-400" />
                      Security
                    </Badge>
                  )}
                  {repo.config?.style_agent_enabled !== false && (
                    <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                      <PaintbrushIcon className="h-3 w-3 text-amber-400" />
                      Style
                    </Badge>
                  )}
                  {repo.config?.test_coverage_agent_enabled !== false && (
                    <Badge variant="secondary" className="text-[10px] gap-1 bg-accent/60">
                      <TestTubeIcon className="h-3 w-3 text-emerald-400" />
                      Coverage
                    </Badge>
                  )}
                  {repo.config?.auto_review_enabled !== false && (
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
      ) : (
        /* Empty State */
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-muted-foreground mb-4">
            <FolderGit2Icon className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-semibold">No repositories connected yet</h3>
          <p className="mt-1 max-w-md text-sm text-muted-foreground leading-relaxed">
            Install the PullSense GitHub App or connect your repositories to start automated AI code reviews on every pull request.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Button
              onClick={() => setIsGuideModalOpen(true)}
              variant="outline"
              className="gap-2 text-xs"
            >
              <BookOpenIcon className="h-4 w-4 text-violet-400" />
              View GitHub App Setup Guide
            </Button>
            <Button
              onClick={() => setIsConnectModalOpen(true)}
              className="bg-violet-600 hover:bg-violet-700 text-white gap-2 text-xs"
            >
              <PlusIcon className="h-4 w-4" />
              Connect Repositories
            </Button>
          </div>
        </div>
      )}

      {/* GitHub App Setup Guide Modal */}
      {isGuideModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="relative w-full max-w-2xl rounded-xl border border-border bg-card p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div className="flex items-center gap-2">
                <BookOpenIcon className="h-5 w-5 text-violet-400" />
                <div>
                  <h3 className="font-semibold text-foreground text-base">
                    GitHub App Connection Guide
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Step-by-step instructions to link GitHub repositories to PullSense.
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsGuideModalOpen(false)}
                className="h-8 w-8 text-muted-foreground"
              >
                <XIcon className="h-4 w-4" />
              </Button>
            </div>

            {/* Quick App Link */}
            <div className="rounded-lg border border-violet-500/30 bg-violet-950/20 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-violet-300">
                  Option 1: Quick Install Existing GitHub App
                </span>
                <Badge variant="outline" className="text-[11px] font-mono">
                  {githubAppName}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                If your GitHub App is registered, click below to install it on your GitHub account or organization:
              </p>
              <div className="flex items-center gap-2">
                <a
                  href={`https://github.com/apps/${githubAppName}/installations/new`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-xs font-medium text-white hover:bg-violet-700 transition-colors shadow-sm"
                >
                  <ExternalLinkIcon className="h-3.5 w-3.5" />
                  Install GitHub App on GitHub
                </a>
              </div>
            </div>

            {/* Step-by-Step Setup */}
            <div className="space-y-4 text-xs">
              <h4 className="font-semibold text-foreground text-sm flex items-center gap-2">
                <KeyIcon className="h-4 w-4 text-amber-400" />
                Option 2: Register a New GitHub App (Self-Hosted / Enterprise)
              </h4>

              <div className="space-y-3 font-mono">
                <div className="rounded-lg border border-border/80 bg-background/50 p-3 space-y-1">
                  <p className="font-sans font-semibold text-foreground">
                    1. Go to GitHub App Creation
                  </p>
                  <p className="text-muted-foreground text-[11px] font-sans">
                    Navigate to <strong>GitHub &gt; Settings &gt; Developer settings &gt; GitHub Apps &gt; New GitHub App</strong>.
                  </p>
                </div>

                <div className="rounded-lg border border-border/80 bg-background/50 p-3 space-y-2">
                  <p className="font-sans font-semibold text-foreground">
                    2. Webhook & Endpoint Settings
                  </p>
                  <div className="space-y-1 text-[11px]">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Webhook URL:</span>
                      <span className="text-foreground font-semibold">
                        http://your-server-domain/api/v1/webhooks/github
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Local Dev (Smee.io):</span>
                      <span className="text-violet-400">https://smee.io/your-unique-channel</span>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-border/80 bg-background/50 p-3 space-y-2">
                  <p className="font-sans font-semibold text-foreground">
                    3. Repository Permissions Required
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="flex items-center gap-1.5 text-emerald-400">
                      <CheckCircle2Icon className="h-3.5 w-3.5" />
                      <span>Pull Requests: Read &amp; Write</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-emerald-400">
                      <CheckCircle2Icon className="h-3.5 w-3.5" />
                      <span>Issues: Read &amp; Write</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-emerald-400">
                      <CheckCircle2Icon className="h-3.5 w-3.5" />
                      <span>Contents: Read-only</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-emerald-400">
                      <CheckCircle2Icon className="h-3.5 w-3.5" />
                      <span>Metadata: Read-only</span>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-border/80 bg-background/50 p-3 space-y-1">
                  <p className="font-sans font-semibold text-foreground">
                    4. Subscribe to Events
                  </p>
                  <p className="text-muted-foreground text-[11px] font-sans">
                    Check <strong>Pull request</strong> and <strong>Installation</strong> events.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end pt-3 border-t border-border/80">
              <Button
                size="sm"
                onClick={() => setIsGuideModalOpen(false)}
                className="bg-violet-600 hover:bg-violet-700 text-white text-xs"
              >
                Got It
              </Button>
            </div>
          </div>
        </div>
      )}

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
                    variant={
                      selectedRepoForConfig.config?.security_agent_enabled !== false
                        ? "secondary"
                        : "outline"
                    }
                    size="sm"
                    onClick={() => handleToggleAgent("security_agent_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config?.security_agent_enabled !== false
                      ? "Enabled"
                      : "Disabled"}
                  </Button>
                </div>

                <div className="flex items-center justify-between p-3">
                  <div className="space-y-0.5">
                    <div className="font-semibold flex items-center gap-1.5 text-foreground">
                      <PaintbrushIcon className="h-3.5 w-3.5 text-amber-400" />
                      Style &amp; Clean Code Agent
                    </div>
                    <p className="text-muted-foreground text-[11px]">
                      Maintainability, naming conventions, and idiomatic patterns.
                    </p>
                  </div>
                  <Button
                    variant={
                      selectedRepoForConfig.config?.style_agent_enabled !== false
                        ? "secondary"
                        : "outline"
                    }
                    size="sm"
                    onClick={() => handleToggleAgent("style_agent_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config?.style_agent_enabled !== false
                      ? "Enabled"
                      : "Disabled"}
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
                    variant={
                      selectedRepoForConfig.config?.test_coverage_agent_enabled !== false
                        ? "secondary"
                        : "outline"
                    }
                    size="sm"
                    onClick={() => handleToggleAgent("test_coverage_agent_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config?.test_coverage_agent_enabled !== false
                      ? "Enabled"
                      : "Disabled"}
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
                    variant={
                      selectedRepoForConfig.config?.auto_review_enabled !== false
                        ? "secondary"
                        : "outline"
                    }
                    size="sm"
                    onClick={() => handleToggleAgent("auto_review_enabled")}
                    className="text-xs h-7"
                  >
                    {selectedRepoForConfig.config?.auto_review_enabled !== false
                      ? "Active"
                      : "Manual Only"}
                  </Button>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/80">
              <Button
                size="sm"
                onClick={() => setSelectedRepoForConfig(null)}
                className="bg-violet-600 hover:bg-violet-700 text-white text-xs"
              >
                Close
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
                <h3 className="font-semibold text-foreground text-sm">
                  Connect GitHub Repositories
                </h3>
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
              Select repositories from your GitHub App installation to enable automated code reviews.
            </p>

            {availableGithubRepos.length > 0 ? (
              <div className="divide-y divide-border/60 rounded-lg border border-border/80 bg-background/50 text-xs max-h-60 overflow-y-auto">
                {availableGithubRepos.map((gh) => {
                  const isSelected = selectedGithubIds.includes(gh.github_repo_id);
                  return (
                    <div
                      key={gh.github_repo_id}
                      onClick={() => {
                        if (isSelected) {
                          setSelectedGithubIds(
                            selectedGithubIds.filter((id) => id !== gh.github_repo_id)
                          );
                        } else {
                          setSelectedGithubIds([...selectedGithubIds, gh.github_repo_id]);
                        }
                      }}
                      className={`flex items-center justify-between p-3 cursor-pointer transition-colors ${
                        isSelected ? "bg-violet-950/20" : "hover:bg-accent/40"
                      }`}
                    >
                      <div>
                        <p className="font-mono font-medium text-foreground">{gh.full_name}</p>
                        <span className="text-[11px] text-muted-foreground">
                          {gh.language || "Repository"}
                        </span>
                      </div>
                      <Button
                        variant={isSelected ? "secondary" : "outline"}
                        size="sm"
                        className="text-xs h-7"
                      >
                        {isSelected ? "Selected" : "Select"}
                      </Button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center space-y-2">
                <AlertCircleIcon className="h-6 w-6 text-amber-400 mx-auto" />
                <p className="text-xs font-semibold text-foreground">
                  No repositories detected from GitHub App
                </p>
                <p className="text-[11px] text-muted-foreground">
                  Make sure you have installed the GitHub App on your account and granted repository permissions.
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setIsConnectModalOpen(false);
                    setIsGuideModalOpen(true);
                  }}
                  className="text-xs mt-2"
                >
                  View Setup Guide
                </Button>
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/80">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsConnectModalOpen(false)}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleConnectSelected}
                disabled={selectedGithubIds.length === 0}
                className="bg-violet-600 hover:bg-violet-700 text-white text-xs"
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
