import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useLocationNotice } from "@/hooks/useLocationNotice";
import type { NoticeData } from "@/types/notice";

export function Notice() {
  const navigate = useNavigate();
  const locationNotice = useLocationNotice();
  const [notice, _setNotice] = useState<NoticeData | null>(
    /*
     * Message passed via location.state: disconnect confirmation, missing-connection warning,
     * or a failed connection attempt. Falls back to null if none.
     */
    locationNotice ?? null,
  );

  useEffect(() => {
    if (locationNotice) {
      // Clear the notice message after displaying it once
      void navigate(location.pathname, { replace: true, state: {} });
    }
  }, []);

  return (
    notice && (
      <p id="notice" className={`${notice.type}-notice`}>
        {notice.message}
      </p>
    )
  );
}
