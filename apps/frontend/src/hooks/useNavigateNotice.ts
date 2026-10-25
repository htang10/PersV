import { useNavigate } from "react-router";
import type { NoticeData } from "@/types/notice";

export function useNavigateNotice() {
  const navigate = useNavigate();

  return (path: string, notice: NoticeData) => {
    navigate(path, {
      state: { notice },
    });
  };
}
