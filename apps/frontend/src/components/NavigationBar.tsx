import { NavLink } from "react-router";
import { ModeToggle } from "@/components/";

export function NavigationBar() {
  return (
    <header className="stick top-0 z-40 border-b bg-background">
      <nav className="flex h-12 items-center justify-between px-6">
        <NavLink
          to="/connect"
          className="font-heading font-semibold tracking-tight text-lg text-foreground transition-colors hover:text-primary"
        >
          PersV
        </NavLink>
        <ModeToggle />
      </nav>
    </header>
  );
}
