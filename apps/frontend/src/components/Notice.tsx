import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useLocationNotice } from "@/hooks/useLocationNotice";
import type { NoticeData } from "@/types/notice";

const NOTICE_STYLES = {
  info: { icon: Info, className: "" },
  success: { icon: CheckCircle2, className: "border-success/40 text-success" },
  warning: { icon: AlertTriangle, className: "border-warning/40 text-warning" },
  error: { icon: AlertCircle, className: "border-destructive/40 text-destructive" },
} satisfies Record<NoticeData["type"], { icon: typeof Info; className: string }>;

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

  if (!notice) return null;

  const { icon: Icon, className } = NOTICE_STYLES[notice.type];

  return (
    <Alert
      id="notice"
      role={notice.type === "error" || notice.type === "warning" ? "alert" : "status"}
      className={className}
    >
      <Icon className="size-4" />
      <AlertDescription className="text-current">{notice.message}</AlertDescription>
    </Alert>
  );
}
