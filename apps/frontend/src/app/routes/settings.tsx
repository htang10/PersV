import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { NavigationBar, Setting, SettingAction, EmailChangeDialog } from "@/components";
import { useAuth } from "@/context/AuthContext";
import { authTokenStore } from "@/services/token";
import { getUserProfile, updateUserProfile } from "@/services/profile";
import { sendOTP, logoutAllSessions } from "@/services/auth";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";

export function meta() {
  return [{ title: "Settings" }];
}

export default function Settings() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const navigateNotice = useNavigateNotice();
  const { isAuthenticated, setIsAuthenticated } = useAuth();
  const [newEmail, setNewEmail] = useState<string | null>(null);
  const [emailSettingKey, setEmailSettingKey] = useState(0);
  const { isPending, isError, data, error } = useQuery({
    queryKey: ["profile"],
    queryFn: getUserProfile,
  });
  const currentDisplayName = data?.display_name ?? "";
  const currentEmail = data?.email ?? "";

  const handleBackToPreviousPage = async () => {
    await navigate(-1);
  };

  const handleDisplayNameUpdate = async (newDisplayName: string) => {
    await updateUserProfile({ new_display_name: newDisplayName });
  };

  const handleEmailChange = async (newEmail: string) => {
    await Promise.all([
      sendOTP({ email: newEmail, purpose: "email_change" }),
      sendOTP({ email: currentEmail, purpose: "email_change" }),
    ]);
    setNewEmail(newEmail);
  };

  const handleEmailChangeCancellation = () => {
    setNewEmail(null);
    setEmailSettingKey((k) => k + 1); // remount Setting so it drops the unverified email
  };

  const handleEmailChangeSuccess = async (newAccessToken: string) => {
    await queryClient.invalidateQueries({ queryKey: ["profile"] });
    authTokenStore.setToken(newAccessToken);
  };

  const handleLogoutAllDevices = useMutation({
    mutationFn: logoutAllSessions,
    onSuccess: () => {
      queryClient.clear(); // clear all cached queries to avoid showing stale data after logout
      authTokenStore.expireSession();
      setIsAuthenticated(false);
      navigateNotice("/connect", {
        type: "info",
        message: "Logged out of all devices.",
      });
    },
  });

  useEffect(() => {
    if (
      !isAuthenticated &&
      !handleLogoutAllDevices.isPending &&
      !handleLogoutAllDevices.isSuccess
    ) {
      navigateNotice("/connect", {
        type: "error",
        message: "You must be logged in to access settings.",
      });
    }
  }, [isAuthenticated, handleLogoutAllDevices.isPending, handleLogoutAllDevices.isSuccess]);

  if (!isAuthenticated) return null;

  if (isPending) {
    return <span>Loading...</span>;
  }

  if (isError) {
    return <span>Error: {error.message}</span>;
  }

  return (
    <>
      <NavigationBar />
      <button onClick={handleBackToPreviousPage}>
        <span>Back</span>
      </button>
      <div>
        <section>
          <h1>Profile</h1>

          <Setting
            label="Display Name"
            name="displayName"
            initial={currentDisplayName}
            onSave={handleDisplayNameUpdate}
          />

          <Setting
            key={`${currentEmail}-${emailSettingKey}`}
            label="Email"
            name="email"
            initial={currentEmail}
            onSave={handleEmailChange}
          />
          <EmailChangeDialog
            currentEmail={currentEmail}
            newEmail={newEmail as string}
            onClose={handleEmailChangeCancellation}
            onChanged={handleEmailChangeSuccess}
          />
        </section>

        <hr />

        <section>
          <h1>Security</h1>

          <SettingAction
            title="Log out of all devices"
            description="Log out of all active sessions across all devices, including this one."
            actionLabel="Log out all devices"
            onAction={() => handleLogoutAllDevices.mutate()}
            // When logout is being processed (pending), disable the button to prevent multiple clicks
            actionDisabled={handleLogoutAllDevices.isPending}
            // Replace the button label with a pending message when the action is in progress
            pendingLabel="Logging out..."
          />
          {/* 
          <SettingAction
            title="Delete account"
            description="Permanently delete your account and all associated data."
            actionLabel="Delete account"
            onAction={handleAccountDeletion}
            variant="danger"
          /> */}
        </section>
      </div>
    </>
  );
}
