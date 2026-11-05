import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { EmailChangeDialog, Setting, NavigationBar } from "@/components";
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

  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const [emailSettingKey, setEmailSettingKey] = useState(0);

  const { isPending, isError, data, error } = useQuery({
    queryKey: ["profile"],
    queryFn: getUserProfile,
  });

  const handleBackToPreviousPage = async () => {
    await navigate(-1);
  };

  const handleUpdateDisplayName = async (newDisplayName: string) => {
    await updateUserProfile({ new_display_name: newDisplayName });
  };

  const handleEmailChange = async (newEmail: string) => {
    await Promise.all([sendOTP(newEmail), sendOTP(currentEmail)]);
    setPendingEmail(newEmail);
  };

  const handleEmailChangeCancellation = () => {
    setPendingEmail(null);
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

  const currentDisplayName = data?.display_name ?? "";
  const currentEmail = data?.email ?? "";

  return (
    <>
      <NavigationBar />
      <button onClick={handleBackToPreviousPage}>
        <span>Back</span>
      </button>
      <div>
        <section>
          <h1>Profile</h1>
          <div>
            <img src="" alt="Avatar" />
          </div>
          <div>
            <Setting
              label="Display Name"
              name="displayName"
              initial={currentDisplayName}
              onSave={handleUpdateDisplayName}
            />
          </div>
          <div>
            <Setting
              key={`${currentEmail}-${emailSettingKey}`}
              label="Email"
              name="email"
              initial={currentEmail}
              onSave={handleEmailChange}
            />
            {pendingEmail && (
              <EmailChangeDialog
                currentEmail={currentEmail}
                newEmail={pendingEmail}
                onClose={handleEmailChangeCancellation}
                onChanged={handleEmailChangeSuccess}
              />
            )}
          </div>
        </section>
        <hr />
        <section>
          <h1>Security</h1>
          <div>
            <h2>Log out of all devices</h2>
            <p>Log out of all active sessions across all devices, including this one.</p>
            <button
              onClick={() => handleLogoutAllDevices.mutate()}
              disabled={handleLogoutAllDevices.isPending}
            >
              {handleLogoutAllDevices.isPending ? "Logging out..." : "Log out all devices"}
            </button>
          </div>
          <div>
            <h2>Delete account</h2>
            <p>Permanently delete your account and all associated data.</p>
            <button>Delete account</button>
          </div>
        </section>
      </div>
    </>
  );
}
