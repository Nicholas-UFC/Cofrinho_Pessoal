import { useState, useRef, useEffect, type JSX } from "react";
import { useAutenticacao } from "../context/useAutenticacao";

const DJANGO_ADMIN_URL: string =
    import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface BarraTopoProps {
    onMenuClick: () => void;
}

export default function BarraTopo({
    onMenuClick,
}: BarraTopoProps): JSX.Element {
    const { username, isAdmin, logout } = useAutenticacao();
    const [open, setOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent): void {
            if (
                menuRef.current &&
                !menuRef.current.contains(event.target as Node)
            ) {
                setOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <header
            style={{
                backgroundColor: "#16213e",
                borderBottom: "1px solid #1e3a5f",
            }}
            className="flex items-center justify-between px-4 md:px-6 h-14 shadow"
        >
            {/* Botão hambúrguer — só aparece no mobile */}
            <button
                onClick={onMenuClick}
                style={{ color: "#22c55e" }}
                className="md:hidden text-2xl leading-none hover:opacity-70 transition-opacity"
                aria-label="Abrir menu"
            >
                ☰
            </button>

            {/* Logo — só aparece no desktop */}
            <div
                style={{ color: "#22c55e" }}
                className="hidden md:block text-lg font-semibold"
            >
                💰
            </div>

            <div className="relative" ref={menuRef}>
                <button
                    onClick={() => {
                        setOpen((prev) => !prev);
                    }}
                    style={{ color: "#f1f5f9" }}
                    className="flex items-center gap-2 text-sm font-medium hover:opacity-80 transition-opacity"
                >
                    <span style={{ color: "#94a3b8" }}>
                        Olá,{" "}
                        <span style={{ color: "#22c55e" }}>
                            {username ?? "usuário"}
                        </span>
                    </span>
                    <span style={{ color: "#94a3b8" }}>▾</span>
                </button>

                {open && (
                    <div
                        style={{
                            backgroundColor: "#16213e",
                            border: "1px solid #1e3a5f",
                        }}
                        className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg py-1 z-50"
                    >
                        {isAdmin && (
                            <a
                                href={`${DJANGO_ADMIN_URL}/admin/`}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: "#f1f5f9" }}
                                className="flex items-center gap-2 px-4 py-2 text-sm hover:opacity-70 transition-opacity"
                                onClick={() => {
                                    setOpen(false);
                                }}
                            >
                                <span>⚙️</span>
                                Painel Admin
                            </a>
                        )}
                        <button
                            onClick={() => {
                                setOpen(false);
                                void logout();
                            }}
                            style={{ color: "#f1f5f9" }}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:opacity-70 transition-opacity"
                        >
                            <span>🚪</span>
                            Logout
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}
