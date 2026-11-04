import { useNavigate } from "react-router";
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { Setting } from "@/components";
import { getUserProfile, updateUserProfile } from "@/services/profile";
import { logoutAllSessions } from "@/services/auth";
import { NavigationBar } from "@/components";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";

export function meta() {
  return [{ title: "Settings" }];
}

export default function Settings() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const navigateNotice = useNavigateNotice();

  const handleBackToPreviousPage = async () => {
    await navigate(-1);
  };

  const handleUpdateDisplayName = async (newDisplayName: string) => {
    await updateUserProfile({ new_display_name: newDisplayName });
  };

  const handleLogoutAllDevices = useMutation({
    mutationFn: logoutAllSessions,
    onSuccess: () => {
      queryClient.clear(); // clear all cached queries to avoid showing stale data after logout
      navigateNotice("/connect", {
        type: "info",
        message: "Logged out of all devices.",
      });
    },
  });

  const { isPending, isError, data, error } = useQuery({
    queryKey: ["profile"],
    queryFn: getUserProfile,
  });

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
          <div>
            <img src="" alt="Avatar" />
          </div>
          <div>
            <Setting
              label="Display Name"
              name="displayName"
              initial={data?.display_name ?? ""}
              onSave={handleUpdateDisplayName}
            />
          </div>
          <div>
            {/* Add a setting for email. Email update will be implemented later */}
            <Setting label="Email" name="email" initial={data?.email ?? ""} onSave={() => void 0} />
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
