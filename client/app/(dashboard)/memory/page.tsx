"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import {
  BrainIcon,
  PlusIcon,
  SearchIcon,
  Building2Icon,
  FolderGit2Icon,
  UserCheckIcon,
  Trash2Icon,
  CheckCircle2Icon,
  ShieldCheckIcon,
  SparklesIcon,
  XIcon,
  RefreshCwIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api, type MemoryRule } from "@/lib/api";

export default function MemoryPage() {
  const { getToken } = useAuth();
  const [memories, setMemories] = useState<MemoryRule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTier, setActiveTier] = useState<"all" | "org" | "repo" | "developer">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [formTier, setFormTier] = useState<"org" | "repo" | "developer">("org");
  const [formType, setFormType] = useState("standard");
  const [formKey, setFormKey] = useState("");
  const [formValue, setFormValue] = useState("");
  const [formTarget, setFormTarget] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchMemories() {
      try {
        const token = await getToken();
        const [orgMemories, repoMemories, devMemories] = await Promise.all([
          api.getOrgMemories(token).catch(() => []),
          api.getRepoMemories(undefined, token).catch(() => []),
          api.getDeveloperMemories(undefined, token).catch(() => []),
        ]);

        if (isMounted) {
          const formatted: MemoryRule[] = [
            ...orgMemories.map((m) => ({ ...m, tier: "org" as const })),
            ...repoMemories.map((m) => ({ ...m, tier: "repo" as const })),
            ...devMemories.map((m) => ({ ...m, tier: "developer" as const })),
          ];
          setMemories(formatted);
        }
      } catch (err) {
        console.error("Failed to load memory rules:", err);
      } finally {
        if (isMounted) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    fetchMemories();

    return () => {
      isMounted = false;
    };
  }, [getToken]);

  const loadMemories = async () => {
    try {
      setIsRefreshing(true);
      const token = await getToken();
      const [orgMemories, repoMemories, devMemories] = await Promise.all([
        api.getOrgMemories(token).catch(() => []),
        api.getRepoMemories(undefined, token).catch(() => []),
        api.getDeveloperMemories(undefined, token).catch(() => []),
      ]);

      const formatted: MemoryRule[] = [
        ...orgMemories.map((m) => ({ ...m, tier: "org" as const })),
        ...repoMemories.map((m) => ({ ...m, tier: "repo" as const })),
        ...devMemories.map((m) => ({ ...m, tier: "developer" as const })),
      ];

      setMemories(formatted);
    } catch (err) {
      console.error("Failed to load memory rules:", err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const filteredMemories = memories.filter((m) => {
    const matchesTier = activeTier === "all" || m.tier === activeTier;
    const matchesSearch =
      m.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.value.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (m.memory_type && m.memory_type.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTier && matchesSearch;
  });

  const handleCreateMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formKey.trim() || !formValue.trim()) return;

    try {
      const token = await getToken();
      if (formTier === "org") {
        await api.createOrgMemory(
          { memory_type: formType, key: formKey.trim(), value: formValue.trim() },
          token
        );
      } else if (formTier === "repo") {
        await api.createRepoMemory(
          {
            repository_id: formTarget.trim() || "default-repo",
            memory_type: formType,
            key: formKey.trim(),
            value: formValue.trim(),
          },
          token
        );
      } else {
        await api.createDeveloperMemory(
          {
            user_id: formTarget.trim() || "default-user",
            memory_type: formType,
            key: formKey.trim(),
            value: formValue.trim(),
          },
          token
        );
      }

      setFormKey("");
      setFormValue("");
      setFormTarget("");
      setIsModalOpen(false);
      await loadMemories();
    } catch (err) {
      console.error("Failed to create memory rule:", err);
    }
  };

  const handleDeleteMemory = async (item: MemoryRule) => {
    try {
      const token = await getToken();
      if (item.tier === "org") {
        await api.deleteOrgMemory(item.id, token);
      } else if (item.tier === "repo") {
        await api.deleteRepoMemory(item.id, token);
      } else {
        await api.deleteDeveloperMemory(item.id, token);
      }
      setMemories(memories.filter((m) => m.id !== item.id));
    } catch (err) {
      console.error("Failed to delete memory rule:", err);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Team Memory &amp; Policies</h1>
            <Badge variant="secondary" className="gap-1 text-xs bg-accent/60">
              <SparklesIcon className="h-3 w-3 text-violet-400" />
              Active in Agent Prompts
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Persistent rules, architecture conventions, and developer preferences remembered and enforced across all PR reviews.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            onClick={() => setIsModalOpen(true)}
            className="bg-violet-600 hover:bg-violet-700 text-white gap-2 shadow-lg shadow-violet-950/20 text-xs"
          >
            <PlusIcon className="h-4 w-4" />
            Add Memory Rule
          </Button>
        </div>
      </div>

      {/* 3-Tier Stats Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div
          onClick={() => setActiveTier("org")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            activeTier === "org"
              ? "border-violet-500 bg-violet-950/20"
              : "border-border/70 bg-card/60 hover:bg-card"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Org Standards
            </span>
            <Building2Icon className="h-4 w-4 text-violet-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold">
              {memories.filter((m) => m.tier === "org").length}
            </span>
            <span className="text-xs text-muted-foreground">company-wide rules</span>
          </div>
        </div>

        <div
          onClick={() => setActiveTier("repo")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            activeTier === "repo"
              ? "border-violet-500 bg-violet-950/20"
              : "border-border/70 bg-card/60 hover:bg-card"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Repo Conventions
            </span>
            <FolderGit2Icon className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold">
              {memories.filter((m) => m.tier === "repo").length}
            </span>
            <span className="text-xs text-muted-foreground">architecture rules</span>
          </div>
        </div>

        <div
          onClick={() => setActiveTier("developer")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            activeTier === "developer"
              ? "border-violet-500 bg-violet-950/20"
              : "border-border/70 bg-card/60 hover:bg-card"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Developer Habits
            </span>
            <UserCheckIcon className="h-4 w-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold">
              {memories.filter((m) => m.tier === "developer").length}
            </span>
            <span className="text-xs text-muted-foreground">personalized styles</span>
          </div>
        </div>
      </div>

      {/* Filter Tabs & Search */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:w-80">
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search memory rules by key, text, or type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-card border-border/80 text-xs"
          />
        </div>

        <div className="flex items-center gap-1.5">
          {[
            { label: "All Rules", value: "all" as const },
            { label: "Organization", value: "org" as const },
            { label: "Repositories", value: "repo" as const },
            { label: "Developers", value: "developer" as const },
          ].map((tab) => (
            <Button
              key={tab.value}
              variant={activeTier === tab.value ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setActiveTier(tab.value)}
              className="text-xs capitalize"
            >
              {tab.label}
            </Button>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={loadMemories}
            disabled={isRefreshing}
            className="h-8 px-2.5 text-xs text-muted-foreground"
          >
            <RefreshCwIcon className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Memory Rules List */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-sm text-muted-foreground">
          <RefreshCwIcon className="h-5 w-5 animate-spin mr-2" />
          Loading memory rules from database...
        </div>
      ) : filteredMemories.length > 0 ? (
        <div className="grid gap-4">
          {filteredMemories.map((item) => {
            const isOrg = item.tier === "org";
            const isRepo = item.tier === "repo";

            return (
              <div
                key={item.id}
                className="group flex flex-col justify-between gap-4 rounded-xl border border-border/70 bg-card/60 p-5 transition-all hover:border-violet-500/40 hover:bg-card/90"
              >
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {isOrg ? (
                        <Badge className="bg-violet-500/15 text-violet-400 border-violet-500/30 gap-1 text-xs">
                          <Building2Icon className="h-3 w-3" />
                          Organization
                        </Badge>
                      ) : isRepo ? (
                        <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 gap-1 text-xs">
                          <FolderGit2Icon className="h-3 w-3" />
                          Repository
                        </Badge>
                      ) : (
                        <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 gap-1 text-xs">
                          <UserCheckIcon className="h-3 w-3" />
                          Developer
                        </Badge>
                      )}

                      <Badge variant="outline" className="text-xs font-mono">
                        {item.memory_type}
                      </Badge>

                      <span className="text-xs font-mono font-semibold text-foreground">
                        {item.key}
                      </span>
                    </div>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteMemory(item)}
                      className="h-7 w-7 text-muted-foreground hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2Icon className="h-3.5 w-3.5" />
                    </Button>
                  </div>

                  <p className="text-xs leading-relaxed text-foreground/90 font-mono bg-background/50 p-3 rounded-lg border border-border/40">
                    {item.value}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground pt-1">
                    <span>Added {new Date(item.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1 text-emerald-400">
                      <CheckCircle2Icon className="h-3 w-3" />
                      Injected in LLM prompt
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
          <BrainIcon className="h-10 w-10 text-muted-foreground mb-3" />
          <h3 className="text-base font-semibold">No memory rules configured</h3>
          <p className="mt-1 text-xs text-muted-foreground max-w-sm">
            Define coding standards or architectural guidelines that the AI agents should always enforce during reviews.
          </p>
          <Button
            size="sm"
            onClick={() => setIsModalOpen(true)}
            className="mt-4 bg-violet-600 hover:bg-violet-700 text-white text-xs gap-1.5"
          >
            <PlusIcon className="h-3.5 w-3.5" />
            Add First Rule
          </Button>
        </div>
      )}

      {/* Add Memory Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="relative w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheckIcon className="h-5 w-5 text-violet-400" />
                <h3 className="font-semibold text-foreground text-sm">Add New Memory Rule</h3>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsModalOpen(false)}
                className="h-8 w-8 text-muted-foreground"
              >
                <XIcon className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleCreateMemory} className="space-y-4 text-xs">
              {/* Tier Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Scope / Tier</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: "Organization", value: "org" as const },
                    { label: "Repository", value: "repo" as const },
                    { label: "Developer", value: "developer" as const },
                  ].map((tier) => (
                    <Button
                      key={tier.value}
                      type="button"
                      variant={formTier === tier.value ? "secondary" : "outline"}
                      size="sm"
                      onClick={() => setFormTier(tier.value)}
                      className="text-xs"
                    >
                      {tier.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Type Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Memory Type</label>
                <Input
                  placeholder="e.g. standard | architecture | convention | preference"
                  value={formType}
                  onChange={(e) => setFormType(e.target.value)}
                  className="text-xs font-mono"
                  required
                />
              </div>

              {/* Target / Identifier */}
              {formTier !== "org" && (
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">
                    Target (Repository ID or Developer Username)
                  </label>
                  <Input
                    placeholder="e.g. acme-corp/api-gateway or sarah-dev"
                    value={formTarget}
                    onChange={(e) => setFormTarget(e.target.value)}
                    className="text-xs font-mono"
                  />
                </div>
              )}

              {/* Key */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Rule Key / Identifier</label>
                <Input
                  placeholder="e.g. clean_architecture or avoid_raw_jwt"
                  value={formKey}
                  onChange={(e) => setFormKey(e.target.value)}
                  className="text-xs font-mono"
                  required
                />
              </div>

              {/* Value / Instruction */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Instruction for AI Reviewers</label>
                <textarea
                  placeholder="State the exact coding standard, architectural rule, or preferred pattern to enforce during PR reviews..."
                  value={formValue}
                  onChange={(e) => setFormValue(e.target.value)}
                  rows={4}
                  className="w-full rounded-md border border-border/80 bg-background px-3 py-2 text-xs font-mono placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-violet-500"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/80">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  className="bg-violet-600 hover:bg-violet-700 text-white gap-1.5"
                >
                  <PlusIcon className="h-3.5 w-3.5" />
                  Save Rule
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
