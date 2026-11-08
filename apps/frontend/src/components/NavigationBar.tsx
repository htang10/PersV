import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthContext";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";
import { logout } from "@/services/auth";
import { authTokenStore } from "@/services/token";
import { queryClient } from "@/lib/queryClient";

export function NavigationBar() {
  const { isAuthenticated, setIsAuthenticated } = useAuth();
  const navigateNotice = useNavigateNotice();
  const [menuProfileOpen, setMenuProfileOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const handleLogout = useMutation({
    mutationFn: async () => {
      setMenuProfileOpen(false); // close the menu immediately to avoid a flash of the menu after logout
      await logout(); // server clears the HttpOnly refresh cookie
    },
    onSuccess: () => {
      queryClient.clear(); // clear all cached queries to avoid showing stale data after logout
      authTokenStore.expireSession();
      setIsAuthenticated(false);
      navigateNotice("/connect", { type: "info", message: "Logged out." });
    },
  });

  useEffect(() => {
    if (!menuProfileOpen) return;

    const handleMouseDown = (e: MouseEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) setMenuProfileOpen(false);
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMenuProfileOpen(false);
    };

    document.addEventListener("mousedown", handleMouseDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [menuProfileOpen]);

  return (
    <header>
      <nav>
        <Link to="/connect" rel="noopener noreferrer">
          <img src="src/assets/logo.png" alt="Logo" width="100" height="100" />
        </Link>
      </nav>
      <div ref={menuRef}>
        {isAuthenticated ? (
          <>
            <button
              type="button"
              aria-expanded={menuProfileOpen}
              aria-controls="profile-menu"
              onClick={() => setMenuProfileOpen((toggle) => !toggle)}
            >
              Profile
            </button>
            {menuProfileOpen && (
              <ul id="profile-menu">
                <li>
                  <Link to="/settings" onClick={() => setMenuProfileOpen(false)}>
                    Settings
                  </Link>
                </li>
                <li>
                  <button onClick={() => handleLogout.mutate()} disabled={handleLogout.isPending}>
                    {handleLogout.isPending ? "Logging out..." : "Log out"}
                  </button>
                </li>
              </ul>
            )}
          </>
        ) : (
          <Link to="/login" target="_blank" rel="noopener noreferrer">
            Log in
          </Link>
        )}
      </div>
    </header>
  );
}
