import { create } from "zustand";

interface AppState {
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Active filters
  activeRepoFilter: string | null;
  setActiveRepoFilter: (repoId: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Sidebar
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Active filters
  activeRepoFilter: null,
  setActiveRepoFilter: (repoId) => set({ activeRepoFilter: repoId }),
}));
