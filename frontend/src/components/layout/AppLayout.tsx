import { Link, Outlet, useLocation } from "react-router-dom";

export default function AppLayout() {
  const location = useLocation();
  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>V2 Operations Console</h1>
        <nav>
          <Link className={location.pathname.startsWith("/sessions") ? "active" : ""} to="/sessions">
            Discussions
          </Link>
          <Link className={location.pathname.startsWith("/runtime-reviews") ? "active" : ""} to="/runtime-reviews">
            Runtime Reviews
          </Link>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
