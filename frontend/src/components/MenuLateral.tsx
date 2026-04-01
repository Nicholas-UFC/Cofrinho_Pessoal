import { NavLink } from "react-router-dom";
import { useAutenticacao } from "../context/useAutenticacao";
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

interface MenuLateralProps {
    open: boolean;
    onClose: () => void;
}

export default function MenuLateral({
    open,
    onClose,
}: MenuLateralProps): JSX.Element {
    const { logout } = useAutenticacao();

    return (
        <aside
            style={{ backgroundColor: "#0f3460", minHeight: "100vh" }}
            className={[
                "w-56 flex flex-col py-6 px-3 shadow-lg flex-shrink-0",
                // Desktop: sempre visível
                "md:relative md:translate-x-0 md:flex",
                // Mobile: drawer fixo que desliza
                "fixed inset-y-0 left-0 z-30 transition-transform duration-300",
                open ? "translate-x-0" : "-translate-x-full md:translate-x-0",
            ].join(" ")}
            aria-label="Menu de navegação"
        >
            <div className="mb-8 px-3 flex items-center justify-between">
                <span
                    style={{ color: "#22c55e" }}
                    className="text-xl font-bold tracking-wide"
                >
                    💰 Cofrinho
                </span>
                {/* Botão fechar — só aparece no mobile */}
                <button
                    onClick={onClose}
                    style={{ color: "#94a3b8" }}
                    className="md:hidden text-lg hover:opacity-70"
                    aria-label="Fechar menu"
                >
                    ✕
                </button>
            </div>

            <nav className="flex flex-col gap-1 flex-1">
                {NAV_ITEMS.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        onClick={onClose}
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
                onClick={() => {
                    onClose();
                    void logout();
                }}
                style={{ color: "#94a3b8" }}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium hover:text-white transition-colors mt-4"
            >
                <span>🚪</span>
                Logout
            </button>
        </aside>
    );
}
