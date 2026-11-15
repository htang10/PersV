import { useEffect } from "react";
import { errorMessage } from "@/errors/error-message";
import { useNavigateNotice } from "./useNavigateNotice";
import { useQuery } from "@tanstack/react-query";
import { checkConnStatus } from "@/services/connection";

export const CONNECTION_STATUS_KEY = ["connection-status"];

export function useConnectionGuard() {
  const navigateNotice = useNavigateNotice();

  const status = useQuery({
    queryKey: CONNECTION_STATUS_KEY,
    queryFn: checkConnStatus,
    staleTime: 0,
    gcTime: 0,
    retry: false,
  });

  useEffect(() => {
    // Only redirect on error if no data was ever returned, because focus refetching can fail briefly
    if (status.isError && !status.data) {
      navigateNotice("/connect", { type: "error", message: errorMessage(status.error) });
    } else if (status.data && !status.data.connected) {
      navigateNotice("/connect", {
        type: "error",
        message: "Not connected to any database yet or the session expired. Please connect first.",
      });
    }
  }, [status.isError, status.error, status.data]);

  return status;
}
