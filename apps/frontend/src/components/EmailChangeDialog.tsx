// src/components/EmailChangeDialog.tsx
import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { updateEmail } from "@/services/auth";
import { errorMessage } from "@/errors/error-message";

type EmailChangeDialogProps = {
  currentEmail: string;
  newEmail: string;
  onClose: () => void;
  onChanged: (newAccessToken: string) => void;
};

export function EmailChangeDialog({
  currentEmail,
  newEmail,
  onClose,
  onChanged,
}: EmailChangeDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [currentEmailCode, setCurrentEmailCode] = useState("");
  const [newEmailCode, setNewEmailCode] = useState("");

  const verify = useMutation({
    mutationFn: async () =>
      await updateEmail({
        newEmail: newEmail,
        newEmailCode: newEmailCode,
        currentEmailCode: currentEmailCode,
      }),
    onSuccess: (data) => {
      onChanged(data.token);
      onClose();
    },
  });

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal(); // guard: Strict Mode runs effects twice in dev
  }, []);

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    verify.mutate();
  };

  return (
    <dialog ref={dialogRef} onClose={onClose}>
      <h2>Verify email change</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="current-email-code">Code sent to {currentEmail}</label>
          <input
            id="current-email-code"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            minLength={6}
            maxLength={6}
            value={currentEmailCode}
            onChange={(e) => setCurrentEmailCode(e.target.value.replace(/\D/g, ""))}
            required
          />
        </div>
        <div>
          <label htmlFor="new-email-code">Code sent to {newEmail}</label>
          <input
            id="new-email-code"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            minLength={6}
            maxLength={6}
            value={newEmailCode}
            onChange={(e) => setNewEmailCode(e.target.value.replace(/\D/g, ""))}
            required
          />
        </div>

        {verify.isError && (
          <span>
            {errorMessage(verify.error, {
              400: "One or both verification codes are incorrect or expired. Double-check the codes or restart the process to get new ones.",
              409: "This email is already linked to an account. Try signing in with it or use a different email address.",
            })}
          </span>
        )}

        <div>
          <button type="button" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" disabled={verify.isPending}>
            {verify.isPending ? "Verifying..." : "Verify email"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
