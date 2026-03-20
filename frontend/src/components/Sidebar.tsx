import { NavLink } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { JSX } from "react";

interface NavItem {
    to: string;
    label: string;
    icon: string;
}

const NAV_ITEMS: NavItem[] = [
    { to: "/dashboard", label: "Dashboard", icon: "📊" },
    { to: "/cadastro", label: "Cadastro", icon: "✏️" },
    { to: "/historico", label: "Histórico", icon: "📋" },
];

export default function Sidebar(): JSX.Element {
    const { logout } = useAuth();

    return (
        <aside
            style={{ backgroundColor: "#0f3460", minHeight: "100vh" }}
            className="w-56 flex flex-col py-6 px-3 shadow-lg"
        >
            <div className="mb-8 px-3">
                <span
                    style={{ color: "#22c55e" }}
                    className="text-xl font-bold tracking-wide"
                >
                    💰 Cofrinho
                </span>
            </div>

            <nav className="flex flex-col gap-1 flex-1">
                {NAV_ITEMS.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        style={({ isActive }) => ({
                            backgroundColor: isActive
                                ? "#22c55e"
                                : "transparent",
                            color: isActive ? "#0f3460" : "#f1f5f9",
                        })}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80"
                    >
                        <span>{item.icon}</span>
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <button
                onClick={logout}
                style={{ color: "#94a3b8" }}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium hover:text-white transition-colors mt-4"
            >
                <span>🚪</span>
                Logout
            </button>
        </aside>
    );
}
