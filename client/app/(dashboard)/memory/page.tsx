"use client";

import { useState } from "react";
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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface MemoryItem {
  id: string;
  tier: "org" | "repo" | "developer";
  memory_type: string;
  key: string;
  value: string;
  target?: string;
  relevance_score?: number;
  created_at: string;
}

const INITIAL_MEMORIES: MemoryItem[] = [
  // Org Standards
  {
    id: "m-1",
    tier: "org",
    memory_type: "standard",
    key: "api_documentation",
    value: "All public API routes must include OpenAPI response schemas and descriptive docstrings with status code definitions.",
    target: "Acme Global Org",
    created_at: "2 days ago",
  },
  {
    id: "m-2",
    tier: "org",
    memory_type: "compliance",
    key: "no_raw_secrets",
    value: "Never commit API keys, connection strings, or RSA private keys to source code or fixtures. Always utilize environment secret managers.",
    target: "Acme Global Org",
    created_at: "1 week ago",
  },
  // Repo Conventions
  {
    id: "m-3",
    tier: "repo",
    memory_type: "architecture",
    key: "clean_architecture_layers",
    value: "Follow strict Clean Architecture: domain models and business services must never import from database infrastructure or API routers.",
    target: "acme-corp/api-gateway",
    relevance_score: 1.0,
    created_at: "3 days ago",
  },
  {
    id: "m-4",
    tier: "repo",
    memory_type: "convention",
    key: "error_hierarchy",
    value: "Raise domain-specific subclasses of `DomainError` instead of generic `ValueError` or `RuntimeError` for clean status mapping.",
    target: "acme-corp/core-service",
    relevance_score: 0.9,
    created_at: "5 days ago",
  },
  // Developer Preferences
  {
    id: "m-5",
    tier: "developer",
    memory_type: "preference",
    key: "async_await_syntax",
    value: "Prefers async/await over raw task scheduling callbacks; prefers explicit typing over untyped `Any` in new functions.",
    target: "sarah-dev",
    relevance_score: 0.95,
    created_at: "1 day ago",
  },
  {
    id: "m-6",
    tier: "developer",
    memory_type: "feedback",
    key: "test_cleanup",
    value: "Frequently reminds to clean up temporary mock fixtures in pytest teardown or `yield` generators.",
    target: "alex-chen",
    relevance_score: 0.85,
    created_at: "4 days ago",
  },
];

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryItem[]>(INITIAL_MEMORIES);
  const [activeTier, setActiveTier] = useState<"all" | "org" | "repo" | "developer">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [formTier, setFormTier] = useState<"org" | "repo" | "developer">("org");
  const [formType, setFormType] = useState("standard");
  const [formKey, setFormKey] = useState("");
  const [formValue, setFormValue] = useState("");
  const [formTarget, setFormTarget] = useState("");

  const filteredMemories = memories.filter((m) => {
    const matchesTier = activeTier === "all" || m.tier === activeTier;
    const matchesSearch =
      m.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.value.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (m.target && m.target.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTier && matchesSearch;
  });

  const handleCreateMemory = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formKey.trim() || !formValue.trim()) return;

    const newItem: MemoryItem = {
      id: `m-${Date.now()}`,
      tier: formTier,
      memory_type: formType,
      key: formKey.trim(),
      value: formValue.trim(),
      target: formTarget.trim() || (formTier === "org" ? "Organization" : "Current Context"),
      relevance_score: 1.0,
      created_at: "Just now",
    };

    setMemories([newItem, ...memories]);
    setFormKey("");
    setFormValue("");
    setFormTarget("");
    setIsModalOpen(false);
  };

  const handleDeleteMemory = (id: string) => {
    setMemories(memories.filter((m) => m.id !== id));
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Team Memory & Policies</h1>
            <Badge variant="secondary" className="gap-1 text-xs bg-accent/60">
              <SparklesIcon className="h-3 w-3 text-violet-400" />
              Active in Agent Prompts
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Persistent rules, architecture conventions, and developer preferences remembered and enforced across all PR reviews.
          </p>
        </div>

        <Button
          onClick={() => setIsModalOpen(true)}
          className="bg-violet-600 hover:bg-violet-700 text-white gap-2 shadow-lg shadow-violet-950/20"
        >
          <PlusIcon className="h-4 w-4" />
          Add Memory Rule
        </Button>
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
            placeholder="Search memory rules by key, text, or target..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-card border-border/80"
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
        </div>
      </div>

      {/* Memory Rules List */}
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

                  <div className="flex items-center gap-2">
                    {item.target && (
                      <span className="text-xs text-muted-foreground font-mono bg-accent/40 px-2 py-0.5 rounded">
                        {item.target}
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteMemory(item.id)}
                      className="h-7 w-7 text-muted-foreground hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2Icon className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>

                <p className="text-sm leading-relaxed text-foreground/90 font-mono text-xs bg-background/50 p-3 rounded-lg border border-border/40">
                  {item.value}
                </p>

                <div className="flex items-center gap-4 text-xs text-muted-foreground pt-1">
                  <span>Added {item.created_at}</span>
                  {item.relevance_score !== undefined && (
                    <>
                      <span>•</span>
                      <span>Relevance: {(item.relevance_score * 100).toFixed(0)}%</span>
                    </>
                  )}
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

        {filteredMemories.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center">
            <BrainIcon className="h-10 w-10 text-muted-foreground mb-3" />
            <h3 className="text-base font-semibold">No memory rules found</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Add a new rule to guide AI reviewers with company and repository architectural standards.
            </p>
          </div>
        )}
      </div>

      {/* Add Memory Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="relative w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheckIcon className="h-5 w-5 text-violet-400" />
                <h3 className="font-semibold text-foreground">Add New Memory Rule</h3>
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

            <form onSubmit={handleCreateMemory} className="space-y-4 text-sm">
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
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">
                  Target (Repo Name / Dev Username / Org)
                </label>
                <Input
                  placeholder="e.g. acme-corp/api-gateway or sarah-dev"
                  value={formTarget}
                  onChange={(e) => setFormTarget(e.target.value)}
                  className="text-xs font-mono"
                />
              </div>

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
