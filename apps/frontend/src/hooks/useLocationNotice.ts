import { useLocation } from "react-router";
import type { NoticeData } from "@/types/notice";

export function useLocationNotice() {
  const location = useLocation();
  return (location.state as { notice?: NoticeData } | undefined)?.notice ?? null;
}
