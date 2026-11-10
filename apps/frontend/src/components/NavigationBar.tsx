import { Link } from "react-router";

export function NavigationBar() {
  return (
    <header>
      <nav>
        <Link to="/connect" rel="noopener noreferrer">
          <span>PersV</span>
        </Link>
      </nav>
    </header>
  );
}
