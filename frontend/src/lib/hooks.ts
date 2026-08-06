/**
 * React hooks para consumo da API IFB com TanStack Query.
 * Todos os hooks usam o cliente HTTP centralizado com credentials: include.
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

// --- Politicians ---

export function usePoliticians(params: {
  q?: string;
  party?: string;
  state?: string;
  page?: number;
  limit?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params.q) searchParams.set("q", params.q);
  if (params.party) searchParams.set("party", params.party);
  if (params.state) searchParams.set("state", params.state);
  searchParams.set("page", String(params.page || 1));
  searchParams.set("limit", String(params.limit || 20));

  return useQuery({
    queryKey: ["politicians", params],
    queryFn: () => api.get(`/api/v1/politicians?${searchParams.toString()}`),
    staleTime: 60_000,
  });
}

export function usePolitician(slug: string) {
  return useQuery({
    queryKey: ["politician", slug],
    queryFn: () => api.get(`/api/v1/politicians/${slug}`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

// --- Electoral ---

export function useCandidacies(slug: string, year?: number) {
  const params = year ? `?election_year=${year}` : "";
  return useQuery({
    queryKey: ["candidacies", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/candidacies${params}`),
    enabled: !!slug,
    staleTime: 300_000,
  });
}

export function useAssets(slug: string, year?: number) {
  const params = year ? `?election_year=${year}` : "";
  return useQuery({
    queryKey: ["assets", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/assets${params}`),
    enabled: !!slug,
    staleTime: 300_000,
  });
}

export function useCampaignRevenues(slug: string, year?: number) {
  const params = year ? `?election_year=${year}` : "";
  return useQuery({
    queryKey: ["campaign-revenues", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/campaign/revenues${params}`),
    enabled: !!slug,
    staleTime: 300_000,
  });
}

export function useCampaignExpenses(slug: string, year?: number) {
  const params = year ? `?election_year=${year}` : "";
  return useQuery({
    queryKey: ["campaign-expenses", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/campaign/expenses${params}`),
    enabled: !!slug,
    staleTime: 300_000,
  });
}

export function useElectionResults(slug: string) {
  return useQuery({
    queryKey: ["election-results", slug],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/election-results`),
    enabled: !!slug,
    staleTime: 300_000,
  });
}

// --- Legislative ---

export function useLegislativeProfile(slug: string) {
  return useQuery({
    queryKey: ["legislative-profile", slug],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/legislative-profile`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

export function usePropositions(slug: string, params?: { year?: number; type?: string; page?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.type) searchParams.set("type", params.type);
  searchParams.set("page", String(params?.page || 1));

  return useQuery({
    queryKey: ["propositions", slug, params],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/propositions?${searchParams.toString()}`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

export function useVotes(slug: string, year?: number) {
  const params = year ? `?year=${year}` : "";
  return useQuery({
    queryKey: ["votes", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/votes${params}`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

export function useAttendance(slug: string, year?: number) {
  const params = year ? `?year=${year}` : "";
  return useQuery({
    queryKey: ["attendance", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/attendance${params}`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

export function useParliamentaryExpenses(slug: string, params?: { year?: number; month?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.month) searchParams.set("month", String(params.month));

  return useQuery({
    queryKey: ["parliamentary-expenses", slug, params],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/parliamentary-expenses?${searchParams.toString()}`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

export function useCommittees(slug: string) {
  return useQuery({
    queryKey: ["committees", slug],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/committees`),
    enabled: !!slug,
    staleTime: 300_000,
  });
}

export function useSpeeches(slug: string, year?: number) {
  const params = year ? `?year=${year}` : "";
  return useQuery({
    queryKey: ["speeches", slug, year],
    queryFn: () => api.get(`/api/v1/politicians/${slug}/speeches${params}`),
    enabled: !!slug,
    staleTime: 120_000,
  });
}

// --- Admin ---

export function useIntegrationDashboard() {
  return useQuery({
    queryKey: ["admin", "integrations", "dashboard"],
    queryFn: () => api.get("/api/v1/admin/integrations/dashboard"),
    staleTime: 10_000,
    refetchInterval: 10_000,
  });
}

export function useSyncJobs(params?: { provider?: string; status?: string; page?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.provider) searchParams.set("provider", params.provider);
  if (params?.status) searchParams.set("status", params.status);
  searchParams.set("page", String(params?.page || 1));

  return useQuery({
    queryKey: ["admin", "jobs", params],
    queryFn: () => api.get(`/api/v1/admin/integrations/jobs?${searchParams.toString()}`),
    staleTime: 5_000,
    refetchInterval: 10_000,
  });
}

export function useReconciliationQueue(status = "pending_review") {
  return useQuery({
    queryKey: ["admin", "reconciliation", status],
    queryFn: () => api.get(`/api/v1/admin/integrations/reconciliation?status=${status}`),
    staleTime: 30_000,
  });
}
