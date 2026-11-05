import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // How long data is considered fresh in milliseconds (5 minutes)
      gcTime: 30 * 60 * 1000, // How long data is retained in the cache in milliseconds (30 minutes)
      refetchOnWindowFocus: true, // Perform a data refetch to ensure the data is up-to-date when the window regains focus (tab switching)
    },
  },
});
