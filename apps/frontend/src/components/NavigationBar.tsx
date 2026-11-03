import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { useAuth } from "@/context/AuthContext";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";
import { logout } from "@/services/auth";
import { authTokenStore } from "@/services/token";

export function NavigationBar() {
  const { isAuthenticated, setIsAuthenticated } = useAuth();
  const navigateNotice = useNavigateNotice();
  const [menuProfileOpen, setMenuProfileOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

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

  const handleLogout = async () => {
    setMenuProfileOpen(false); // close the menu immediately to avoid a flash of the menu after logout
    await logout(); // server clears the HttpOnly refresh cookie
    authTokenStore.expireSession();
    setIsAuthenticated(false);
    navigateNotice("/connect", { type: "info", message: "Logged out." });
  };

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
                  <button type="button" onClick={handleLogout}>
                    Log out
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
