import { NavLink, Outlet } from "react-router-dom";

export function AppShell() {
  return (
    <div className="shell">
      <header className="top">
        <h1>Plant Health System</h1>
        <nav>
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/irrigation">Irrigation</NavLink>
          <NavLink to="/ml">ML</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
