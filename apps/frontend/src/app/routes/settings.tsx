import { useNavigate } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Setting } from "@/components";
import { getUserProfile, updateUserProfile } from "@/services/profile";
import { logout, logoutAllSessions, updateEmail } from "@/services/auth";
import { NavigationBar } from "@/components";

export function meta() {
  return [{ title: "Settings" }];
}

export default function Settings() {
  const navigate = useNavigate();

  const backToPreviousPage = async () => {
    await navigate(-1);
  };

  const updateDisplayName = async (newDisplayName: string) => {
    await updateUserProfile({ new_display_name: newDisplayName });
  };

  const updateEmail = async (newEmail: string) => {};

  const { isPending, isError, data, error } = useQuery({
    queryKey: ["profile"],
    queryFn: getUserProfile,
    staleTime: 5 * 60 * 1000, // How long data is considered fresh in milliseconds (5 minutes)
    gcTime: 30 * 60 * 1000, // How long data is retained in the cache in milliseconds (30 minutes)
    refetchOnWindowFocus: true, // Perform a data refetch to ensure the data is up-to-date when the window regains focus (tab switching)
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
      <button onClick={backToPreviousPage}>
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
              onSave={updateDisplayName}
            />
          </div>
          <div>
            <Setting label="Email" name="email" initial={data?.email ?? ""} onSave={updateEmail} />
          </div>
        </section>
        <hr />
        <section>
          <h1>Security</h1>
          <div>
            <h2>Log out of all devices</h2>
            <p>Log out of all active sessions across all devices, including this one.</p>
            <button>Log out of all devices</button>
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
